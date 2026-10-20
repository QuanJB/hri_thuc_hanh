#!/usr/bin/env python3
# --------------------------------------------------------------------------
# auto_navigator.py – Điều hướng tự động qua nhiều điểm mục tiêu bằng Nav2
#
# Sử dụng nav2_simple_commander để gửi robot tuần tự qua các waypoints.
# Các tọa độ mục tiêu (x, y, yaw) được khai báo trong danh sách WAYPOINTS.
#
# Usage:  ros2 run tb4_autonav_system auto_navigator
# --------------------------------------------------------------------------

import math
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


# ═══════════════════════════════════════════════════════════════════════════
# CẤU HÌNH CÁC ĐIỂM MỤC TIÊU (x, y, yaw_degrees)
# Sinh viên thay đổi tọa độ này sau khi khảo sát bản đồ trên RViz2.
# Sử dụng "Publish Point" trên RViz2 hoặc:
#   ros2 topic echo /clicked_point
#   ros2 topic echo /amcl_pose
# ═══════════════════════════════════════════════════════════════════════════
WAYPOINTS = [
    # (x,     y,     yaw_degrees)
    ( 1.0,   0.5,    0.0),    # Goal 1
    ( 2.0,  -1.0,   90.0),    # Goal 2
    (-0.5,   1.5,  180.0),    # Goal 3
]


def yaw_to_quaternion(yaw_deg: float):
    """Chuyển đổi góc yaw (độ) sang quaternion (chỉ quay quanh trục Z)."""
    yaw_rad = math.radians(yaw_deg)
    qz = math.sin(yaw_rad / 2.0)
    qw = math.cos(yaw_rad / 2.0)
    return (0.0, 0.0, qz, qw)


def create_pose(navigator: BasicNavigator, x: float, y: float, yaw_deg: float) -> PoseStamped:
    """Tạo PoseStamped trong frame 'map'."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0
    _, _, qz, qw = yaw_to_quaternion(yaw_deg)
    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = qz
    pose.pose.orientation.w = qw
    return pose


def main():
    rclpy.init()
    navigator = BasicNavigator()

    # ── Đợi Nav2 sẵn sàng ──────────────────────────────────────────────
    navigator.get_logger().info('⏳ Đang đợi Nav2 khởi động...')
    navigator.waitUntilNav2Active()
    navigator.get_logger().info('✅ Nav2 đã sẵn sàng!')

    # ── Duyệt qua từng waypoint ────────────────────────────────────────
    for i, (x, y, yaw) in enumerate(WAYPOINTS, start=1):
        goal_pose = create_pose(navigator, x, y, yaw)

        navigator.get_logger().info(
            f'🚀 Đang di chuyển đến Goal {i}/{len(WAYPOINTS)}: '
            f'x={x:.2f}, y={y:.2f}, yaw={yaw:.1f}°'
        )

        navigator.goToPose(goal_pose)

        # Đợi cho đến khi hoàn thành hoặc thất bại
        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback:
                # Hiển thị thời gian ước tính còn lại
                eta = Duration.from_msg(feedback.estimated_time_remaining)
                if eta.nanoseconds > 0:
                    navigator.get_logger().info(
                        f'   📍 Goal {i} – ETA: {eta.nanoseconds / 1e9:.1f}s',
                        throttle_duration_sec=2.0,
                    )

        # ── Kiểm tra kết quả ───────────────────────────────────────────
        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            navigator.get_logger().info(f'✅ Goal {i} – Đã đến nơi thành công!')
        elif result == TaskResult.CANCELED:
            navigator.get_logger().warn(f'⚠️  Goal {i} – Bị hủy.')
        elif result == TaskResult.FAILED:
            navigator.get_logger().error(f'❌ Goal {i} – Thất bại! Chuyển sang goal tiếp theo.')
        else:
            navigator.get_logger().error(f'❌ Goal {i} – Trạng thái không xác định.')

    # ── Hoàn tất ───────────────────────────────────────────────────────
    navigator.get_logger().info('🏁 Đã hoàn thành tất cả các điểm mục tiêu!')
    navigator.lifecycleShutdown()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

