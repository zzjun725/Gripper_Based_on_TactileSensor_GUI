import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
from queue import Queue
import time

i = 0
q = Queue(maxsize=0)
data_num = 0

mSerial = serial.Serial(
    port='COM5',
    baudrate=115200,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)


def Serial():
    global i
    global q
    while True:
        n = mSerial.inWaiting()
        if n:
            data_raw = mSerial.readline()
            data_str = bytes.decode(data_raw)
            if len(data_str) > 2:
                data_num = float(data_str)
            q.put(data_num)


def plotData():
    global i
    if i < historyLength:
        data[i] = q.get()
        i = i + 1
    else:
        data[:-1] = data[1:]
        data[i - 1] = q.get()
    curve.setData(data)


if __name__ == "__main__":
    app = pg.mkQApp()  # 建立app
    win = pg.GraphicsWindow()  # 建立窗口
    win.setWindowTitle(u'pyqtgraph逐点画波形图')
    win.resize(800, 500)  # 小窗口大小
    historyLength = 100  # 横坐标长度
    a = 0
    data = np.zeros(historyLength)  # 把数组长度定下来
    p = win.addPlot()  # 把图p加入到窗口中
    p.showGrid(x=True, y=True)  # 把X和Y的表格打开
    p.setRange(xRange=[0, historyLength], yRange=[-1, 6], padding=0)
    p.setLabel(axis='left', text='y')  # 靠左
    p.setLabel(axis='bottom', text='x')
    p.setTitle('test')  # 表格的名字
    curve = p.plot()  # 绘制一个图形
    curve.setData(data)
    th1 = threading.Thread(target=Serial)
    th1.start()
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(plotData)  # 定时刷新数据显示
    timer.start(1)  # 多少ms调用一次
    app.exec_()
