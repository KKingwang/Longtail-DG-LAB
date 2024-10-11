import socket
import struct
import time


def send_udp_message(channel, wave_data_tuple_a, wave_data_tuple_b, power_data_tuple_ab):
    # 创建 UDP 套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 获取字符串的长度
    channel_length = len(channel)

    # '!I{}siii' 表示网络字节序下，一个无符号整数（表示字符串长度），一个可变长度的字符串，和三个整数
    # format_string = f'!I{message_length}siii'
    format_string = f'!I{channel_length}s{len(wave_data_tuple_a)}i{len(wave_data_tuple_b)}i{len(power_data_tuple_ab)}i'

    # 打包数据，将字符串长度、字符串内容和元组一起打包
    packed_data = struct.pack(format_string, channel_length, channel.encode(), *wave_data_tuple_a, *wave_data_tuple_b,
                              *power_data_tuple_ab)

    # 发送数据
    sock.sendto(packed_data, ("127.0.0.1", 7788))

    # 关闭套接字
    sock.close()


def create_wave_sequence(channel_mode, sequence_a, sequence_b, power_ab):
    max_length = max(len(sequence_a), len(sequence_b))
    for i in range(max_length):
        wave_a = sequence_a[i] if i < len(sequence_a) else (0, 0, 0)
        wave_b = sequence_b[i] if i < len(sequence_b) else (0, 0, 0)
        send_udp_message(channel_mode, wave_a, wave_b, power_ab)
        print(f"发送波形序列: {wave_a}, {wave_b}, {power_ab}")
        time.sleep(0.1)  # 每0.1秒发送一次


if __name__ == '__main__':
    # 示例使用
    channel_modes = "onab"  # 输入模式,只能四个字符（on_a：开启a通道, on_b：开启b通道, onab：开启ab通达, off_：关闭）

    # 强度等级，禁止留空（a通道,b通道）
    power_ab_value = (15, 15)

    # 频谱以列表形式写出，上线分别为31，1023，31，具体信息看 v2 文档自行研究，列表禁止为 None，否则会报错，可以为（0，0，0）。
    wave_sequences_a = [
        (5, 135, 20), (5, 125, 20), (5, 115, 20), (5, 105, 20),
        (5, 95, 20), (4, 86, 20), (4, 76, 20), (4, 66, 20),
        (3, 57, 20), (3, 47, 20), (3, 37, 20), (2, 28, 20),
        (2, 18, 20), (1, 14, 20), (1, 9, 20)
    ]
    wave_sequences_b = [
        (5, 95, 20), (5, 95, 20), (5, 95, 20), (5, 95, 20), (5, 95, 20),
        (1, 9, 20), (1, 9), (1, 9, 20), (1, 9, 20), (1, 9, 20)
    ]
    """
    实例波形
    
    波形1 = [
        (5, 95, 20), (5, 95, 20), (5, 95, 20), (5, 95, 20), (5, 95, 20),
        (1, 9, 20), (1, 9), (1, 9, 20), (1, 9, 20), (1, 9, 20)
    ]
    
    波形2 = [
        (1, 9, 4), (1, 9, 8), (1, 9, 12), (1, 9, 16), (1, 9, 18), 
        (1, 9, 19), (1, 9, 20), (1, 9, 0), (1, 9, 0), (1, 9, 0)
    ]
    
    波形3 = [
        (5, 135, 20), (5, 125, 20), (5, 115, 20), (5, 105, 20),
        (5, 95, 20), (4, 86, 20), (4, 76, 20), (4, 66, 20),
        (3, 57, 20), (3, 47, 20), (3, 37, 20), (2, 28, 20),
        (2, 18, 20), (1, 14, 20), (1, 9, 20)
    ]
    
    """

    # 生成波形序列
    create_wave_sequence(channel_modes, wave_sequences_a, wave_sequences_b, power_ab_value)
