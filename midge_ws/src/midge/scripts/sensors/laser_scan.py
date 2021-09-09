#!/usr/bin/python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan


class Laser:
    """
        Handle with lidar sensor
    """
    def __init__(self):
        self.node = rospy.init_node('Laser_Scan', anonymous=True)
        self.laser_info = None
        self.topic = '/scan'

    def get_laser_info(self):
        """
            @return laser_info
        """
        return self.laser_info

    def capture(self):
        """
            Take information from lidar sensor
        """
        self.laser_info = rospy.wait_for_message(self.topic, LaserScan)