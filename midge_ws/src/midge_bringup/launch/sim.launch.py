"""Midge in Gazebo Harmonic with SLAM (slam_toolbox), Nav2, the explorer node and the web app.

    ros2 launch midge_bringup sim.launch.py
    ros2 launch midge_bringup sim.launch.py world:=empty.sdf gui:=false rviz:=false
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, TimerAction)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import (AnyLaunchDescriptionSource,
                                               PythonLaunchDescriptionSource)
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('midge_bringup')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    slam_toolbox = get_package_share_directory('slam_toolbox')
    midge_web = get_package_share_directory('midge_web')

    world = LaunchConfiguration('world')
    gui = LaunchConfiguration('gui')
    sim_time = {'use_sim_time': True}
    nav2_params = os.path.join(pkg, 'config', 'nav2.yaml')

    args = [
        DeclareLaunchArgument('world', default_value='house.sdf',
                              description='World file in midge_bringup/worlds'),
        DeclareLaunchArgument('gui', default_value='true', description='Gazebo GUI'),
        DeclareLaunchArgument('rviz', default_value='true', description='Start RViz2'),
        DeclareLaunchArgument('nav', default_value='true', description='Start Nav2'),
        DeclareLaunchArgument('web', default_value='true', description='Start the web app'),
        DeclareLaunchArgument('explorer', default_value='true',
                              description='Start the midge node (joystick / obstacle avoidance)'),
        DeclareLaunchArgument('joy', default_value='false',
                              description='Read a physical gamepad (/dev/input/js0)'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
    ]

    # Lets Gazebo resolve package://midge_bringup/... meshes
    resource_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', os.path.dirname(pkg))

    robot_description = ParameterValue(
        Command(['xacro ', os.path.join(pkg, 'urdf', 'midge.urdf.xacro')]), value_type=str)

    robot_state_publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}, sim_time],
        output='screen')

    gazebo_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': ['-r ', PathJoinSubstitution([pkg, 'worlds', world])],
            'on_exit_shutdown': 'true'}.items(),
        condition=IfCondition(gui))

    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': ['-r -s ', PathJoinSubstitution([pkg, 'worlds', world])],
            'on_exit_shutdown': 'true'}.items(),
        condition=UnlessCondition(gui))

    spawn = Node(
        package='ros_gz_sim', executable='create',
        arguments=['-topic', 'robot_description', '-name', 'midge',
                   '-x', LaunchConfiguration('x'), '-y', LaunchConfiguration('y'),
                   '-z', '0.02', '-Y', LaunchConfiguration('yaw')],
        output='screen')

    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        parameters=[{'config_file': os.path.join(pkg, 'config', 'bridge.yaml')}, sim_time],
        output='screen')

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_toolbox, 'launch', 'online_async_launch.py')),
        launch_arguments={
            'slam_params_file': os.path.join(pkg, 'config', 'slam.yaml'),
            'use_sim_time': 'true'}.items())

    # Nav2 nodes, driven straight to /cmd_vel (no velocity smoother / collision monitor)
    nav2_nodes = [
        Node(package=package, executable=executable, name=name,
             parameters=[nav2_params], output='screen')
        for package, executable, name in [
            ('nav2_controller', 'controller_server', 'controller_server'),
            ('nav2_planner', 'planner_server', 'planner_server'),
            ('nav2_behaviors', 'behavior_server', 'behavior_server'),
            ('nav2_bt_navigator', 'bt_navigator', 'bt_navigator'),
            ('nav2_lifecycle_manager', 'lifecycle_manager', 'lifecycle_manager_navigation'),
        ]
    ]
    # Give gazebo and slam_toolbox time to publish /map and the map->odom transform
    nav2 = TimerAction(period=8.0, actions=nav2_nodes,
                       condition=IfCondition(LaunchConfiguration('nav')))

    explorer = Node(
        package='midge', executable='midge',
        parameters=[sim_time],
        output='screen',
        condition=IfCondition(LaunchConfiguration('explorer')))

    joy = Node(
        package='joy', executable='joy_node',
        parameters=[{'device_id': 0, 'deadzone': 0.12}],
        condition=IfCondition(LaunchConfiguration('joy')))

    web = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(os.path.join(midge_web, 'launch', 'web.launch.py')),
        condition=IfCondition(LaunchConfiguration('web')))

    rviz = Node(
        package='rviz2', executable='rviz2',
        arguments=['-d', os.path.join(pkg, 'rviz', 'midge.rviz')],
        parameters=[sim_time],
        condition=IfCondition(LaunchConfiguration('rviz')))

    return LaunchDescription(args + [
        resource_path, robot_state_publisher, gazebo_gui, gazebo_server, spawn, bridge,
        slam, nav2, explorer, joy, web, rviz,
    ])
