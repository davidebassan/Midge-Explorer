"""Web app: rosbridge (websocket), web_video_server (camera stream) and a static file server.

    ros2 launch midge_web web.launch.py
Then open http://localhost:8000
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    www = os.path.join(get_package_share_directory('midge_web'), 'www')
    rosbridge = get_package_share_directory('rosbridge_server')

    return LaunchDescription([
        DeclareLaunchArgument('http_port', default_value='8000'),
        DeclareLaunchArgument('websocket_port', default_value='9090'),
        DeclareLaunchArgument('video_port', default_value='8080'),

        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                os.path.join(rosbridge, 'launch', 'rosbridge_websocket_launch.xml')),
            launch_arguments={'port': LaunchConfiguration('websocket_port')}.items()),

        Node(package='web_video_server', executable='web_video_server',
             parameters=[{'port': ParameterValue(LaunchConfiguration('video_port'), value_type=int)}]),

        ExecuteProcess(
            cmd=['python3', '-m', 'http.server', LaunchConfiguration('http_port'),
                 '--directory', www],
            name='web_server', output='screen'),
    ])
