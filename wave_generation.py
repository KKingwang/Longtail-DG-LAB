import random
from udp_update import create_wave_sequence


def frequency_update(frequency, z):
    x = round(((frequency / 1000) ** 0.5) * 15)
    y = round(frequency - x)
    return x, y, z


def for_frequency_update(frequency_list, z, power):
    for frequency in frequency_list:
        a = frequency_update(frequency, z)
        print(a)
        create_wave_sequence("on_a", [a], [(0, 0, 0)], power)


def main():
    random_numbers_ = [random.randint(1, 200) for _ in range(1)]

    # 脉冲宽度 z
    frequency_z_ = 31
    power_ = (16, 17)
    for_frequency_update(random_numbers_, frequency_z_, power_)


if __name__ == '__main__':
    # 示例使用
    """
    随机列表和固定列表只能选一个，使用时请注释掉另一个
    输入数字为频率，计算公式是 v2 文档中的公式，具体信息请自行研究
    """
    # 频率固定列表
    # frequency_list_ = [23, 20, 15, 10, 5, 2, 111, 170, 186, 106, 119, 101]
    # 频率随机列表，范围 1-600，数量 100
    random_numbers = [random.randint(1, 200) for _ in range(10)]

    # 强度固定列表
    # power_ = (16, 17)
    # 强度随机列表，A 通道范围 16-20，B 通道范围 16-20
    random_power = (random.randint(16, 20), random.randint(16, 20))

    # 脉冲宽度 z
    frequency_z = 31
    for_frequency_update(random_numbers, frequency_z, random_power)
