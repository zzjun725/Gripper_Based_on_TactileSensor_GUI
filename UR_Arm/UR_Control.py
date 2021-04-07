import urx
import logging
import time
from utils import utils


class UR_Robot_Arm:
    def __init__(self, rob_id="192.168.1.233",
                 ini_y=0.1, ini_z=-0.2,
                 work_z=0.255, work_y=0.10,
                 press_z=0.0035, press_x=0.02,
                 grasp_times=2,
                 a=0.15, v=0.25):
        self.ini_y = ini_y
        self.ini_z = ini_z
        self.work_z = work_z
        self.work_y = work_y
        self.press_z = press_z
        self.press_x = press_x
        self.work_a = a
        self.work_v = v
        self.grasptimes = grasp_times
        self.rob = urx.Robot(rob_id)
        self.inipose = utils.safe_setzero(self.rob.getj())
        self.rob.set_tcp((0, 0, 0, 0, 0, 0))
        self.rob.set_payload(0.5, (0, 0, 0))

    def get_pose(self):
        print('关节角度', self.rob.getj())
        print('绝对坐标', self.rob.getl())

    def move_for_work(self, a=0.2, v=0.4):
        base = -108
        shoulder = -90
        elbow = 60
        # wrist_d = 30
        # wrist_e = 90
        wrist_d = -60
        wrist_e = -90
        wrist_f = 0
        pose = self.rob.getj()
        print("init joint angle", pose)
        work_pose = [utils.deg2rad(deg) for deg in [base, shoulder, elbow, wrist_d, wrist_e, wrist_f]]
        print("work joint angle", work_pose)
        self.rob.movej(work_pose, acc=a, vel=v, wait=False)
        time.sleep(5)
        self.rob.translate_tool((0, self.work_y, self.work_z),
                               acc=0.1, vel=0.2, wait=False)
        time.sleep(8)

        return work_pose

    def grasp_A(self):
        # tool坐标系，x逆，y上，z前
        # y后 z下 x右
        pose = self.rob.getl()
        print("robot tcp is at: ", pose)
        self.rob.translate_tool((0, self.ini_y, self.ini_z),
                                acc=self.work_a, vel=self.work_v, wait=False)
        time.sleep(5)
        for _ in range(self.grasptimes):
            self.rob.translate_tool((0, self.work_y, self.work_z),
                                    acc=self.work_a, vel=self.work_v, wait=False)
            time.sleep(5)
            self.rob.translate_tool((0, -self.work_y, -self.work_z),
                                    acc=self.work_a, vel=self.work_v, wait=False)
            time.sleep(5)

    def press_A(self):
        pose = self.rob.getl()
        print("robot tcp is at: ", pose)

        for _ in range(6):
            self.rob.translate_tool((0, 0, self.press_z),
                                    acc=self.work_a, vel=self.work_v, wait=False)
            time.sleep(15)
            self.rob.translate_tool((0, 0, -self.press_z),
                                    acc=self.work_a, vel=self.work_v, wait=False)
            time.sleep(15)
            # self.rob.translate_tool((self.press_x, 0, 0),
            #                         acc=0.1, vel=0.1, wait=False)
            # time.sleep(2)

    def back_to_init(self, a=0.2, v=0.4):
        self.rob.movej(self.inipose, acc=a, vel=v, wait=False)

    def exec_A(self):
        self.move_for_work()
        time.sleep(8)
        self.grasp_A()
        time.sleep(1)
        self.back_to_init()
        time.sleep(8)

    def stop(self):
        self.rob.stop()

    def close(self):
        self.rob.close()


def main():
    logging.basicConfig(level=logging.WARN)

    ur = UR_Robot_Arm(a=0.05, v=0.0005)
    time.sleep(0.5)
    # ur.move_for_work()
    print(ur.rob.getj())

    ur.press_A()
    ur.close()


if __name__ == "__main__":
    main()
