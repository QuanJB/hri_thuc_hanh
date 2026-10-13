# --------------------------------------------------------------------------
# Launch File 2 – Mapping (SLAM + Teleop)
# Starts online async SLAM via the turtlebot4_navigation package and opens
# teleop_twist_keyboard in a separate xterm window for manual driving.
# Usage:  ros2 launch tb4_autonav_system 2_mapping.launch.py
# --------------------------------------------------------------------------

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ── Declare arguments ──────────────────────────────────────────────
    sync_arg = DeclareLaunchArgument(
        'sync',
        default_value='false',
        description='Use synchronous SLAM (true) or async (false, default)',
    )

    # ── Include turtlebot4_navigation SLAM launch ──────────────────────
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('turtlebot4_navigation'),
                'launch',
                'slam.launch.py',
            ])
        ),
        launch_arguments={
            'sync': LaunchConfiguration('sync'),
        }.items(),
    )

    # ── Open teleop_twist_keyboard in an xterm window ──────────────────
    teleop = ExecuteProcess(
        cmd=[
            'xterm', '-e',
            'ros2', 'run', 'teleop_twist_keyboard', 'teleop_twist_keyboard',
        ],
        name='teleop_twist_keyboard',
        output='screen',
    )

    return LaunchDescription([
        sync_arg,
        slam,
        teleop,
    ])

