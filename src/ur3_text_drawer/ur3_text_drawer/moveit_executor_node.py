#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from ur3_text_drawer.srv import GenerateTextTrajectory
from moveit_msgs.srv import GetCartesianPath
from moveit_msgs.action import ExecuteTrajectory, MoveGroup
from moveit_msgs.msg import MoveItErrorCodes, Constraints, PositionConstraint, OrientationConstraint, BoundingVolume
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import PoseStamped

class MoveItExecutorNode(Node):
    def __init__(self):
        super().__init__('moveit_executor')
        self.declare_parameter('text', 'Q')
        self.text = self.get_parameter('text').get_parameter_value().string_value

        self.text_cli = self.create_client(GenerateTextTrajectory, 'generate_text_trajectory')
        self.cartesian_cli = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self.move_action_cli = ActionClient(self, MoveGroup, 'move_action')
        self.execute_cli = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')

    def wait_for_servers(self):
        self.get_logger().info('Chờ các dịch vụ MoveIt...')
        self.text_cli.wait_for_service()
        self.cartesian_cli.wait_for_service()
        self.move_action_cli.wait_for_server()
        self.execute_cli.wait_for_server()

    def go_to_start_point(self, start_pose):
        self.get_logger().info('Bước 1: Thoát khỏi Singularity, di chuyển cong đến điểm bắt đầu...')
        goal = MoveGroup.Goal()
        goal.request.group_name = 'ur_manipulator'
        
        # Đặt mục tiêu là điểm đầu tiên của chữ Q
        pose_stamped = PoseStamped()
        pose_stamped.header.frame_id = 'base_link'
        pose_stamped.pose = start_pose
        
        # Ràng buộc mục tiêu
        constraint = Constraints()
        p_const = PositionConstraint()
        p_const.header.frame_id = 'base_link'
        p_const.link_name = 'tool0' # Điểm chót của UR3
        p_const.target_point_offset.x = 0.0
        p_const.target_point_offset.y = 0.0
        p_const.target_point_offset.z = 0.0
        bv = BoundingVolume()
        sphere = SolidPrimitive()
        sphere.type = SolidPrimitive.SPHERE
        sphere.dimensions = [0.01] # Dung sai 1cm
        bv.primitives.append(sphere)
        bv.primitive_poses.append(start_pose)
        p_const.constraint_region = bv
        p_const.weight = 1.0
        constraint.position_constraints.append(p_const)
        
        o_const = OrientationConstraint()
        o_const.header.frame_id = 'base_link'
        o_const.link_name = 'tool0'
        o_const.orientation = start_pose.orientation
        o_const.absolute_x_axis_tolerance = 0.05
        o_const.absolute_y_axis_tolerance = 0.05
        o_const.absolute_z_axis_tolerance = 0.05
        o_const.weight = 1.0
        constraint.orientation_constraints.append(o_const)
        
        goal.request.goal_constraints.append(constraint)
        
        future = self.move_action_cli.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error('Không thể tìm đường đến điểm bắt đầu!')
            return False
            
        res_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, res_future)
        return res_future.result().result.error_code.val == MoveItErrorCodes.SUCCESS

    def run_workflow(self):
        # 1. Xin tọa độ
        req_text = GenerateTextTrajectory.Request()
        req_text.text = self.text
        future_text = self.text_cli.call_async(req_text)
        rclpy.spin_until_future_complete(self, future_text)
        poses = future_text.result().poses.poses 

        if not poses: return
        
        # 2. Bắt buộc robot di chuyển an toàn đến điểm đầu tiên trước
        if not self.go_to_start_point(poses[0]):
            return

        # 3. Sau khi đến nơi an toàn, mới bắt đầu vẽ nét thẳng
        self.get_logger().info('Bước 2: Robot đã sẵn sàng vẽ! Bắt đầu tính Cartesian Path...')
        req_cart = GetCartesianPath.Request()
        req_cart.group_name = 'ur_manipulator'
        req_cart.header.frame_id = 'base_link'
        req_cart.waypoints = poses
        req_cart.max_step = 0.01
        req_cart.avoid_collisions = True
        
        future_cart = self.cartesian_cli.call_async(req_cart)
        rclpy.spin_until_future_complete(self, future_cart)
        res_cart = future_cart.result()
        
        if res_cart.fraction < 0.9:
            self.get_logger().error(f'Quỹ đạo vẽ hỏng (Fraction: {res_cart.fraction})')
            return
            
        self.get_logger().info('Bắt đầu thực thi nét vẽ...')
        goal_msg = ExecuteTrajectory.Goal()
        goal_msg.trajectory = res_cart.solution
        future_exec = self.execute_cli.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future_exec)
        goal_handle = future_exec.result()
        future_res = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, future_res)
        self.get_logger().info('✨ Hoàn thành chữ Q! ✨')

def main(args=None):
    rclpy.init(args=args)
    node = MoveItExecutorNode()
    node.wait_for_servers()
    node.run_workflow()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
