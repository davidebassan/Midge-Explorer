#!/usr/bin/python

import rospy
import tf
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan


class Tf_listener:
    """
        Handle with odom position
    """
    def __init__(self):
        self.topic = '/tf'
        self.max_lidar_range = 30
        self.rate = rospy.Rate(1.0)
        self.translation = 0
        self.rotation = 0
        self.listener = tf.TransformListener()

    def get_transform(self):
        """
            @return arrays translation, rotation
        """
        self.listener.waitForTransform('/map', '/robot_footprint', rospy.Time(),rospy.Duration(4.0))
        self.translation, self.rotation = self.listener.lookupTransform('/map', '/robot_footprint', rospy.Time(0))
        return self.translation, self.rotation