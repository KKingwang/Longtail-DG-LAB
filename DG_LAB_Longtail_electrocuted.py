import asyncio
import socket
import struct
from bleak import BleakClient, BleakScanner

strength_CharacteristicId = "955a1504-0fe2-f5aa-a094-84b8d4f3e8ad"
A_CharacteristicId = "955a1506-0fe2-f5aa-a094-84b8d4f3e8ad"
B_CharacteristicId = "955a1505-0fe2-f5aa-a094-84b8d4f3e8ad"


class DgLab:
    def __init__(self, target_name):
        self.target_name = target_name
        self.bt_address = ""
        self.client = None
        self.pulseFrequency = None
        self.ab_power_max = None

    async def scan_devices(self):
        print("Start scanning:")
        devices = await BleakScanner.discover()
        for device in devices:
            print(device)
            if device.name == self.target_name:
                print("Device found")
                self.bt_address = device.address
                break

    async def connect_to_device(self):
        if not self.bt_address:
            print("Device not found. Make sure it is nearby and turned on.")
            return

        self.client = BleakClient(self.bt_address)
        await self.client.connect()
        if not self.client.is_connected:
            print("Failed to connect.")
            return
        print(f"Connected to {self.bt_address}")
        print("------------------------------------")

    async def send_data(self, channel, wave_scanner_a, wave_scanner_b, power_ab):
        if not self.client or not self.client.is_connected:
            print("Client is not connected.")
            return

        if power_ab[0] > self.ab_power_max or power_ab[1] > self.ab_power_max:
            print(f"无效值。a_power 和 b_power 值都应小于且不等于最大值： {self.ab_power_max + 1} 。")
            pass
        else:
            for timer in range(1):
                ab_power_new = tuple(x * 10 for x in power_ab)
                print(f"AB端口强度分别是：{ab_power_new}")
                combined_power = (ab_power_new[0] << 11) | ab_power_new[1]
                # 构建24位数据：23-22位为0（保留），21-11位为B通道强度，10-0位为A通道强度
                power_to_write = combined_power.to_bytes(3, byteorder='little')  # 将24位值转换为3字节小端格式
                await self.client.write_gatt_char(strength_CharacteristicId, power_to_write)
                if channel == "A":
                    print(f"A端口已发送：{wave_scanner_a}")
                    print("------------------------------------")
                    await self.client.write_gatt_char(A_CharacteristicId, wave_scanner_a)
                elif channel == "B":
                    print(f"B端口已发送：{wave_scanner_b}")
                    print("------------------------------------")
                    await self.client.write_gatt_char(B_CharacteristicId, wave_scanner_b)
                elif channel == "ALL":
                    print(f"AB端口已发送：{wave_scanner_a}, {wave_scanner_b}")
                    print("------------------------------------")
                    await self.client.write_gatt_char(A_CharacteristicId, wave_scanner_a)
                    await self.client.write_gatt_char(B_CharacteristicId, wave_scanner_b)
                else:
                    print("Invalid channel. Please select either A or B.")
                    pass

    async def run(self):
        await self.scan_devices()
        await self.connect_to_device()


def send_pulse_params(x, y, z):
    # 确保x, y, z的范围合法
    if not (0 <= x <= 31) or not (0 <= y <= 1023) or not (0 <= z <= 31):
        raise ValueError("参数超出范围")
    # 构建数据包（小端格式）
    # 数据包格式: X (5 bits), Y (10 bits), Z (5 bits)
    packed_data = (z << 15) | (y << 5) | x
    data_bytes = packed_data.to_bytes(3, byteorder='little')
    return data_bytes


def start_udp():
    # 启动网络功能（UDP）
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", 7788))
    return udp_socket


def main():
    # I just get kicked by it 2024.08.27
    # I just get kicked by it again 2024.09.01
    # BE VERY CAREFUL CHANGING THIS power !!!
    # longtail = DgLab("D-LAB ESTIM01")
    # asyncio.run(longtail.run())
    udp_socket = start_udp()
    running = True
    while running:
        data, addr = udp_socket.recvfrom(1024)  # 1024 是缓冲区大小，可以根据需要调整
        if len(data) < 40:
            data = data.ljust(40, b'\x00')  # 用零字节填充
        elif len(data) > 40:
            data = data[:40]  # 截断到40字节
        message_length = struct.unpack('!I', data[:4])[0]  # 解包字符串长度（第一个无符号整数）
        format_string = f'!I{message_length}s3i3i2i'  # 根据字符串长度，构建解包格式
        unpacked_data = struct.unpack(format_string, data)
        channel = unpacked_data[1].decode()
        wave_data_tuple_a = unpacked_data[2:5]
        wave_data_tuple_b = unpacked_data[5:8]
        power_data_tuple_ab = unpacked_data[8:10]
        # print(f"Received message: {message}")
        # print(f"Received tuple A: {wave_data_tuple_a}")
        # print(f"Received tuple B: {wave_data_tuple_b}")
        # print(f"Received tuple AB: {power_data_tuple_ab}")
        if channel == "on_a":
            print("开启通道 A")
            print(f"A 接收的频率元组值为: {wave_data_tuple_a}")
            asyncio.run(
                longtail.send_data("A", send_pulse_params(*wave_data_tuple_a), send_pulse_params(*wave_data_tuple_b),
                                   power_data_tuple_ab))
        elif channel == "on_b":
            print("开启通道 B")
            print(f"B 接收的频率元组值为: {wave_data_tuple_b}")
            asyncio.run(
                longtail.send_data("B", send_pulse_params(*wave_data_tuple_a), send_pulse_params(*wave_data_tuple_b),
                                   power_data_tuple_ab))
        elif channel == "onab":
            print("开启通道 AB")
            print(f"AB 接收的频率元组值为: {wave_data_tuple_a}, {wave_data_tuple_b}")
            asyncio.run(
                longtail.send_data("ALL", send_pulse_params(*wave_data_tuple_a), send_pulse_params(*wave_data_tuple_b),
                                   power_data_tuple_ab))
        elif channel == "off_":
            running = False
        else:
            print("Invalid command.")


if __name__ == "__main__":
    # 创建实例
    longtail = DgLab("D-LAB ESTIM01")
    asyncio.run(longtail.run())
    # AB通道最大强度
    longtail.ab_power_max = 20
    main()
