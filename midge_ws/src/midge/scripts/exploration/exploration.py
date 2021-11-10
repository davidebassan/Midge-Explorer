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
        self.obstacle = None
        self.obstacle_state = None

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

    """
    def checkpoints_creation(self, occupancy_grid,n=40):
        # Idea: Dalla mappa creo i punti di interesse, quelli sonosciuti.
        # In posizione [k][0] c'è la x, in posizione [k][1] c'è la y, in posizione [k][2] c'è la z.
        #self.checkpoints = [][][]

        distance_treshold = 1 #Minimum distance between checkpoints
        


        for i in range(0, len(occupancy_grid)):
            if
    """


    def checkpoints_cleaner(self, occupancy_grid):
        pass



    def obstacle_description(self, msg):
        """
            @param msg LaserScan message
            @return dict regions that contain minimum distance for every direction
        """
        self.obstacle = {
            'right':  min(min(msg.ranges[0:143]), 10),
            'front_right': min(min(msg.ranges[144:287]), 10),
            'front':  min(min(msg.ranges[288:431]), 10),
            'front_left':  min(min(msg.ranges[432:575]), 10),
            'left':   min(min(msg.ranges[576:719]), 10),
        }

    def get_cmd_avoid_obstacle(self):
        msg = Twist()
        linear_x = 0
        angular_z = 0

        if self.obstacle['front'] > 1 and self.obstacle['front_left'] > 1 and self.obstacle['front_right'] > 1:
            self.obstacle_state = 'No obstacle found'
            linear_x = 0.6
            angular_z = 0

        elif self.obstacle['front'] < 1 and self.obstacle['front_left'] > 1 and self.obstacle['front_right'] > 1:
            self.obstacle_state = 'Found obstacle in front'
            linear_x = -0.6
            angular_z = 0

        elif self.obstacle['front'] > 1 and self.obstacle['front_left'] > 1 and self.obstacle['front_right'] < 1:
            self.obstacle_state = 'Found obstacle in front_right'
            linear_x = 0
            angular_z = 0.6

        elif self.obstacle['front'] > 1 and self.obstacle['front_left'] < 1 and self.obstacle['front_right'] > 1:
            self.obstacle_state = 'Found obstacle in front_left'
            linear_x = 0
            angular_z = -0.6

        elif self.obstacle['front'] < 1 and self.obstacle['front_left'] > 1 and self.obstacle['front_right'] < 1:
            self.obstacle_state = 'Found obstacle in front and front_right'
            linear_x = -0.6
            angular_z = 0.6

        elif self.obstacle['front'] < 1 and self.obstacle['front_left'] < 1 and self.obstacle['front_right'] > 1:
            self.obstacle_state = 'Found obstacle in front and front_left'
            linear_x = -0.6
            angular_z = -0.6

        elif self.obstacle['front'] < 1 and self.obstacle['front_left'] < 1 and self.obstacle['front_right'] < 1:
                self.obstacle_state = 'Found obstacle in front and front_left and front_right'
                linear_x = -0.6
                angular_z = 0.6

        elif self.obstacle['front'] > 1 and self.obstacle['front_left'] < 1 and self.obstacle['front_right'] < 1:
                self.obstacle_state = 'Found obstacle in front_left and front_right'
                linear_x = 0.6
                angular_z = 0

        else:
            self.obstacle_state = 'Error'
            rospy.loginfo(self.obstacle)

        rospy.loginfo(self.obstacle_state)
        msg.linear.x = linear_x
        msg.angular.z = angular_z

        return msg

    def move_avoid_obstacle(self, msg):
        self.obstacle_description(msg)
        return self.get_cmd_avoid_obstacle()