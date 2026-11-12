# ROS 2 Jazzy + Gazebo Harmonic + Nav2 + slam_toolbox, with a virtual desktop
# reachable from the browser (noVNC) so it also runs on macOS / Apple Silicon.
FROM ros:jazzy

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-jazzy-ros-gz \
      ros-jazzy-navigation2 \
      ros-jazzy-nav2-bringup \
      ros-jazzy-slam-toolbox \
      ros-jazzy-robot-state-publisher \
      ros-jazzy-joint-state-publisher \
      ros-jazzy-xacro \
      ros-jazzy-rviz2 \
      ros-jazzy-rosbridge-suite \
      ros-jazzy-web-video-server \
      ros-jazzy-joy \
      python3-colcon-common-extensions \
      xvfb x11vnc fluxbox novnc websockify xterm \
      mesa-utils libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# Software OpenGL (no GPU inside Docker on macOS)
ENV DISPLAY=:1 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    QT_X11_NO_MITSHM=1

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /midge_ws
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
