import serial
from queue import Queue
from copy import deepcopy
import pandas as pd
import re
import numpy as np
import threading
from utils import utils
import time
import os
from matplotlib import pyplot as plt
from scipy import signal
from utils.utils import path_filler
'''
To Do List:
对终止符的处理
index = False， 不用clip

'''

class Read_Data(object):
    def __init__(self, sensor_num=6, default_length=200, default_com='COM5'):
        self.end_index = 0
        self.begin_index = 0
        self.begin_time = 0
        self.end_time = 0
        self.test_times = 0
        self.serial = self.serial_init(default_com)
        self.num = sensor_num
        self.length = default_length
        self.sensor_qlist = [Queue(maxsize=0) for _ in range(self.num)]  # read all real-time sensor data
        self.sensordata_plot = np.array([np.zeros(self.length) for _ in range(self.num)], dtype=np.float64)  # plot data
        self.sensor_q = Queue(maxsize=self.num)  # read a frame of sensor data
        self.sensordata_per = [0 for _ in range(self.num)]  # store a frame of sensor data
        self.sensordata_save = pd.DataFrame([self.sensordata_per], columns=range(self.num))
        self.sensordata_deltasave = pd.DataFrame([self.sensordata_per], columns=range(self.num))
        self.sensordata_clip = pd.DataFrame([self.sensordata_per], columns=range(self.num))
        self.data_path = self.data_dir_init(path_filler('Data'))  # create a dir for data saving

    @staticmethod
    def serial_init(com):
        myserial = serial.Serial(
            port=com,
            baudrate=115200,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )
        return myserial

    @staticmethod
    def data_dir_init(data_dir):
        local_time_raw = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        local_time = re.sub("\D", "", local_time_raw)
        data_path = os.path.join(data_dir, 'grasp_data{}'.format(local_time))
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, 'abs'), exist_ok=True)
        os.makedirs(os.path.join(data_path, 'delta'), exist_ok=True)
        return data_path

    def serial_read(self):
        while True:
            n = self.serial.inWaiting()
            if n:
                data_raw = self.serial.readline()
                data_str = bytes.decode(data_raw)
                # 若读到终止符('e')则清空队列
                if len(data_str) == 3:
                    self.sensor_q.queue.clear()
                else:
                    data_fliter = re.sub("\D", "", data_str)
                    if len(data_fliter) > 2:
                        data_num = float(data_fliter) / 100
                        if data_num < 6:
                            self.sensor_q.put(data_num)
                # 若接收到完整的n个数据则开始输送数据
                if self.sensor_q.qsize() == self.num:
                    for ind in range(self.num):
                        self.sensordata_per[ind] = self.sensor_q.get()
                        self.sensor_qlist[ind].put(deepcopy(self.sensordata_per[ind]))
                    old_per = self.sensordata_save[-1:].to_numpy()[..., 0:self.num]
                    # self.sensordata_per = self.sensordata_per[0:self.num]
                    print(self.sensordata_per)
                    delta_per = utils.get_item_delta(self.sensordata_per, old_per)
                    time_stamp = str(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()))
                    delta_per += [time_stamp]
                    # self.sensordata_per += [time_stamp]
                    self.sensordata_deltasave = self.sensordata_deltasave.append([delta_per], ignore_index=True)
                    self.sensordata_save = self.sensordata_save.append([self.sensordata_per+[time_stamp]], ignore_index=True)

    def _print_data(self):
        while True:
            # 串口读入byte类型的数据，打印出来是b'5.12\r\n'，需要译码
            data_raw = self.serial.readline()
            data_str = bytes.decode(data_raw)
            # print('com5', data_str)
            if len(data_str) == 3:
                # print('clear')
                self.sensor_q.queue.clear()
                # print(sensor_q.qsize())
            else:
                data_fliter = re.sub("\D", "", data_str)
                if len(data_fliter) > 2:
                    data_num = float(data_fliter) / 100
                    if data_num < 6:
                        self.sensor_q.put(data_num)
            if self.sensor_q.qsize() == self.num:
                for ind in range(self.num):
                    self.sensordata_per[ind] = self.sensor_q.get()
                    self.sensor_qlist[ind].put(deepcopy(self.sensordata_per[ind]))
                sensordata_save = sensordata_save.append([self.sensordata_per], ignore_index=True)
                print(self.sensordata_per)
                print(sensordata_save)

    def save_data(self, save_data, mode):
        # save_data.to_excel('sensor_data', sheet_name='test1')
        # save_data.to_csv('test.txt', sep='\t', index=False, header=None)
        self.sensordata_clip.drop(self.sensordata_clip.index, inplace=True)
        self.sensordata_clip = self.sensordata_clip.append(save_data, ignore_index=True)
        self.sensordata_clip.to_csv(os.path.join(self.data_path,
                                                 '{}/{}_{}{}.txt'
                                                 .format(mode, mode, self.begin_time, self.end_time)),
                                    index=0)
        print('{}_data is saved'.format(mode))

    def save_graspdata(self, status=None):
        if status == 'begin':
            print('begin')
            self.begin_index = self.sensordata_save.shape[0]
            self.begin_time = str(time.strftime("%d_%H%M%S", time.localtime()))
        if status == 'end':
            print('end')
            self.end_index = self.sensordata_save.shape[0]
            grasp_abs_data = self.sensordata_save[self.begin_index:self.end_index]
            grasp_delta_data = self.sensordata_deltasave[self.begin_index:self.end_index]
            # print(grasp_abs_data.to_numpy())
            self.test_times += 1
            self.end_time = str(time.strftime("-%H%M%S", time.localtime()))
            self.save_data(grasp_abs_data, mode='abs')
            self.save_data(grasp_delta_data, mode='delta')


