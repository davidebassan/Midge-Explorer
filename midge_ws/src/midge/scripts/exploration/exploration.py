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
        self.current_point = None
        self.checkpoints = None

    def get_map(self):
        self.map = rospy.wait_for_message(self.topic, OccupancyGrid)

        return self.map.data

    def get_position_in_map(self, x, y):
        # TODO: Test sull'orientamento?
        self.get_map()
        grid_x = int(x - self.map.info.origin.position.x) / self.map.info.resolution
        grid_y = int(y - self.map.info.origin.position.y) / self.map.info.resolution
        self.current_point = int(grid_y * self.map.info.width + grid_x)
        return self.current_point

    def read_map(self, index):
        return self.map.data[index]

    def get_transformed_position(self):
        try:
            self.listener.waitForTransform('/map', '/robot_footprint', rospy.Time(), rospy.Duration(4.0))
            trans, rot = self.listener.lookupTransform('/map', '/robot_footprint', rospy.Time(0))
            return trans, rot
        except Exception as e:
            return None

    def angle_to_goal(self, rot):
        return tf.transformations.euler_from_quaternion(rot)

    def checkpoints_creation(self, trans, rot,  n=40):
        # Idea: Dalla mappa creo i punti di interesse, quelli sonosciuti.
        # In posizione [k][0] c'è la x, in posizione [k][1] c'è la y, in posizione [k][2] c'è la z.
        #self.checkpoints = [][]

        # Random area generation point
        # Da fare SOLO al setup all'entrata dell'area.
        # Quello che voglio fare è creare dei checkpoint per una grandezza definita.

        # Getting orientation
        yaw = self.angle_to_goal(rot)[2]
        print(yaw)
        # Getting now x and y
        x = trans[0]
        y = trans[1]










