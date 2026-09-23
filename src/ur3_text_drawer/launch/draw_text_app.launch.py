#!/usr/bin/env python3
"""Launch both text_to_waypoints_node and moveit_executor_node."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()

    text_node = Node(
        package='ur3_text_drawer',
        executable='text_to_waypoints_node.py',
        name='text_to_waypoints_node',
        output='screen',
    )

    executor_node = Node(
        package='ur3_text_drawer',
        executable='moveit_executor_node.py',
        name='moveit_executor_node',
        output='screen',
        parameters=[{'text': 'Q'}],
    )

    ld.add_action(text_node)
    ld.add_action(executor_node)

    return ld
