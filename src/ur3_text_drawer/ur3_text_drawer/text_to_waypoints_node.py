#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseArray, Pose, Point, Quaternion
from std_msgs.msg import Header
from ur3_text_drawer.srv import GenerateTextTrajectory
from visualization_msgs.msg import Marker  # Thư viện để vẽ hình lên RViz

class TextToWaypointsNode(Node):
    def __init__(self):
        super().__init__('text_to_waypoints')
        self.srv = self.create_service(GenerateTextTrajectory, 'generate_text_trajectory', self.handle_generate)
        # Khởi tạo kênh xuất dữ liệu hình ảnh (Publisher) cho RViz
        self.marker_pub = self.create_publisher(Marker, 'text_marker', 10)
        self.get_logger().info('Text to waypoints service ready: generate_text_trajectory')

    def handle_generate(self, request, response):
        text = request.text.strip()
        pose_array = PoseArray()
        pose_array.header = Header()
        pose_array.header.frame_id = 'base_link'
        pose_array.header.stamp = self.get_clock().now().to_msg()

        if text.upper() == 'Q':
            poses = self._generate_q_waypoints()
        else:
            poses = []

        pose_array.poses = poses
        response.poses = pose_array
        
        # Bắn hình ảnh bản nháp chữ Q lên RViz ngay khi được yêu cầu
        if poses:
            self.publish_marker(poses)
            
        return response

    def _generate_q_waypoints(self):
        center_x = 0.25  
        center_y = 0.0
        z = 0.2          
        radius = 0.05
        points = []
        steps = 20 # Tăng độ mịn nét chữ (20 điểm cong)
        
        downward_orientation = Quaternion(x=1.0, y=0.0, z=0.0, w=0.0)

        # Vẽ vòng tròn (Khép kín bằng cách chạy vòng lặp steps + 1)
        for i in range(steps + 1):
            theta = 2.0 * math.pi * (i / float(steps))
            x = center_x + radius * math.cos(theta)
            y = center_y + radius * math.sin(theta)
            p = Pose()
            p.position = Point(x=x, y=y, z=z)
            p.orientation = downward_orientation
            points.append(p)

        # Nét gạch chéo
        tail1 = Pose()
        tail1.position = Point(x=center_x + 0.02, y=center_y - 0.02, z=z)
        tail1.orientation = downward_orientation
        tail2 = Pose()
        tail2.position = Point(x=center_x + 0.06, y=center_y - 0.06, z=z)
        tail2.orientation = downward_orientation
        
        points.append(tail1)
        points.append(tail2)

        return points

    def publish_marker(self, poses):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "text_drawing"
        marker.id = 0
        marker.type = Marker.LINE_STRIP # Nối các điểm thành 1 đường liền nét
        marker.action = Marker.ADD
        
        # Kích thước nét bút: 5mm (0.005 mét)
        marker.scale.x = 0.005 
        
        # Màu sắc: Đỏ tươi rực rỡ (RGBA)
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0 
        
        # Nạp tọa độ vào
        for pose in poses:
            marker.points.append(pose.position)
            
        self.marker_pub.publish(marker)
        self.get_logger().info('Đã vẽ bản nháp lên RViz2!')

def main(args=None):
    rclpy.init(args=args)
    node = TextToWaypointsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
