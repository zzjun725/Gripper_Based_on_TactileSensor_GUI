from urx import Robot
rob = Robot("192.168.1.1")
rob.x  # returns current x
rob.rx  # returns 0 (could return x component of axis vector, but it is not very usefull
rob.rx -= 0.1  # rotate tool around X axis
rob.z_t += 0.01  # move robot in tool z axis for +1cm

csys = rob.new_csys_from_xpy() #  generate a new csys from 3 points: X, origin, Y
rob.set_csys(csys)