#!/usr/bin/env python3
"""Bringup launch that includes the UR simulation MoveIt launch from ur_simulation_gz."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    ur_sim_pkg_share = get_package_share_directory('ur_simulation_gz')
    included_launch = os.path.join(ur_sim_pkg_share, 'launch', 'ur_sim_moveit.launch.py')

    include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(included_launch),
        launch_arguments={
            'ur_type': 'ur3',
            'launch_rviz': 'true',
            'use_sim_time': 'true',
        }.items(),
    )

    return LaunchDescription([include])
