cmake_minimum_required(VERSION 2.8.3)
project(led_widget)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  duckietown_msgs
)


catkin_python_setup()


catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)
