from UNO_SensorData.Sensordata import Tactile_DataLoader, Force_Dataloader
import os
from matplotlib import pyplot as plt
from copy import deepcopy
import numpy as np
import pandas as pd
from utils.utils import path_filler

data_path_list = [os.path.join(path_filler('Data'), file)
                  for file in os.listdir(path_filler('Data'))
                  if file.startswith('grasp_data20210407151308333')]
data_loader = Tactile_DataLoader()
for data_path in data_path_list:
    data_list = data_loader.load_data(data_dir=data_path)
    fig_list = data_loader.plot(data_list)
    for fig in fig_list:
        plt.show()

force_data_path_list = [os.path.join(path_filler('Data'), file)
                        for file in os.listdir(path_filler('Data'))
                        if file.startswith('force')]
force_data_loader = Force_Dataloader()
#
for data_path in force_data_path_list:
    data_list, start_time_list = force_data_loader.load_data(data_dir=data_path)
#     # fig_list = force_data_loader.plot(data_list)
#     # for fig in fig_list:
#     #     plt.show()
data_inverse_list = deepcopy(data_list)
for idx, item in enumerate(data_list):
    tmp = deepcopy(np.negative(item.to_numpy()))
    data_inverse_list[idx] = pd.Series(tmp)
#
data_inverse_list[0].plot(title=start_time_list[0])
plt.show()
