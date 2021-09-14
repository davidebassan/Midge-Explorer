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


class Midge:
    def __init__(self):
        self.node = rospy.init_node('Midge', anonymous=True)
        self.actuators = Move()
        self.laser = Laser()
        self.camera = Camera()
        self.exploration = Exploration()
        self.cv2_bridge = CvBridge()
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
    print((midge.exploration.get_transformed_position()))



    """
    # Exploration and Map Creation
    # Slam Approach
    while True:
        # Second approach: Random Navigation
        # Get Laser information
        laser_information = midge.retrieve_laser()

        while not midge.obstacles_near(midge.retrieve_laser().ranges):
            midge.actuators.straight()

        rotation_degree_steps = 20
        rotation_degree = 0
        direction = random.choice([-1,1])
        while midge.obstacles_near(midge.retrieve_laser().ranges):
            if rotation_degree > 180:
                break
            # Random direction of rotation
            #print(direction*rotation_degree)
            midge.actuators.rotate(direction*rotation_degree)
            rotation_degree = rotation_degree+rotation_degree_steps




    while True:
        # Second approach: Random Navigation
        # Get Laser information
        laser_information = midge.retrieve_laser()

        # Select a random degree that is > 2
        retry = 0
        bypass = False
        degree = random.randint(0, 719)


        # TODO: Controllare da 10 gradi prima a 10 gradi dopo!
        obstacles_near = False
        for i in range(degree-35, degree+35):
            if laser_information.ranges[degree] != 0 and laser_information.ranges[degree] < 2:
                obstacles_near = True

        while obstacles_near or (bypass is False and laser_information.ranges[360] < 2):
            degree = random.randint(0, 719)

            obstacles_near = False
            for i in range(degree - 15, degree + 15):
                if laser_information.ranges[degree] != 0 and laser_information.ranges[degree] < 2:
                    obstacles_near = True
                    retry += 1

            # Note:          90
            #              0   180
            #               270

            if retry > 5:
                degree = 719 # Is 180 / 4
                retry = 0
                # Do rotation and checks again

                midge.actuators.stop()
                bypass = True

            print(obstacles_near)

        midge.actuators.rotate(degree/4)
        midge.actuators.straight()
        """