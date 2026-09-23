cmake_minimum_required(VERSION 3.8)
project(ur3_text_drawer)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)

# Build Custom Service
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/GenerateTextTrajectory.srv"
  DEPENDENCIES geometry_msgs
)

# Cài đặt các file code Python thành node thực thi
install(PROGRAMS
  ur3_text_drawer/text_to_waypoints_node.py
  ur3_text_drawer/moveit_executor_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# Cài đặt các thư mục cần thiết
install(DIRECTORY
  launch
  config
  images
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
