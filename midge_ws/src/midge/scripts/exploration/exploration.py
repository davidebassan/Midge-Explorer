#!/usr/bin/python3
import rospy
import tf
from geometry_msgs.msg import Twist
from nav_msgs.msg import OccupancyGrid

class Exploration:
    def __init__(self):
        # Subscriber Creation
        # self.subscriber = rospy.Subsriber('map', Twist, queue_size=10)
        self.topic = '/map'
        self.map = None
        self.heatmap = None
        self.listener = tf.TransformListener()

    def get_map(self):
        self.map = rospy.wait_for_message(self.topic, OccupancyGrid)
        print(dir(self.map))
        return self.map.data

    def get_position_in_map(self, x, y):
        map_x = int(x - map.info.origin.position.x) / map.info.resolution
        map_y = int(y - map.info.origin.position.y) / map.info.resolution
        current_point = self.map.data

    def get_transformed_position(self):
        try:
            (trans, rot) = self.listener.lookupTransform('/robot_footprint', '', rospy.Time(0))
            return trans, rot
        except Exception as e:
            return e

    def get_heatmap(self):
        pass
