#!/usr/bin/python3
import rospy
from geometry_msgs.msg import Twist
from utils.Coordinates import Coordinates

class Move:

    def __init__(self):
        self.speed_linear = 1
        self.speed_angular = 1
        self.angular = Coordinates()
        self.linear = Coordinates()
        # Initialize the node
        """
        rospy.init_node('Move', anonymous=False)
        # Publisher Creation
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        # Set telling ratio
        r = rospy.Rate(10) #15 Hz
        """
    def move(self, linear=False, angular=False, speed=False):
        if linear:
            self.linear = Coordinates(linear)
        if angular:
            self.angular = Coordinates(angular)

        move_cmd = Twist()
        move_cmd.linear = self.linear*self.speed
        move_cmd.angular = self.angular*self.speed
        self.cmd_vel.publish(move_cmd)

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