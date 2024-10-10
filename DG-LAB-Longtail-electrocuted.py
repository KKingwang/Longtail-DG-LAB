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
        self.a_value = None
        self.b_value = None
        self.pulseFrequency = None
        self.ab_value_max = None

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

    async def send_data(self, channel, wave_scanner_a, wave_scanner_b):
        if not self.client or not self.client.is_connected:
            print("Client is not connected.")
            return

        if self.a_value > self.ab_value_max or self.b_value > self.ab_value_max:
            print(f"无效值。a_value 和 b_value 值都应小于且不等于最大值： {self.ab_value_max + 1} 。")
            pass
        else:
            for timer in range(1):
                a_value_new = self.a_value * 7
                b_value_new = self.b_value * 7
                combined_value = (b_value_new << 11) | a_value_new  # 构建24位数据：23-22位为0（保留），21-11位为B通道强度，10-0位为A通道强度
                value_to_write = combined_value.to_bytes(3, byteorder='little')  # 将24位值转换为3字节小端格式
                await self.client.write_gatt_char(strength_CharacteristicId, value_to_write)
                if channel == "A":
                    print(f"A端口已发送：{wave_scanner_a}")
                    await self.client.write_gatt_char(A_CharacteristicId, wave_scanner_a)
                elif channel == "B":
                    print(f"B端口已发送：{wave_scanner_b}")
                    await self.client.write_gatt_char(B_CharacteristicId, wave_scanner_b)
                elif channel == "ALL":
                    print(f"AB端口已发送：{wave_scanner_a}, {wave_scanner_b}")
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
    # BE VERY CAREFUL CHANGING THIS VALUE !!!
    # longtail = DgLab("D-LAB ESTIM01")
    # asyncio.run(longtail.run())
    udp_socket = start_udp()
    running = True
    while running:
        data, addr = udp_socket.recvfrom(1024)  # 1024 是缓冲区大小，可以根据需要调整
        message_length = struct.unpack('!I', data[:4])[0]  # 解包字符串长度（第一个无符号整数）
        format_string = f'!I{message_length}s3i3i'  # 根据字符串长度，构建解包格式
        unpacked_data = struct.unpack(format_string, data)
        message = unpacked_data[1].decode()
        data_tuple_a = unpacked_data[2:5]
        data_tuple_b = unpacked_data[5:8]
        # print(f"Received message: {message}")
        # print(f"Received tuple A: {data_tuple_a}")
        # print(f"Received tuple B: {data_tuple_b}")
        if message == "on_a":
            print("on_a")
            print(f"Received tuple: {data_tuple_a}")
            send_pulse_params(*data_tuple_a)
            asyncio.run(longtail.send_data("A", send_pulse_params(*data_tuple_a), send_pulse_params(*data_tuple_b)))
        elif message == "on_b":
            print("on_b")
            print(f"Received tuple: {data_tuple_b}")
            send_pulse_params(*data_tuple_b)
            asyncio.run(longtail.send_data("B", send_pulse_params(*data_tuple_a), send_pulse_params(*data_tuple_b)))
        elif message == "on_all":
            print("on_all")
            print(f"Received tuple: {data_tuple_a}")
            print(f"Received tuple: {data_tuple_b}")
            asyncio.run(longtail.send_data("ALL", send_pulse_params(*data_tuple_a), send_pulse_params(*data_tuple_b)))
        elif message == "off":
            running = False
        else:
            print("Invalid command.")


if __name__ == "__main__":
    # 创建实例
    longtail = DgLab("D-LAB ESTIM01")
    asyncio.run(longtail.run())
    # AB通道最大强度
    longtail.ab_value_max = 15
    # 通道强度（高于最大时无效）
    longtail.a_value = 15
    longtail.b_value = 18
    main()
