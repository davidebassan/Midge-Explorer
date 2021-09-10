#!/usr/bin/python3
import rospy
from geometry_msgs.msg import Twist

class Move:
    def __init__(self):
        self.speed_linear = 1
        self.speed_angular = 1
        self.coords = Twist()
        # Initialize the node
        # rospy.init_node('Move', anonymous=False)
        # Publisher Creation
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)

    def move(self, linear=False, angular=False, speed=False):
        pass

    def rotate(self, degree, speed=40):
        """
            Execute a rotation:
            Note:    0
                270     90
                    180
            :param degree is degree of rotation
            :speed degree/second
        """
        PI = 3.14

        # Reset all
        self.coords.linear.x = 0
        self.coords.linear.y = 0
        self.coords.linear.z = 0
        self.coords.angular.x = 0
        self.coords.angular.y = 0
        self.coords.angular.z = 0

        degree = degree - 90

        # Convert all to radians
        angular_speed = speed*2*PI/360
        relative_angle = degree*2*PI/360

        if degree > 0:
            # Clockwise rotation
            self.coords.angular.z = -abs(angular_speed)
        else:
            self.coords.angular.z = abs(angular_speed)

        time_alpha = rospy.Time.now().to_sec()
        current_angle = 0
        # Perform rotation
        while current_angle < relative_angle:
            self.cmd_vel.publish(self.coords)
            time_beta = rospy.Time.now().to_sec()
            current_angle = angular_speed*(time_beta - time_alpha)
        # Force stop rotation
        self.coords.angular.z = 0
        self.cmd_vel.publish(self.coords)

    def straight(self, speed=0.5):
        # Reset all
        self.coords.linear.x = speed
        self.coords.linear.y = 0
        self.coords.linear.z = 0
        self.coords.angular.x = 0
        self.coords.angular.y = 0
        self.coords.angular.z = 0
        self.cmd_vel.publish(self.coords)

    def stop(self):
        # Reset all
        self.coords.linear.x = 0
        self.coords.linear.y = 0
        self.coords.linear.z = 0
        self.coords.angular.x = 0
        self.coords.angular.y = 0
        self.coords.angular.z = 0
        self.cmd_vel.publish(self.coords)


    def set_speed(self, speed, linear=True, angular=False):
        """
            Sets speed for angular
            :param speed integer from 0.01 to 0.99
        """
        if speed < 0.01 or speed > 0.99:
            pass
        else:
            if linear:
                self.speed_linear = speed
            if angular:
                self.speed_angular = speed