#!/usr/bin/python3
import rospy
import tf
import random
from std_msgs.msg import String


class Web:
    def __init__(self):
        # Subscriber Creation
        self.navigation_method = None
        self.topic = '/navigation_method'
        self.subscriber = rospy.Subscriber(self.topic, String, self.update_navigation_method)

    def update_navigation_method(self, data):
        self.navigation_method = data.data

    def get_navigation_method(self):
        return self.navigation_method