from UNO_SensorData.Sensordata import Tactile_DataLoader, Force_Dataloader
import os
from matplotlib import pyplot as plt
from copy import deepcopy
import numpy as np
import pandas as pd
from utils.utils import path_filler

tacile_data_dir = [os.path.join(path_filler('Data'), file)
                   for file in os.listdir(path_filler('Data'))
                   if file.startswith('grasp_data20210407160922dd1')]

tactile_data_loader = Tactile_DataLoader()
for data_path in tacile_data_dir:
    t_data_list = tactile_data_loader.load_data(data_dir=data_path)
    # fig_list = tactile_data_loader.plot(data_list)
    # for fig in fig_list:
    #     plt.show()

force_data_dir = [os.path.join(path_filler('Data'), file)
                  for file in os.listdir(path_filler('Data'))
                  if file.startswith('force')]

force_data_loader = Force_Dataloader()
# 读取力传感器数据并使用列表存储
for data_path in force_data_dir:
    data_list, start_time_list = force_data_loader.load_data(data_dir=data_path)
data_inverse_list = deepcopy(data_list)
for idx, item in enumerate(data_list):
    tmp = deepcopy(np.negative(item.to_numpy()))
    data_inverse_list[idx] = pd.Series(tmp)
# 绘制力传感器数据图像

plt.figure()
for data in t_data_list:
    # data_plot = data.iloc[:, :-1]
    t_data_inverse_list = deepcopy(t_data_list)
    for idx, item in enumerate(t_data_list):
        tmp = deepcopy(item.to_numpy())
        bias = np.array([0.2]*len(tmp))
        tmp = tmp-bias
        t_data_inverse_list[idx] = pd.Series(tmp)
    t_data_inverse_list[0].plot.line(label='tactile')
    # t_data_list[0].plot.line(label='tactile')
data_inverse_list[1].plot(title='two sensor', c='red', label='force')
plt.legend()
plt.show()
