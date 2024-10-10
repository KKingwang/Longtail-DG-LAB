import cv2

from wave_generation import main

# 打开 OBS 虚拟摄像头
cap = cv2.VideoCapture(1)  # 通常为摄像头 0，如果不对请尝试 1 或 2

if not cap.isOpened():
    print("无法打开虚拟摄像头")
    exit()

# 初始化血量检测的基准值
prev_hp = None

# 血量区域的坐标（根据实际情况调整）
# 左上角坐标 (x, y)
# 右下角坐标 (x, y)
# 平均灰度值
hp_region_top_left = (639, 373)
hp_region_bottom_right = (1908, 1058)
average_greyscale = 255

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break

        # 提取血量区域
        hp_region = frame[hp_region_top_left[1]:hp_region_bottom_right[1],
                    hp_region_top_left[0]:hp_region_bottom_right[0]]

        # 转换为灰度图像进行处理
        gray = cv2.cvtColor(hp_region, cv2.COLOR_BGR2GRAY)

        # 简单的二值化处理
        _, threshold = cv2.threshold(gray, (average_greyscale - 1), 255, cv2.THRESH_BINARY)

        # 计算血量条区域的白色像素数量（假设白色像素代表血量）
        current_hp = cv2.countNonZero(threshold)

        # 初始化基准值
        if prev_hp is None:
            prev_hp = current_hp

        # 判断血量是否变化（只会在血量减少时运行函数）
        # 没有加判断，可能会出奇奇怪怪的bug，比如打开背包之类的也会触发，后续做优化 -- 2024.10.11
        if current_hp < prev_hp and abs(current_hp - prev_hp) > 50:  # 50 是一个阈值，可以根据需要调整
            print("血量减少！")
            main()

        # 更新基准值
        prev_hp = current_hp

        # 在画面上绘制红色矩形框以显示血量区域
        cv2.rectangle(frame, hp_region_top_left, hp_region_bottom_right, (0, 0, 255), 2)  # 红色框，2像素宽

        # 显示当前画面
        cv2.imshow('OBS Frame', frame)

        # 显示二值化后的图像
        cv2.imshow('Threshold Image', threshold)

        # 持续检测，直到窗口被手动关闭
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    # 当按下 Ctrl+C 时，中断循环并关闭
    print("检测已停止")

finally:
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
