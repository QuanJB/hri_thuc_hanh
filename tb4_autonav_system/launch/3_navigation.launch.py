# --------------------------------------------------------------------------
# Launch File 3 – Localization & Navigation (Nav2 + AMCL)
# Loads Nav2 with a saved map for autonomous navigation.
# Usage:  ros2 launch tb4_autonav_system 3_navigation.launch.py
#         ros2 launch tb4_autonav_system 3_navigation.launch.py map:=/absolute/path/to/map.yaml
# --------------------------------------------------------------------------

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ── Default map path (installed alongside this package) ────────────
    default_map = PathJoinSubstitution([
        FindPackageShare('tb4_autonav_system'),
        'maps',
        'my_map.yaml',
    ])

    # ── Declare arguments ──────────────────────────────────────────────
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Full path to the map .yaml file for Nav2 / AMCL',
    )

    # ── Include turtlebot4_navigation Nav2 launch ──────────────────────
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('turtlebot4_navigation'),
                'launch',
                'nav2.launch.py',
            ])
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
        }.items(),
    )

    return LaunchDescription([
        map_arg,
        nav2,
    ])

