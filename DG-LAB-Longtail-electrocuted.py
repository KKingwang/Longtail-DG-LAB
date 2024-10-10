import asyncio
import socket
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
        self.a_wave = []
        self.b_wave = []
        self.pulseFrequency=None

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

    async def send_data(self,channel):
        if not self.client or not self.client.is_connected:
            print("Client is not connected.")
            return

        if self.a_value > 15 and self.b_value > 15:
            print("Invalid values. Both A and B values should be less than 16.")
            pass
        else:
            for timer in range(5):
                a_value_new = self.a_value * 7
                b_value_new = self.b_value * 7
                combined_value = (b_value_new << 11) | a_value_new  # 构建24位数据：23-22位为0（保留），21-11位为B通道强度，10-0位为A通道强度
                value_to_write = combined_value.to_bytes(3, byteorder='little')  # 将24位值转换为3字节小端格式
                await self.client.write_gatt_char(strength_CharacteristicId, value_to_write)
                if channel == "A":
                    for waveScanner in self.a_wave:
                        print("Writing wave: " + waveScanner)
                        await self.client.write_gatt_char(A_CharacteristicId, bytes.fromhex(waveScanner))
                        await asyncio.sleep(self.pulseFrequency)
                elif channel == "B":
                    for waveScanner in self.b_wave:
                        print("Writing wave: " + waveScanner)
                        await self.client.write_gatt_char(B_CharacteristicId, bytes.fromhex(waveScanner))
                        await asyncio.sleep(self.pulseFrequency)
                else:
                    print("Invalid channel. Please select either A or B.")
                    pass
    async def run(self):
        await self.scan_devices()
        await self.connect_to_device()


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
        recv_data, sender_info = udp_socket.recvfrom(1024)
        print("{}发送{}".format(sender_info, recv_data))
        recv_data_str = recv_data.decode("utf-8")
        try:
            print(f"启动通道：{recv_data_str[-1]}")
        except Exception as ret:
            print("error:", ret)

        if recv_data_str == "on_a":
            asyncio.run(longtail.send_data("A"))
        elif recv_data_str == "on_b":
            asyncio.run(longtail.send_data("B"))
        elif recv_data_str == "on_all":
            asyncio.run(longtail.send_data("A"))
            asyncio.run(longtail.send_data("B"))
        elif recv_data_str == "off":
            running = False
        else:
            print("Invalid command.")


if __name__ == "__main__":
    # 创建实例
    longtail = DgLab("D-LAB ESTIM01")
    asyncio.run(longtail.run())
    # 脉冲间隔延迟（郊狼的程序把每一秒分割成1000毫秒，在每个毫秒内都可以产生一次脉冲）
    longtail.pulseFrequency = 0.1
    # 脉冲波形（列表形式）
    longtail.a_wave = ['210100','210102','210104','210106','210108','21010A','21010A','21010A','000000','000000','000000','000000',]
    longtail.b_wave = ['21010A','21010A','21010A','21010A','21010A',]
    # 通道强度（大于15无效）
    longtail.a_value = 7
    longtail.b_value = 7
    main()
