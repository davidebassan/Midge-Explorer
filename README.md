# Midge Explorer

***Thesis*** · a differential drive robot with a lidar and a camera that maps its
surroundings, avoids obstacles on its own and can be driven from a web app.

Version 2 runs on **ROS 2 Jazzy** with **Gazebo Harmonic**, **slam_toolbox** and **Nav2**.
The original ROS 1 version (gmapping, move_base, Gazebo Classic) is in the git history
before the `ros2-migration` branch.

## Packages

| Package | Contents |
| --- | --- |
| `midge_bringup` | Robot model (xacro), `house` and `empty` worlds, SLAM / Nav2 / bridge configuration, RViz config, `sim.launch.py` |
| `midge` | The `midge` node: joystick driving with obstacle protection and reactive obstacle avoidance |
| `midge_web` | Web app (camera, live map, Nav2 goals, joystick) with rosbridge and web_video_server |

## Run it with Docker (Linux, macOS, Windows)

Requires Docker. Everything else is in the image.

```
docker compose up --build
```

Then open:

- **http://localhost:6080/vnc.html?autoconnect=1&resize=scale** · desktop with Gazebo and RViz
- **http://localhost:8000** · web app

The first build of the image takes a while (about 4 GB). The workspace is mounted from
`midge_ws/`, so code changes only need a restart of the container
(`docker compose restart`). A shell in the running simulation:

```
docker exec -it midge bash
source /midge_ws/install/setup.bash
```

Gazebo and RViz use software rendering inside the container, so expect a real-time
factor below 1 on slower machines.

## Run it on Ubuntu 24.04 without Docker

```
sudo apt install ros-jazzy-ros-gz ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox ros-jazzy-xacro ros-jazzy-rosbridge-suite \
  ros-jazzy-web-video-server ros-jazzy-joy
cd midge_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch midge_bringup sim.launch.py
```

## Launch options

```
ros2 launch midge_bringup sim.launch.py world:=empty.sdf gui:=false rviz:=false joy:=true
```

| Argument | Default | |
| --- | --- | --- |
| `world` | `house.sdf` | World in `midge_bringup/worlds` |
| `gui` | `true` | Gazebo GUI |
| `rviz` | `true` | RViz2 |
| `nav` | `true` | Nav2 |
| `web` | `true` | Web app, rosbridge, camera stream |
| `explorer` | `true` | `midge` node |
| `joy` | `false` | Physical gamepad on `/dev/input/js0` |
| `x`, `y`, `yaw` | `0` | Spawn pose |

## Driving modes

Pick a mode in the web app, or publish it:

```
ros2 topic pub --once /navigation_method std_msgs/msg/String "{data: auto}"
```

| Mode | Behaviour |
| --- | --- |
| `joy` (default) | Manual driving from `/joy` (gamepad or web joystick). Forward motion stops when an obstacle is closer than `stop_distance`. |
| `auto` | Reactive obstacle avoidance from the lidar. When boxed in it turns around. |
| `nav` | Nav2 drives. Click on the map in the web app, or use *2D Goal Pose* in RViz: a goal switches to this mode by itself, and leaving it cancels the goal. |
| `stop` | The robot stays still. |

`midge` node parameters: `mode`, `min_distance` (1.0 m), `stop_distance` (0.5 m),
`linear_speed` (0.4 m/s), `angular_speed` (0.8 rad/s), `joy_linear_scale`,
`joy_angular_scale`, `joy_timeout`, `rate`.

## Topics

| Topic | Type | |
| --- | --- | --- |
| `/scan` | `sensor_msgs/LaserScan` | Hokuyo, 180°, 720 samples |
| `/camera/rgb/image_raw` | `sensor_msgs/Image` | Front camera |
| `/cmd_vel` | `geometry_msgs/Twist` | Velocity command |
| `/map` | `nav_msgs/OccupancyGrid` | slam_toolbox map |
| `/navigation_method` | `std_msgs/String` | Driving mode |
| `/movement_assistant` | `std_msgs/String` | Obstacle warnings |
| `/midge/status` | `std_msgs/String` | JSON: mode, obstacle state, distances |
| `/midge/pose` | `geometry_msgs/PoseStamped` | Robot pose in `map` |

## Tests

```
cd midge_ws
colcon test --packages-select midge && colcon test-result --verbose
```
