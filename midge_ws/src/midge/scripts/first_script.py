#!/usr/bin/python3

import rospy
from std_msgs.msg import String
from actuators.actuators import Move
from sensors.laser_scan import Laser
from utils.Coordinates import Coordinates
from sensor_msgs.msg import LaserScan

class Midge:

    def __init__(self):
        actuators = Move(0, 0)


def callback(msg):
    print(msg.ranges)



if __name__ == '__main__':
    laser = Laser()
    info = laser.get_laser_info()
    print(info)
    laser.stop()
    """while True:
        if info is not None:
            for degree in info:
                print(degree)
    """

