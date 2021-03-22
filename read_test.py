import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
import pandas as pd
import re
from queue import Queue
import time

# 全局变量
sensor_num = 2
i = 0
default_length = 300

# 初始化qlist（从串口读入数据）和sensordata（储存发送给plot的数据）
info_qlist = [Queue(maxsize=0) for _ in range(sensor_num)]
sensordata_matrix = np.array([np.zeros(default_length) for _ in range(sensor_num)], dtype=np.float64)
sensordata_save = pd.DataFrame(columns=range(sensor_num))
sensordata_save=sensordata_save.append([[0, 0]], ignore_index=True)
sensor_q = Queue(maxsize=sensor_num)

# test1 = sensordata_matrix[1]
# pg.plot(test1)

mSerial = serial.Serial(
    port='COM5',
    baudrate=115200,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)


def Serial():
    global sensordata_save
    data_num = 0
    while True:
        n = mSerial.inWaiting()
        if n:
            data_raw = mSerial.readline()
            data_str = bytes.decode(data_raw)
            if len(data_str) > 2:
                data_num = float(re.sub("\D", "", data_str))/100
            info_qlist[0].put(data_num)
            info_qlist[1].put(5)
            # info_qlist[2].put(5)
            # if data_str == 'E':
            #     sensor_q.empty()
            # else:
            #     data_num = float(data_str)
            #     sensor_q.put(data_num)
            # if sensor_q.qsize() == sensor_num:
            #     sensordata_save = sensordata_save.append(sensor_q, ignore_index=True)
            #     for ind in range(sensor_num):
            #         info_qlist[ind].put(sensor_q.get())


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
    sensordata_save.to_excel('sensor_data', sheet_name='test1')


def test():
    while True:
        # 串口读入byte类型的数据，打印出来是b'5.12\r\n'，需要译码
        data_raw = mSerial.readline()
        data_str = bytes.decode(data_raw)
        # print('com5', data_str)
        if len(data_str) > 2:
          data_num = float(re.sub("\D", "", data_str))/100
          print('com5', data_num)


if __name__ == "__main__":
    # test()
    app = pg.mkQApp()  # 建立app
    win = pg.GraphicsWindow()  # 建立窗口
    win.setWindowTitle(u'test')
    win.resize(1000, 600)  # 小窗口大小
    sensorgraph_list = list()
    sensorplot_list = list()
    data = np.zeros(default_length)
    for index in range(sensor_num):
        sensorgraph_list.append(win.addPlot())  # 把图p加入到窗口中
        tmp = sensorgraph_list[index]
        tmp.showGrid(x=True, y=True)  # 把X和Y的表格打开
        tmp.setRange(xRange=[0, default_length], yRange=[-6, 6], padding=0)
        tmp.setLabel(axis='left', text='y')
        tmp.setLabel(axis='bottom', text='x')
        tmp.setTitle('传感器{}数据'.format(index))  # 表格的名字
        sensorplot_list.append(sensorgraph_list[index].plot())
        curve_tmp = sensorplot_list[index]  # 绘制一个图形
        curve_tmp.setData(data)

    th_Readserial = threading.Thread(target=Serial)
    th_Readserial.start()
    # th_Displaysensor = threading.Thread(target=display)
    # th_Displaysensor.start()
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(plotData)  # 定时刷新数据显示
    timer.start(1)  # 调用频率（ms）
    app.exec_()
    print('start')



