#!/bin/bash
source /opt/ros/$ROS_DISTRO/setup.bash
source $ROS2_WS/install/local_setup.bash
export TURTLEBOT3_MODEL=burger

# Start jupyterlab (for remote access over browser)
#export JUPYTER_ENABLE_LAB=yes
#export JUPYTER_TOKEN=docker
#jupyter-lab --ip 0.0.0.0 -IdentityProvider.token='ros_ml_container' --no-browser --allow-root &

exec "$@"