#!/usr/bin/python3

import rospy
import cv2
import random
from cv_bridge import CvBridge
from std_msgs.msg import String
from actuators.actuators import Move
from sensors.laser_scan import Laser
from sensors.camera import Camera
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

    """
    # First approach: Scheduled Navigation
    
    # Get laser information about obstacles
    laser_information = midge.retrieve_laser()
    print(laser_information.ranges)
    print("{0°: " + str(laser_information.ranges[0]) + "; 90°: " + str(laser_information.ranges[360]) + "; 180°: " + str(laser_information.ranges[719]) + ";")

    max_distance = max(laser_information.ranges)
    max_distance_degree = laser_information.ranges.index(max_distance) / 4
    """
    while True:
        # Second approach: Random Navigation
        # Get Laser information
        laser_information = midge.retrieve_laser()

        # Select a random degree that is > 2
        retry = 0
        bypass = False
        degree = random.randint(0, 719)
        # TODO: Controllare da 10 gradi prima a 10 gradi dopo!
        while laser_information.ranges[degree] < 2 or (bypass is True and laser_information.ranges[360]):
            degree = random.randint(0, 719)
            retry += 1

            # Note:          90
            #              0   180
            #               270

            # Make a 180° degree rotation because my robot start from
            if retry > 5:
                degree = 180
                retry = 0
                # Do rotation and checks again
                midge.actuators.rotate(degree)
                bypass=True

        midge.actuators.straight()
