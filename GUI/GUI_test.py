from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, \
    QStackedLayout, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import sys
import pyqtgraph as pg
import threading
import numpy as np
import time
from UR_Arm.UR_Control import UR_Robot_Arm
from UNO_SensorData.Sensordata import Read_Data
import logging
# pg.setConfigOptions(leftButtonPan=False)
logging.basicConfig(level=logging.INFO,
                    filename='gui_log',
                    filemode='a')


class BaseThread(QThread):

    def __init__(self, target, args):
        QThread.__init__(self)
        self.target = target
        self.args = args

    def run(self):
        self.target()

    def stop(self):
        self.terminate()


class GraspThread(QThread):
    status = pyqtSignal(str)

    def __init__(self, target, args, name=""):
        QThread.__init__(self)
        self.target = target
        self.args = args
        self.is_running = True

    def run(self):
        self.status.emit('begin')
        time.sleep(1)
        self.target()
        time.sleep(1)
        self.status.emit('end')

    def stop(self):
        self.terminate()


class SensorDataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.sensordata = Read_Data()
        self.read_q = self.sensordata.sensor_qlist
        self.plotdata = self.sensordata.sensordata_plot
        self.widget, self.plot = self.plot_widget_init()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.widget)
        self.serial_th = BaseThread(target=self.read_serial, args=None)
        self.plot_th = BaseThread(target=self.plot_data, args=None)

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
            tmp.setRange(xRange=[0, self.sensordata.length+10], yRange=[0, 5.5], padding=0)
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
        self.plot_th.start()
        self.serial_th.start()

    def read_serial(self):
        self.sensordata.serial_read()

    def plot_data(self):
        while True:
            for sensor_index in range(self.sensordata.num):
                data = self.plotdata[sensor_index]
                data[:-1] = data[1:]
                data[self.sensordata.length - 1] = self.read_q[sensor_index].get()
                # data[self.sensordata.length - 1] = np.random.randint(1, 100)/100
                self.plot[sensor_index].setData(data)
            time.sleep(0.05)


class GraspWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.rob = UR_Robot_Arm(a=0.1, v=0.0004, work_z=0.254, press_z=0.003)
        self.display()
        self.grasp_th = GraspThread(target=self.rob_grasp, args=None)
        self.test_th = BaseThread(target=self.rob_test, args=None)
        self.workinit_th = BaseThread(target=self.rob_move_for_work, args=None)

    def display(self):
        x = np.linspace(-5 * np.pi, 5 * np.pi, 500)
        y = 0.5 * np.sin(x)
        self.plt = pg.PlotWidget()
        self.plt.plot(x, y, pen="b")
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.plt)

    def rob_grasp(self):
        self.rob.exec_A()

    def rob_test(self):
        self.rob.press_A()

    def rob_move_for_work(self):
        self.rob.move_for_work()

    def start_grasp(self):
        self.grasp_th.start()

    def start_test(self):
        self.test_th.start()

    def start_move(self):
        self.workinit_th.start()

    def rob_stop(self):
        self.rob.stop()


class GraspWidget_test(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.plt = pg.PlotWidget()
        x = np.linspace(-5 * np.pi, 5 * np.pi, 500)
        y = 0.5 * np.sin(x)
        self.plt.plot(x, y, pen="b")
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.plt)
        self.grasp_th = GraspThread(target=self.rob_grasp, args=None)

    def rob_grasp(self):
        print('fake_grasp')
        time.sleep(1)

    def start_grasp(self):
        self.grasp_th.start()


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


class Main_Ui(QWidget):
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


class Main_window(QMainWindow):
    test_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(Main_window, self).__init__(parent)
        self.setWindowTitle("tactile_test")
        self.resize(1600, 900)
        # self.test_signal = pyqtSignal(str)

        # btn_layout
        self.btn_layout = QHBoxLayout()
        self.btn_backmain = QPushButton("主界面")
        self.btn_start = QPushButton("开始")
        self.btn_sensordata = QPushButton("传感器数据")
        self.btn_grasp = QPushButton("初始化位置")
        self.btn_test_begin = QPushButton("开始测试")
        self.btn_test_end = QPushButton("结束测试")
        self.btn_layout.addWidget(self.btn_backmain)
        self.btn_layout.addWidget(self.btn_start)
        self.btn_layout.addWidget(self.btn_sensordata)
        self.btn_layout.addWidget(self.btn_grasp)
        self.btn_layout.addWidget(self.btn_test_begin)
        self.btn_layout.addWidget(self.btn_test_end)
        self.btn_layout.addStretch()
        self.btn_start.clicked.connect(self.btn_start_click)
        self.btn_sensordata.clicked.connect(self.btn_sensordata_click)
        self.btn_grasp.clicked.connect(self.btn_grasp_click)
        self.btn_backmain.clicked.connect(self.btn_backmain_click)
        self.btn_test_begin.clicked.connect(self.btn_test_begin_click)
        self.btn_test_end.clicked.connect(self.btn_test_end_click)

        # display_layout
        self.display_layout = QStackedLayout()
        self.mainUI_wgt = Main_Ui()
        self.sensor_wgt = SensorDataWidget()
        # self.sensor_wgt = SensorData_test()
        self.robot_wgt = GraspWidget()
        # self.robot_wgt = GraspWidget_test()
        self.robot_wgt.grasp_th.status.connect(self.sensor_wgt.sensordata.save_graspdata)
        self.display_layout.addWidget(self.sensor_wgt)
        self.display_layout.addWidget(self.robot_wgt)
        self.display_layout.addWidget(self.mainUI_wgt)

        # test_data
        self.test_signal.connect(self.sensor_wgt.sensordata.save_graspdata)

        # main layout (embed)
        self.mainlayout = QVBoxLayout()
        self.mainlayout.addLayout(self.btn_layout)
        self.mainlayout.addLayout(self.display_layout)
        mainwidget = QWidget()
        mainwidget.setLayout(self.mainlayout)
        self.setCentralWidget(mainwidget)

    def btn_start_click(self):
        self.sensor_wgt.start_work()

    def btn_sensordata_click(self):
        # print(threading.currentThread())
        self.display_layout.setCurrentIndex(0)

    def btn_grasp_click(self):
        # print(threading.currentThread())
        self.display_layout.setCurrentIndex(1)
        self.robot_wgt.start_move()

    def btn_backmain_click(self):
        self.display_layout.setCurrentIndex(2)

    def btn_test_begin_click(self):
        self.test_signal.emit('begin')
        self.robot_wgt.start_test()

    def btn_test_end_click(self):
        self.test_signal.emit('end')
        self.robot_wgt.rob_stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main_window()
    win.show()
    sys.exit(app.exec_())
