# --------------------------------------------------------------------------
# Launch File 4 – Autonomous Navigation + YOLO Detection
# Khởi chạy Node điều hướng tự động qua các waypoints và Node nhận diện
# vật thể bằng YOLO từ camera TurtleBot 4.
#
# Trước khi chạy file này, hãy đảm bảo:
#   1. Simulation đang chạy  (1_sim.launch.py)
#   2. Nav2 + Localization đang chạy  (3_navigation.launch.py)
#   3. Đã set Initial Pose trên RViz2
#
# Usage:  ros2 launch tb4_autonav_system 4_autonav_yolo.launch.py
# --------------------------------------------------------------------------

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ── Declare arguments ──────────────────────────────────────────────
    model_arg = DeclareLaunchArgument(
        'yolo_model',
        default_value='yolov8n.pt',
        description='Tên hoặc đường dẫn mô hình YOLO (vd: yolov8n.pt, yolov8s.pt)',
    )

    confidence_arg = DeclareLaunchArgument(
        'confidence',
        default_value='0.5',
        description='Ngưỡng độ tin cậy tối thiểu cho YOLO',
    )

    camera_topic_arg = DeclareLaunchArgument(
        'camera_topic',
        default_value='/oakd/rgb/preview/image_raw',
        description='Topic hình ảnh từ camera TurtleBot 4',
    )

    display_arg = DeclareLaunchArgument(
        'display_window',
        default_value='true',
        description='Hiển thị cửa sổ OpenCV với kết quả YOLO',
    )

    # ── YOLO Detector Node ─────────────────────────────────────────────
    yolo_node = Node(
        package='tb4_autonav_system',
        executable='yolo_detector',
        name='yolo_detector',
        output='screen',
        parameters=[{
            'model': LaunchConfiguration('yolo_model'),
            'confidence_threshold': LaunchConfiguration('confidence'),
            'camera_topic': LaunchConfiguration('camera_topic'),
            'display_window': LaunchConfiguration('display_window'),
        }],
    )

    # ── Auto Navigator Node ───────────────────────────────────────────
    # Delay 5 giây để đảm bảo YOLO đã sẵn sàng trước khi robot bắt đầu
    # di chuyển (tùy chọn, có thể bỏ TimerAction nếu không cần).
    auto_nav_node = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='tb4_autonav_system',
                executable='auto_navigator',
                name='auto_navigator',
                output='screen',
            ),
        ],
    )

    return LaunchDescription([
        model_arg,
        confidence_arg,
        camera_topic_arg,
        display_arg,
        yolo_node,
        auto_nav_node,
    ])

