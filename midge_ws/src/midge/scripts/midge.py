#!/usr/bin/python3

import rospy
import cv2
import random
import tf
from cv_bridge import CvBridge
from std_msgs.msg import String
from actuators.actuators import Move
from exploration.exploration import Exploration
from sensors.laser_scan import Laser
from sensors.camera import Camera
from sensor_msgs.msg import LaserScan
from web.web import Web

class Midge:
    def __init__(self):
        self.node = rospy.init_node('Midge', anonymous=True)
        self.actuators = Move()
        self.laser = Laser()
        self.camera = Camera()
        self.exploration = Exploration()
        self.cv2_bridge = CvBridge()
        self.web = Web()
        self.last_image = None
        self.last_laser_info = None
        self.laser_MARGIN_DEGREE = 30
        self.laser_MIN_DISTANCE = 1

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

    def obstacles_near(self, laser_ranges):
        for j in range((90 - self.laser_MARGIN_DEGREE) * 4, (90 + self.laser_MARGIN_DEGREE) * 4):
            if laser_ranges[j] < self.laser_MIN_DISTANCE:
                return True
        return False

    def get_transformed_position(self):
        return self.exploration.get_transformed_position()


if __name__ == '__main__':
    """
        Main function
    """
    midge = Midge()

    while True:
        # Move Avoid Obstacle
        if midge.web.get_navigation_method() == 'joy':
            midge.actuators.joystick_move()
            msg = midge.retrieve_laser()
            cmd_vel = midge.exploration.protection_obstacle(msg)
        else:
            msg = midge.retrieve_laser()
            cmd_vel = midge.exploration.move_avoid_obstacle(msg)
            midge.actuators.controller(cmd_vel)


