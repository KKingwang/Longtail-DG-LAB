import time
import cv2
import numpy as np

cv2.destroyAllWindows()  # 确保所有窗口被关闭

# 打开 OBS 虚拟摄像头
cap = cv2.VideoCapture(1)  # 通常为摄像头 0，如果不对请尝试 1 或 2

if not cap.isOpened():
    print("无法打开虚拟摄像头")
    exit()

# 读取一帧画面作为截图
ret, frame = cap.read()
if not ret:
    print("无法读取摄像头画面")
    cap.release()
    exit()

# 释放摄像头资源，因为我们只需要这一张截图
cap.release()
time.sleep(1)  # 等待1秒，确保摄像头资源完全释放

# 全局变量用于存储区域坐标
hp_region_top_left = None
hp_region_bottom_right = None
drawing = False  # 表示是否正在绘制矩形


# 鼠标回调函数
def draw_rectangle(event, x, y, flags, param):
    global hp_region_top_left, hp_region_bottom_right, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        # 左键按下，开始绘制矩形，记录左上角坐标
        drawing = True
        hp_region_top_left = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        # 鼠标移动时，更新右下角坐标
        if drawing:
            hp_region_bottom_right = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        # 左键释放，结束绘制，记录最终的右下角坐标
        drawing = False
        hp_region_bottom_right = (x, y)


# 创建一个窗口并绑定鼠标回调
cv2.namedWindow('Screenshot')
cv2.setMouseCallback('Screenshot', draw_rectangle)

while True:
    # 创建一份副本用于显示，不修改原始截图
    display_frame = frame.copy()

    # 如果已经选择了区域，则绘制矩形框
    if hp_region_top_left and hp_region_bottom_right:
        cv2.rectangle(display_frame, hp_region_top_left, hp_region_bottom_right, (0, 0, 255), 2)

    # 显示当前截图
    cv2.imshow('Screenshot', display_frame)

    # 持续检测，直到窗口被手动关闭
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# 关闭窗口
cv2.destroyAllWindows()

# 输出选定区域的坐标
if hp_region_top_left and hp_region_bottom_right:
    print(f"hp_region_top_left = {hp_region_top_left}")
    print(f"hp_region_bottom_right = {hp_region_bottom_right}")

    # 计算灰度平均值
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x1, y1 = hp_region_top_left
    x2, y2 = hp_region_bottom_right
    selected_region = gray_frame[y1:y2, x1:x2]

    if selected_region.size > 0:
        mean_gray_value = np.mean(selected_region)
        print(f"average_greyscale = {mean_gray_value:.0f}")
    else:
        print("选定区域无效或为空")
else:
    print("选定区域无效或为空")
