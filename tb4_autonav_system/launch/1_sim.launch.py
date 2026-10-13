# --------------------------------------------------------------------------
# Launch File 1 – Simulation
# Brings up the TurtleBot 4 in an Ignition Gazebo world with RViz.
# Usage:  ros2 launch tb4_autonav_system 1_sim.launch.py
#         ros2 launch tb4_autonav_system 1_sim.launch.py world:=depot
# --------------------------------------------------------------------------

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ── Declare arguments ──────────────────────────────────────────────
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='warehouse',
        description='Ignition Gazebo world to load (e.g. warehouse, depot, maze)',
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Whether to launch RViz alongside the simulation',
    )

    # ── Include the official TurtleBot 4 Ignition launch ───────────────
    turtlebot4_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('turtlebot4_ignition_bringup'),
                'launch',
                'turtlebot4_ignition.launch.py',
            ])
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'rviz':  LaunchConfiguration('rviz'),
        }.items(),
    )

    return LaunchDescription([
        world_arg,
        rviz_arg,
        turtlebot4_sim,
    ])

