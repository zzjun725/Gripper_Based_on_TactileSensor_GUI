import urx
import logging
import time
import copy
import fire
from math import pi

default_rob_id = "192.168.1.233"


def deg2rad(deg):
    return round(deg*pi/180, 4)


default_angel = {
    'base': 0,
    'shoulder': -1.57,
    'albow': 0,
    'wristD': -1.57,
    'wristE': 0,
    'wristF': 0
}


def init_robot(rob_id):
    rob = urx.Robot(rob_id)
    ini = rob.getj()
    return rob, ini


def safe_setzero(a_list):
    return_list = copy.deepcopy(a_list)
    for index, item in enumerate(a_list):
        if abs(item) < 0.005:
            return_list[index] = 0
        else:
            return_list[index] = item
    return return_list


def get_pose(robo=None):
    print('关节角度', robo.getj())
    print('绝对坐标', robo.getl())


def move_for_work(robo=None, a=0.2, v=0.4):
    if robo is None:
        raise AssertionError('must choose a robot')
    base = -110
    shoulder = -90
    elbow = 60
    wrist_d = 30
    wrist_e = 90
    wrist_f = 0
    pose = robo.getj()
    print("init joint angle", pose)
    work_pose = [deg2rad(deg) for deg in [base, shoulder, elbow, wrist_d, wrist_e, wrist_f]]
    print("work joint angle", work_pose)
    robo.movej(work_pose, acc=a, vel=v, wait=False)
    return work_pose


def back_to_init(robo=None, inipose=None, a=0.2, v=0.4):
    if robo is None:
        raise AssertionError('must choose a robot')
    robo.movej(inipose, acc=a, vel=v, wait=False)


def grasp(robo=None, ini_y=0.1, ini_z=-0.15, work_z=0.3, work_y=-0.24, grasp_times=2, a=0.15, v=0.25):
    if robo is None:
        raise AssertionError('must choose a robot')
    # tool坐标系，x逆，y上，z前
    pose = robo.getl()
    print("robot tcp is at: ", pose)
    robo.translate_tool((0, ini_y, ini_z), acc=a, vel=v, wait=False)
    time.sleep(5)
    for _ in range(grasp_times):
        robo.translate_tool((0, work_y, work_z), acc=a, vel=v, wait=False)
        time.sleep(5)
        robo.translate_tool((0, -work_y, -work_z), acc=a, vel=v, wait=False)
        time.sleep(5)
    # print("relative move back and forth in tool coordinate")
    # robo.translate_tool((0, 0, -l), acc=a, vel=v)
    # robo.translate_tool((0, 0, l), acc=a, vel=v)


def main(rob_id=default_rob_id):
    logging.basicConfig(level=logging.WARN)

    rob = urx.Robot(rob_id)
    rob.set_tcp((0, 0, 0, 0, 0, 0))
    rob.set_payload(0.5, (0, 0, 0))
    init_pose = safe_setzero(rob.getj())
    time.sleep(0.5)

    move_for_work(rob)
    print('init')
    time.sleep(8)
    # print(rob.getj())
    # print('move_for_work')
    # time.sleep(4)
    # # print(rob.getj())
    grasp(rob)
    print('grasp')
    time.sleep(1)
    # print('grasp')
    # print(init_pose)
    back_to_init(rob, inipose=init_pose)
    # time.sleep(6)

    rob.close()


if __name__ == "__main__":
    main()
