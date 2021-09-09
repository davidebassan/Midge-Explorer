#!/usr/bin/python3
import rospy
from geometry_msgs.msg import Twist
from utils.Coordinates import Coordinates

class Move:

    def __init__(self, speed, cords):
        self.speed = speed
        self.angular = Coordinates(cords.angular)
        self.linear = Coordinates(cords.linear)
        # Initialize the node
        rospy.init_node('Move', anonymous=False)
        # Publisher Creation
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        # Set telling ratio
        r = rospy.Rate(15) #15 Hz

    def move(self, linear=False, angular=False, speed=False):
        if speed:
            self.speed = speed
        if linear:
            self.linear = Coordinates(linear)
        if angular:
            self.angular = Coordinates(angular)

        move_cmd = Twist()
        move_cmd.linear = self.linear*self.speed
        move_cmd.angular = self.angular*self.speed
        self.cmd_vel.publish(move_cmd)
