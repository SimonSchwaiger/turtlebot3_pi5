# ROS 2 Turtlebot3 Docker Setup for Raspberry Pi 5

This repository contains a Docker-based setup for running ROS 2 Humble and Turtlebot3 on a Raspberry Pi 5. It includes:

- Docker configuration for ROS 2 Humble and Turtlebot3 drivers
- Web-based teleoperation using touch-controls
- Discovery server for experimenting with ROS 2 networking

At the time of writing, Turtlebot3 hardware is only supported up to ROS 2 Humble. However, I only had a Pi 5 in hand, which requires at least Ubuntu 24.04. Therefore, everything is containerised.ROS2 installation.

## Setup

0. Install Ubuntu Server 24.04 for Rasperry Pi using Raspberry Pi Imager: https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi#4-boot-ubuntu-server
1. Set timezone: https://askubuntu.com/questions/1528949/time-setting-problems-with-ubuntu-24-04
2. Ensure SSH and internet access and update the Pi's OS: `sudo apt update && sudo apt upgrade -y`
3. Install Docker: https://docs.docker.com/engine/install/ubuntu/
4. Add user to *docker* group: `sudo usermod -aG docker $USER` and reboot
5. Download packages by running `bash download_packages.sh` in *src*
6. Configure `LDS_MODEL` and `ROS_DOMAIN_ID` to your model as indicated in: https://emanual.robotis.com/docs/en/platform/turtlebot3/sbc_setup/#sbc-setup
7. Build Docker image (this will take a while): `docker build -t turtlebot3_pi5 .`
8. `docker run -it --rm --net=host -v /dev:/dev -v $PWD/src:/opt/ros2_ws/src --privileged turtlebot3_pi5:latest bash`

## Wifi connection

1. Ensure that wifi interface is present: `ip link show`
2. Edit Connection configuration: `sudo nano /etc/netplan/50-cloud-init.yaml`
    ```yaml
    network:
        version: 2
        ethernets:
            ...
        wifis:
            wlan0:
            dhcp4: true
            optional: true
            access-points:
                "Your_SSID":
                password: "Your_WiFi_Password"
    ```
3. Apply changes: `sudo netplan apply`
4. Confirm wifi connection: `ip a`

## Teleop

1. Webserver is started at robot_ip:8550 for teleoperation
2. To be served to other members in the network, this port needs to be whitelisted in the firewall: `sudo ufw allow 8550/tcp`
3. Due to current limitations in flet (used UI toolkit), an internet connection is required for initial setup of new clients
    * *Flet currently needs an internet connection to install client-side librarys (if not cached on client device)*
        Issue trackers for self-hosting and offline-only
    * Workaround for self-hosting: https://github.com/TomBursch/kitchenowl/pull/36
    * Tracker for offline use: https://github.com/flutter/flutter/issues/60069#issuecomment-1152340236

## Dev Container

I use my [ROS ML Container (link)](https://github.com/SimonSchwaiger/ros-ml-container) for remote development and connection to ROS. The following command configures it for this project.

`SKIP_COMPILE=false DOCKER_RUN_ARGS="--net host --privileged -v /dev:/dev --ipc=host -v /dev/shm:/dev/shm" ROS_DISTRO=humble bash buildandrun.sh`