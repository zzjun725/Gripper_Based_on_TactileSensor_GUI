from math import pi
import copy
import os


def path_filler(path):
    abs_path = os.path.abspath(os.path.join('..', path))
    return abs_path


def deg2rad(deg):
    return round(deg * pi / 180, 4)


def safe_abs(num):
    if num >= 0:
        return num
    else:
        return -num


def safe_setzero(a_list):
    return_list = copy.deepcopy(a_list)
    for index, item in enumerate(a_list):
        if safe_abs(item) < 0.0015:
            return_list[index] = 0
        else:
            return_list[index] = item
    return return_list


def safe_round(raw_data, num=2):
    if isinstance(raw_data, list):
        result_list = copy.deepcopy(raw_data)
        for idx, i in enumerate(raw_data):
            result_list[idx] = round(i, num)
        return result_list


def get_item_delta(new_list, old_list):
    delta_list = (new_list - old_list).tolist()[0]
    delta_list.reverse()
    # print(delta_list[:-1])
    for idx, item in enumerate(delta_list[:-1]):
        delta_list[idx] = delta_list[idx] - delta_list[idx + 1]
    delta_list = safe_setzero(safe_round(delta_list))
    return delta_list
