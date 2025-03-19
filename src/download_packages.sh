# Based on: https://emanual.robotis.com/docs/en/platform/turtlebot3/sbc_setup/#sbc-setup
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/ld08_driver.git

cd turtlebot3 && rm -r turtlebot3_cartographer turtlebot3_navigation2 && cd ..