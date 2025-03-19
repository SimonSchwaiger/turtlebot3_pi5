# docker build -t turtlebot3_pi5 .
## Local: docker run -it --rm --net=host -v /dev:/dev -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $PWD/src:/opt/ros2_ws/src --privileged turtlebot3_pi5:latest bash
## Headless: docker run -it --rm --net=host -v /dev:/dev -v $PWD/src:/opt/ros2_ws/src --privileged turtlebot3_pi5:latest bash

ARG ROS_DISTRO=humble

FROM ros:${ROS_DISTRO}-ros-base

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

ENV ROS2_WS=/opt/ros2_ws
ENV TURTLEBOT3_MODEL=burger
ENV LDS_MODEL=LDS-01
ENV OPENCR_MODEL=${TURTLEBOT3_MODEL}
ENV OPENCR_PORT=/dev/ttyACM0

RUN apt-get update && apt-get upgrade -y

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-argcomplete python3-colcon-common-extensions libboost-system-dev build-essential

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-hls-lfcd-lds-driver \
    ros-${ROS_DISTRO}-turtlebot3-msgs \
    ros-${ROS_DISTRO}-dynamixel-sdk \
    libudev-dev

## Teleop
RUN apt-get install -y --no-install-recommends \
    ros-$ROS_DISTRO-teleop-twist-joy ros-$ROS_DISTRO-joy ros-$ROS_DISTRO-key-teleop

## Add required packages for opencr flash
RUN dpkg --add-architecture armhf  
RUN apt-get update 
RUN apt-get install -y --no-install-recommends libc6:armhf
# Install usbutils for device debugging
RUN apt-get install -y --no-install-recommends usbutils

## BUILD WORKSPACE
# Copy ROS packages for compilation in container
COPY ./src $ROS2_WS/src

# Install ros dependencies
RUN apt-get update && rosdep update && rosdep install --from-paths $ROS2_WS/src -i -y --rosdistro $ROS_DISTRO

# Compile workspace
RUN /bin/bash -c "source /opt/ros/$ROS_DISTRO/setup.bash \
    && cd $ROS2_WS \
    && colcon build --symlink-install"

# Remove src folder used for compilation, since the real src folder will be mounted at runtime
RUN rm -rf $ROS2_WS/src

# Cleanup
RUN rm -rf /var/lib/apt/lists/*

# Add ROS and venv sourcing to bashrc for interactive debugging
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> ~/.bashrc
RUN echo "source $ROS2_WS/install/local_setup.bash" >> ~/.bashrc

#TB3 Config
RUN echo "export TURTLEBOT3_MODEL=$TURTLEBOT3_MODEL" >> ~/.bashrc
RUN echo "export LDS_MODEL=$LDS_MODEL" >> ~/.bashrc
RUN echo "export ROS_DOMAIN_ID=30 #TURTLEBOT3" >> ~/.bashrc

# Set shell env variable for jupyterlab (this fixes autocompletion in web-based shell)
ENV SHELL=/bin/bash

# Add entrypoint
ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
