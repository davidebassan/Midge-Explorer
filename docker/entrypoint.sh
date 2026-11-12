#!/bin/bash
# Starts a virtual desktop (Xvfb + fluxbox) shared over noVNC on port 6080,
# builds the workspace and runs the given command.
set -e
source /opt/ros/jazzy/setup.bash

if [ "${HEADLESS:-0}" != "1" ]; then
  Xvfb :1 -screen 0 "${SCREEN:-1600x900x24}" >/tmp/xvfb.log 2>&1 &
  sleep 1
  fluxbox >/tmp/fluxbox.log 2>&1 &
  x11vnc -display :1 -forever -shared -nopw -quiet -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
  websockify --web /usr/share/novnc 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
  echo "Desktop: http://localhost:6080/vnc.html?autoconnect=1&resize=scale"
fi

cd /midge_ws
if [ "${BUILD:-1}" = "1" ] || [ ! -f install/setup.bash ]; then
  colcon build --symlink-install
fi
source install/setup.bash

exec "$@"
