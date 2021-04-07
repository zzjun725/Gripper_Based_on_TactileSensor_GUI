from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, \
    QStackedLayout, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import sys
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


# pg.setConfigOptions(leftButtonPan=False)

class RunThread(QThread):
    # counter_value = pyqtSignal(int)

    def __init__(self, target, args, name=""):
        QThread.__init__(self)
        self.target = target
        self.args = args
        self.is_running = True

    def run(self):
        # print("starting",self.name, "at:",ctime())
        # self.res = self.target(*self.args)
        self.target()

    def stop(self):
        # 负责停止线程
        self.terminate()


class SensorData(object):
    def __init__(self, sensor_num=6, default_length=200, default_com='COM5'):
        self.serial = self.serial_init(default_com)
        self.num = sensor_num
        self.length = default_length
        self.info_qlist = [Queue(maxsize=0) for _ in range(sensor_num)]
        self.sensordata_matrix = np.array([np.zeros(default_length) for _ in range(sensor_num)], dtype=np.float64)
        self.sensordata_save = pd.DataFrame(columns=range(sensor_num))
        self.sensor_q = Queue(maxsize=sensor_num)  # 暂存 防止丢包
        self.sensordata_per = [0 for _ in range(sensor_num)]  # 暂存给dataframe 防止丢包
        self.sensordata_save = self.sensordata_save.append([self.sensordata_per], ignore_index=True)

    def serial_init(self, com):
        myserial = serial.Serial(
            port=com,
            baudrate=115200,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )
        return myserial

    def serial_read(self):
        data_num = 0
        print(threading.currentThread())
        while True:
            n = self.serial.inWaiting()
            if n:
                data_raw = self.serial.readline()
                data_str = bytes.decode(data_raw)
                # print('com5', data_str)
                # 若读到终止符则清空队列
                if data_str == 'e':
                    self.sensor_q.empty()
                else:
                    data_fliter = re.sub("\D", "", data_str)
                    if len(data_fliter) > 2:
                        data_num = float(data_fliter) / 100
                        self.sensor_q.put(data_num)
                # 若接收到完整的n个数据则开始输送数据
                if self.sensor_q.qsize() == self.num:
                    for ind in range(self.num):
                        self.sensordata_per[ind] = self.sensor_q.get()
                        self.info_qlist[ind].put(deepcopy(self.sensordata_per[ind]))
                    self.sensordata_save = self.sensordata_save.append([self.sensordata_per], ignore_index=True)

    def _print_data(self):
        global sensordata_save
        while True:
            # 串口读入byte类型的数据，打印出来是b'5.12\r\n'，需要译码
            data_raw = self.serial.readline()
            data_str = bytes.decode(data_raw)
            # print('com5', data_str)
            if data_str == 'e':
                self.sensor_q.empty()
            else:
                data_fliter = re.sub("\D", "", data_str)
                if len(data_fliter) > 2:
                    data_num = float(data_fliter) / 100
                    self.sensor_q.put(data_num)
            if self.sensor_q.qsize() == self.num:
                for ind in range(self.num):
                    self.sensordata_per[ind] = self.sensor_q.get()
                    self.info_qlist[ind].put(deepcopy(self.sensordata_per[ind]))
                sensordata_save = sensordata_save.append([self.sensordata_per], ignore_index=True)
                print(self.sensordata_per)
                print(sensordata_save)

    def save_data(self):
        self.sensordata_save.to_excel('sensor_data', sheet_name='test1')


class SensorDataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.sensordata = SensorData()
        self.read_q = self.sensordata.info_qlist
        self.plotdata = self.sensordata.sensordata_matrix
        self.widget, self.plot = self.plot_widget_init()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.widget)

    def plot_widget_init(self):
        data = np.zeros(self.sensordata.length)
        sensorgraph_list = list()
        sensorplot_list = list()
        gridLayout = QGridLayout()
        sensor_widget = QWidget()
        for index in range(self.sensordata.num):
            sensorgraph_list.append(pg.PlotWidget())  # 把图p加入到窗口中
            tmp = sensorgraph_list[index]
            if index < 3:
                gridLayout.addWidget(sensorgraph_list[index], index, 0)
            else:
                gridLayout.addWidget(sensorgraph_list[index], index - 3, 1)
            tmp.showGrid(x=True, y=True)  # 把X和Y的网格打开
            tmp.setRange(xRange=[0, self.sensordata.length+10], yRange=[-3, 6], padding=0)
            tmp.setLabel(axis='left', text='y')
            tmp.setLabel(axis='bottom', text='x')
            tmp.setTitle('传感器{}数据'.format(index))  # 表格的名字
            sensorplot_list.append(sensorgraph_list[index].plot())
            curve_tmp = sensorplot_list[index]  # 绘制一个图形
            curve_tmp.setData(data)
        sensor_widget.setLayout(gridLayout)
        return sensor_widget, sensorplot_list

    def start_work(self):
        print(threading.currentThread())
        # self.plot_timer = QTimer()
        # self.plot_timer.timeout.connect(self.plotData)  # 定时刷新数据显示
        # self.plot_timer.start(1)  # 调用频率（ms）
        self.plot_th = RunThread(target=self.plotData, args=None)
        self.plot_th.start()
        self.serial_th = RunThread(target=self.read_serial, args=None)
        self.serial_th.start()
        # self.serial_th = threading.Thread(target=self.read_serial)
        # self.serial_th.start()

    def read_serial(self):
        self.sensordata.serial_read()

    def plotData(self):
        while True:
            for sensor_index in range(self.sensordata.num):
                data = self.plotdata[sensor_index]
                # if self.times < self.length:
                #     data[self.times] = self.sensor_qlist[sensor_index].get()
                #     self.times = self.times + 1
                # else:
                data[:-1] = data[1:]
                data[self.sensordata.length - 1] = self.read_q[sensor_index].get()
                # data[self.sensordata.length - 1] = np.random.randint(1, 100)/100
                self.plot[sensor_index].setData(data)
                print(threading.currentThread())
            time.sleep(0.01)


class SensorData_test(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.plt = pg.PlotWidget()
        x = np.linspace(-5 * np.pi, 5 * np.pi, 500)
        y = 0.5 * np.sin(x)
        self.plt.plot(x, y, pen="r")

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.plt)
        # self.setStyleSheet("background-color:green;")


class GraspWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.plt = pg.PlotWidget()
        x = np.linspace(-5 * np.pi, 5 * np.pi, 500)
        y = 0.5 * np.sin(x)
        self.plt.plot(x, y, pen="b")

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.plt)


class Main_win(QMainWindow):
    def __init__(self, parent=None):
        super(Main_win, self).__init__(parent)
        self.setWindowTitle("tactile_test")
        self.resize(1600, 900)

        # 按钮widget设置
        self.btn_start = QPushButton("开始")
        self.btn_sensordata = QPushButton("传感器数据")
        self.btn_grasp = QPushButton("执行抓取")
        # self.btn_sensordata.setFixedSize(200, 25)
        # self.btn_grasp.setFixedSize(200, 25)
        self.btn_wgt = QWidget()
        # self.btn_widget.setFixedHeight(35)
        self.btn_layout = QHBoxLayout()
        # self.btn_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_layout.addWidget(self.btn_start)
        self.btn_layout.addWidget(self.btn_sensordata)
        self.btn_layout.addWidget(self.btn_grasp)
        self.btn_layout.addStretch()
        self.btn_wgt.setLayout(self.btn_layout)
        self.btn_start.clicked.connect(self.btn_start_click)
        self.btn_sensordata.clicked.connect(self.btn_sensordata_click)
        self.btn_grasp.clicked.connect(self.btn_grasp_click)

        # self.sensor_wgt = SensorData_test()
        self.sensor_wgt = SensorDataWidget()
        self.robot_wgt = GraspWidget()

        self.displaywidget = QWidget()
        self.stacked_layout = QStackedLayout()
        self.displaywidget.setLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.sensor_wgt)
        self.stacked_layout.addWidget(self.robot_wgt)

        # main layout 设置
        self.mainlayout = QVBoxLayout()
        # self.mainlayout.addLayout(self.btn_layout)
        # self.mainlayout.addLayout(self.stacked_layout)
        self.mainlayout.addWidget(self.btn_wgt)
        self.mainlayout.addWidget(self.displaywidget)

        centralWidget = QWidget()
        centralWidget.setLayout(self.mainlayout)
        self.setCentralWidget(centralWidget)

    def btn_start_click(self):
        self.sensor_wgt.start_work()

    def btn_sensordata_click(self):
        # print(threading.currentThread())
        self.stacked_layout.setCurrentIndex(0)

    def btn_grasp_click(self):
        # print(threading.currentThread())
        self.stacked_layout.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main_win()
    win.show()
    sys.exit(app.exec_())