class DataLoader(object):
    def __init__(self):
        pass

    def plot(self, data_list, sub=False):
        fig = []
        if isinstance(data_list, list):
            for data in data_list:
                # data_plot = data.iloc[:, :-1]
                fig.append(data.plot.line(subplots=sub, title='Tactile sensor'))
        if isinstance(data_list, pd.DataFrame):
            fig.append(data_list.plot.line(subplots=sub))
        return fig


class Tactile_DataLoader(DataLoader):
    def __init__(self, sensor_num=6):
        super().__init__()
        self.num = sensor_num
        self.sensordata_per = [0 for _ in range(sensor_num)]  # 暂存给dataframe 防止丢包
        self.sensordata_save = pd.DataFrame([self.sensordata_per], columns=range(sensor_num))
        self.sensordata_deltasave = pd.DataFrame([self.sensordata_per], columns=range(sensor_num))
        self.test_times = 0
        self.start_sample = 50
        self.end_sample = 300

    def load_data(self, data_dir, mode='abs', point='single', pin=0):
        data_path_list = os.listdir(os.path.join(data_dir, mode))
        data_list = [pd.DataFrame() for _ in range(len(data_path_list))]
        if point == 'muti':
            for idx in range(len(data_path_list)):
                data_path = os.path.join(data_dir, mode, data_path_list[idx])
                data_list[idx] = pd.read_csv(data_path)
            return data_list
        if point == 'single':
            for idx in range(len(data_path_list)):
                data_path = os.path.join(data_dir, 'abs', data_path_list[idx])
                data_list[idx] = pd.read_csv(data_path).iloc[self.start_sample:self.end_sample, pin].reset_index(drop=True)
            return data_list


    #def plot(self, data_list, ):


class Force_Dataloader(DataLoader):
    def __init__(self):
        super().__init__()
        self.time_stamp_pos = 9
        self.spec_force_pos = 2
        self.start_sample = 50
        self.end_sample = 300

    def load_data(self, data_dir, times=1):
        data_path_list = os.listdir(data_dir)
        data_list = [pd.DataFrame() for _ in range(len(data_path_list))]
        start_time_list = [0]*len(data_path_list)
        for idx in range(len(data_path_list)):
            data_path = os.path.join(data_dir, data_path_list[idx])
            data_tmp = pd.read_csv(data_path)
            start_time_list[idx] = data_tmp.columns.to_list()[self.time_stamp_pos]
            data_list[idx] = pd.read_csv(data_path).iloc[self.start_sample:self.end_sample, self.spec_force_pos]
        return data_list, start_time_list


# class SingalFilter():
#     t = np.linspace(0, 1.0, 2001)
#     xlow = np.sin(2 * np.pi * 5 * t)
#     xhigh = np.sin(2 * np.pi * 250 * t)
#     x = xlow + xhigh
#     b, a = signal.butter(8, 0.125)

if __name__ == '__main__':
    k = Read_Data()
    print(k)


