#!/usr/bin/python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan

class Laser:

    def __init__(self):
        # Initialize the node
        self.node = rospy.init_node('Laser_Scan', anonymous=True)
        self.laser_info = None
        self.ratio = 40
        self.topic = '/scan'
        # Subscriber Creation
        rospy.Rate(self.ratio)
        self.subscriber = rospy.Subscriber(self.topic, LaserScan, self.callback)
        rospy.spin()
        # Set telling ratio

    def callback(self, msg):
        self.laser_info = msg

    def get_laser_info(self):
        return self.laser_info

    def stop(self):
        self.subscriber.unregister()