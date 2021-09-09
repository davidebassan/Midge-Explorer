#!/usr/bin/python3

import rospy
import cv2
from cv_bridge import CvBridge
from std_msgs.msg import String
from actuators.actuators import Move
from sensors.laser_scan import Laser
from sensors.camera import Camera
from utils.Coordinates import Coordinates
from sensor_msgs.msg import LaserScan


class Midge:
    def __init__(self):
        self.actuators = Move()
        self.laser = Laser()
        self.camera = Camera()
        self.cv2_bridge = CvBridge()
        self.last_image = None
        self.last_laser_info = None

    def retrieve_laser(self):
        """
            Retrieve laser information
        """
        self.laser.capture()
        self.last_laser_info = self.laser.get_laser_info()
        return self.last_laser_info

    def retrieve_camera(self):
        """
            Take a photo and convert to cv2 image
        """
        def ros_to_cv(image_msg):
            return self.cv2_bridge.imgmsg_to_cv2(image_msg, desidered_encoding='passtrhough')

        camera.capture(info=True)
        camera.get_camera_info()
        image = camera.get_camera_image()
        self.last_image = ros_to_cv(image)
        return self.last_image

    def build_map(self):
        pass

    def motor_navigation(self):
        pass


if __name__ == '__main__':
    """
        Main function
    """
    midge = Midge()

    # Get laser information about obstacles
    laser_information = midge.retrieve_laser()
    print(laser_information.ranges)
    print("{0°: " + str(laser_information.ranges[0]) + "; 90°: " + str(laser_information.ranges[360]) + "; 180°: " + str(laser_information.ranges[719]) + ";")







