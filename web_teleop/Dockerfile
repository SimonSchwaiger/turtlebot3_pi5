ARG ROS_DISTRO=humble

FROM ros:${ROS_DISTRO}-ros-base

RUN apt-get update 

RUN apt-get install -y --no-install-recommends \
    python3 python3-pip \
    ros-humble-rosbridge-suite

COPY requirements.txt .
RUN pip install -r requirements.txt

