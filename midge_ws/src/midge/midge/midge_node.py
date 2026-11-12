"""Midge main node.

Driving modes, chosen on /navigation_method (std_msgs/String):
  joy   manual driving from /joy (gamepad or the web joystick); forward motion
        is stopped when an obstacle is closer than stop_distance
  auto  reactive obstacle avoidance from the lidar
  nav   Nav2 drives (goals on /goal_pose); this node stays quiet. A goal on
        /goal_pose switches to this mode, leaving it cancels the Nav2 goals
  stop  the robot stays still

Publishes:
  /cmd_vel              geometry_msgs/Twist (only in joy and auto)
  /movement_assistant   std_msgs/String, obstacle warnings when they change
  /midge/status         std_msgs/String, JSON with mode, obstacle state and distances
  /midge/pose           geometry_msgs/PoseStamped, robot pose in the map frame
"""
import json
import math

import rclpy
from action_msgs.srv import CancelGoal
from geometry_msgs.msg import PoseStamped, Twist
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import Joy, LaserScan
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener

from midge import obstacles

MODES = ('joy', 'auto', 'nav', 'stop')


class Midge(Node):

    def __init__(self):
        super().__init__('midge')
        self.declare_parameter('mode', 'joy')
        self.declare_parameter('min_distance', 1.0)
        self.declare_parameter('stop_distance', 0.5)
        self.declare_parameter('linear_speed', 0.4)
        self.declare_parameter('angular_speed', 0.8)
        self.declare_parameter('joy_linear_scale', 0.5)
        self.declare_parameter('joy_angular_scale', 1.5)
        self.declare_parameter('joy_timeout', 0.5)
        self.declare_parameter('rate', 10.0)

        self.mode = self.get_parameter('mode').value
        if self.mode not in MODES:
            self.mode = 'stop'

        self.scan = None
        self.scan_time = None
        self.joy_cmd = (0.0, 0.0)
        self.joy_time = None
        self.state = obstacles.CLEAR
        self.regions = None
        self.turn_sign = 0
        self.turn_around_until = None
        self.last_warning = None

        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.assistant_pub = self.create_publisher(String, 'movement_assistant', 10)
        self.status_pub = self.create_publisher(String, 'midge/status', 10)
        self.pose_pub = self.create_publisher(PoseStamped, 'midge/pose', 10)

        self.create_subscription(LaserScan, 'scan', self.on_scan, qos_profile_sensor_data)
        self.create_subscription(Joy, 'joy', self.on_joy, 10)
        self.create_subscription(String, 'navigation_method', self.on_mode, 10)
        self.create_subscription(PoseStamped, 'goal_pose', self.on_goal, 10)

        self.cancel_nav = self.create_client(CancelGoal, 'navigate_to_pose/_action/cancel_goal')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_timer(1.0 / self.get_parameter('rate').value, self.step)
        self.create_timer(0.5, self.publish_status)
        self.create_timer(0.2, self.publish_pose)
        self.get_logger().info(f'Midge ready, mode: {self.mode}')

    # Inputs

    def on_scan(self, msg):
        self.scan = msg
        self.scan_time = self.get_clock().now()

    def on_joy(self, msg):
        if len(msg.axes) < 2:
            return
        linear = self.get_parameter('joy_linear_scale').value * msg.axes[1]
        angular = self.get_parameter('joy_angular_scale').value * msg.axes[0]
        self.joy_cmd = (linear, angular)
        self.joy_time = self.get_clock().now()

    def on_mode(self, msg):
        mode = msg.data.strip().lower()
        if mode not in MODES:
            self.get_logger().warn(f'Unknown navigation method "{msg.data}", expected {MODES}')
            return
        self.set_mode(mode)

    def on_goal(self, msg):
        # A goal for Nav2 (web map or RViz "2D Goal Pose") hands driving over to Nav2
        if self.mode != 'nav':
            self.get_logger().info('Nav2 goal received')
            self.set_mode('nav')

    def set_mode(self, mode):
        if mode == self.mode:
            return
        if self.mode == 'nav':
            self.cancel_nav_goals()
        self.get_logger().info(f'Navigation method: {self.mode} -> {mode}')
        self.mode = mode
        self.turn_sign = 0
        self.turn_around_until = None
        self.publish_cmd(0.0, 0.0)

    # Control loop

    def step(self):
        self.update_obstacles()
        if self.mode == 'joy':
            self.step_joy()
        elif self.mode == 'auto':
            self.step_auto()

    def update_obstacles(self):
        if not self.fresh(self.scan_time, 1.0):
            self.regions = None
            return
        self.regions = obstacles.sector_distances(
            self.scan.ranges, self.scan.angle_min, self.scan.angle_increment)
        self.state = obstacles.classify(self.regions, self.get_parameter('min_distance').value)
        self.warn(self.state)

    def step_joy(self):
        if not self.fresh(self.joy_time, self.get_parameter('joy_timeout').value):
            self.joy_cmd = (0.0, 0.0)
        linear, angular = self.joy_cmd
        if linear > 0.0 and self.front_distance() < self.get_parameter('stop_distance').value:
            linear = 0.0
        self.publish_cmd(linear, angular)

    def step_auto(self):
        if self.regions is None:
            self.publish_cmd(0.0, 0.0)  # no lidar data: do not drive blind
            return
        speed = self.get_parameter('linear_speed').value
        turn = self.get_parameter('angular_speed').value
        now = self.get_clock().now()

        # Turning around (half a turn) after being blocked on every side
        if self.turn_around_until is not None:
            if now < self.turn_around_until:
                self.publish_cmd(0.0, self.turn_sign * turn)
                return
            self.turn_around_until = None
            self.turn_sign = 0

        if self.state == obstacles.BLOCKED:
            _, _, self.turn_sign = obstacles.avoidance_command(
                self.state, self.regions, speed, turn, self.turn_sign)
            self.turn_around_until = now + Duration(seconds=math.pi / turn)
            self.publish_cmd(0.0, self.turn_sign * turn)
            return

        linear, angular, self.turn_sign = obstacles.avoidance_command(
            self.state, self.regions, speed, turn, self.turn_sign)
        self.publish_cmd(linear, angular)

    # Helpers

    def fresh(self, stamp, max_age):
        return stamp is not None and \
            (self.get_clock().now() - stamp) < Duration(seconds=max_age)

    def front_distance(self):
        return self.regions['front'] if self.regions else math.inf

    def publish_cmd(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.cmd_pub.publish(msg)

    def warn(self, state):
        if state == self.last_warning:
            return
        self.last_warning = state
        self.assistant_pub.publish(String(data=state))

    def cancel_nav_goals(self):
        if self.cancel_nav.service_is_ready():
            # Empty request (zero goal id and stamp) cancels every goal
            self.cancel_nav.call_async(CancelGoal.Request())
            self.publish_cmd(0.0, 0.0)

    def publish_status(self):
        status = {
            'mode': self.mode,
            'obstacle': self.state if self.regions else 'No lidar data',
            'regions': {k: round(v, 2) for k, v in (self.regions or {}).items()},
        }
        self.status_pub.publish(String(data=json.dumps(status)))

    def publish_pose(self):
        try:
            t = self.tf_buffer.lookup_transform('map', 'base_footprint', Time())
        except TransformException:
            return
        pose = PoseStamped()
        pose.header = t.header
        pose.pose.position.x = t.transform.translation.x
        pose.pose.position.y = t.transform.translation.y
        pose.pose.position.z = t.transform.translation.z
        pose.pose.orientation = t.transform.rotation
        self.pose_pub.publish(pose)


def main():
    rclpy.init()
    node = Midge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.publish_cmd(0.0, 0.0)
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
