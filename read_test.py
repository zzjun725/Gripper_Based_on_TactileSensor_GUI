import sys
from utils import utils
import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
import pandas as pd
import re
from queue import Queue
from copy import deepcopy
import time

# 全局变量
sensor_num = 6
i = 0
default_length = 300

# 初始化qlist（从串口读入数据）和sensordata（储存发送给plot的数据）
# 使用队列来读取 线程安全
info_qlist = [Queue(maxsize=0) for _ in range(sensor_num)]
sensordata_matrix = np.array([np.zeros(default_length) for _ in range(sensor_num)], dtype=np.float64)
sensordata_save = pd.DataFrame(columns=range(sensor_num))
sensordata_deltasave = pd.DataFrame(columns=range(sensor_num))
sensor_q = Queue(maxsize=sensor_num)  # 暂存 防止丢包
sensordata_per = [0 for _ in range(sensor_num)]  # 暂存 防止丢包
sensordata_save = sensordata_save.append([sensordata_per], ignore_index=True)
sensordata_deltasave = sensordata_deltasave.append([sensordata_per], ignore_index=True)

# test1 = sensordata_plot[1]
# pg.plot(test1)

mSerial = serial.Serial(
    port='COM5',
    baudrate=115200,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)


# 串口通讯函数
def Serial():
    global sensordata_save
    data_num = 0
    while True:
        n = mSerial.inWaiting()
        if n:
            data_raw = mSerial.readline()
            data_str = bytes.decode(data_raw)
            # print('com5', data_str)
            # 若读到终止符则清空队列
            if data_str == 'e':
                sensor_q.empty()
            else:
                data_fliter = re.sub("\D", "", data_str)
                if len(data_fliter) > 2:
                    data_num = float(data_fliter) / 100
                    sensor_q.put(data_num)
            # 若接收到完整的n个数据则开始输送数据
            if sensor_q.qsize() == sensor_num:
                for ind in range(sensor_num):
                    sensordata_per[ind] = sensor_q.get()
                    info_qlist[ind].put(deepcopy(sensordata_per[ind]))
                sensordata_save = sensordata_save.append([sensordata_per], ignore_index=True)


# 绘制图像
def plotData():
    global i, sensordata_matrix
    for sensor_index in range(sensor_num):
        data = sensordata_matrix[sensor_index]
        if i < default_length:
            data[i] = info_qlist[sensor_index].get()
            i = i + 1
        else:
            data[:-1] = data[1:]
            data[i - 1] = info_qlist[sensor_index].get()
        sensorplot_list[sensor_index].setData(data)
        # curve_tmp.setData(data)


def save_data():
    # 输出数据到excel
    sensordata_save.to_csv('sensor_data')


# 测试 直接打印串口传输过来的数据
def test():
    global sensordata_save, sensordata_deltasave
    while True:
        # 串口读入byte类型的数据，打印出来是b'5.12\r\n'，需要译码
        data_raw = mSerial.readline()
        data_str = bytes.decode(data_raw)
        # print('com5', data_str)
        if len(data_str) == 3:
            # print('clear')
            sensor_q.queue.clear()
            # print(sensor_q.qsize())
        else:
            data_fliter = re.sub("\D", "", data_str)
            if len(data_fliter) > 2:
                data_num = float(data_fliter) / 100
                if data_num < 6 :
                    sensor_q.put(data_num)
                    # print(sensor_q.qsize())
        if sensor_q.qsize() == sensor_num:
            for ind in range(sensor_num):
                sensordata_per[ind] = sensor_q.get()
                info_qlist[ind].put(deepcopy(sensordata_per[ind]))
            #
            old_per = sensordata_save[-1:].to_numpy()
            delta_per = utils.get_item_delta(sensordata_per, old_per)
            print(delta_per)
            sensordata_deltasave = sensordata_deltasave.append([delta_per], ignore_index=True)
            #
            sensordata_save = sensordata_save.append([sensordata_per], ignore_index=True)
            print(sensordata_per)
            # print(sensordata_save)


test()
app = pg.mkQApp()  # 建立app
win = pg.GraphicsWindow()  # 建立窗口
win.setWindowTitle(u'test')
win.resize(1400, 900)  # 小窗口大小
sensorgraph_list = list()
sensorplot_list = list()
data = np.zeros(default_length)
for index in range(sensor_num):
    # 三个图则换行
    if index > 2 and index % 3 == 0:
        win.nextRow()
    sensorgraph_list.append(win.addPlot())  # 把图p加入到窗口中
    tmp = sensorgraph_list[index]
    tmp.showGrid(x=True, y=True)  # 把X和Y的表格打开
    tmp.setRange(xRange=[0, default_length], yRange=[0, 5.5], padding=0)
    tmp.setLabel(axis='left', text='y')
    tmp.setLabel(axis='bottom', text='x')
    tmp.setTitle('传感器{}数据'.format(index))  # 表格的名字
    sensorplot_list.append(sensorgraph_list[index].plot())
    curve_tmp = sensorplot_list[index]  # 绘制一个图形
    curve_tmp.setData(data)

# 开一个线程用来读取串口
th_Readserial = threading.Thread(target=Serial)
th_Readserial.start()
# th_Displaysensor = threading.Thread(target=display)
# th_Displaysensor.start()
# 开一个计时器用来绘图
timer = pg.QtCore.QTimer()
timer.timeout.connect(plotData)  # 定时刷新数据显示
timer.start(1)  # 调用频率（ms）
sys.exit(app.exec_())
print('start')
