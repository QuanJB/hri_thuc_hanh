#!/usr/bin/env python3
# --------------------------------------------------------------------------
# yolo_detector.py – Nhận diện vật thể bằng YOLO từ camera TurtleBot 4
#
# Subscribe hình ảnh từ camera OAK-D, chạy YOLOv8 inference,
# vẽ bounding box + label và publish kết quả lên topic /yolo/detections_image
# để hiển thị trên RViz2.
#
# Usage:  ros2 run tb4_autonav_system yolo_detector
#         ros2 run tb4_autonav_system yolo_detector --ros-args -p model:=yolov8s.pt
#         ros2 run tb4_autonav_system yolo_detector --ros-args -p camera_topic:=/oakd/rgb/preview/image_raw
# --------------------------------------------------------------------------

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__('yolo_detector')

        # ── Khai báo parameters ────────────────────────────────────────
        self.declare_parameter('camera_topic', '/oakd/rgb/preview/image_raw')
        self.declare_parameter('model', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('publish_topic', '/yolo/detections_image')
        self.declare_parameter('display_window', True)

        camera_topic = self.get_parameter('camera_topic').value
        model_name = self.get_parameter('model').value
        self.conf_threshold = self.get_parameter('confidence_threshold').value
        publish_topic = self.get_parameter('publish_topic').value
        self.display_window = self.get_parameter('display_window').value

        # ── Khởi tạo YOLO ─────────────────────────────────────────────
        if not YOLO_AVAILABLE:
            self.get_logger().error(
                '❌ Thư viện ultralytics chưa được cài đặt!\n'
                '   Chạy: pip3 install ultralytics'
            )
            raise RuntimeError('ultralytics not installed')

        self.get_logger().info(f'⏳ Đang tải mô hình YOLO: {model_name}...')
        self.model = YOLO(model_name)
        self.get_logger().info(f'✅ Đã tải mô hình YOLO: {model_name}')

        # ── cv_bridge ──────────────────────────────────────────────────
        self.bridge = CvBridge()

        # ── QoS tương thích với camera Gazebo ──────────────────────────
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # ── Subscriber: hình ảnh từ camera ─────────────────────────────
        self.image_sub = self.create_subscription(
            Image,
            camera_topic,
            self.image_callback,
            qos,
        )
        self.get_logger().info(f'📷 Đang subscribe topic: {camera_topic}')

        # ── Publisher: hình ảnh đã annotate ────────────────────────────
        self.image_pub = self.create_publisher(Image, publish_topic, 10)
        self.get_logger().info(f'📤 Publish kết quả lên topic: {publish_topic}')

    def image_callback(self, msg: Image):
        """Xử lý mỗi frame ảnh từ camera."""
        try:
            # Chuyển đổi ROS Image → OpenCV BGR
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Lỗi chuyển đổi ảnh: {e}')
            return

        # ── Chạy YOLO inference ────────────────────────────────────────
        results = self.model(cv_image, conf=self.conf_threshold, verbose=False)

        # ── Xử lý kết quả ─────────────────────────────────────────────
        annotated_frame = cv_image.copy()

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            for box in result.boxes:
                # Lấy tọa độ bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]

                # Vẽ bounding box
                color = self._get_color(class_id)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                # Vẽ label
                label = f'{class_name} {confidence:.2f}'
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - label_size[1] - 10),
                    (x1 + label_size[0], y1),
                    color,
                    -1,
                )
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                # In thông tin ra terminal
                self.get_logger().info(
                    f'🔍 Phát hiện: {class_name} | '
                    f'Độ tin cậy: {confidence:.2f} | '
                    f'Vị trí: [{x1}, {y1}, {x2}, {y2}]',
                    throttle_duration_sec=0.5,
                )

        # ── Publish ảnh đã annotate ────────────────────────────────────
        try:
            out_msg = self.bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
            out_msg.header = msg.header
            self.image_pub.publish(out_msg)
        except Exception as e:
            self.get_logger().error(f'Lỗi publish ảnh: {e}')

        # ── Hiển thị cửa sổ OpenCV (tuỳ chọn) ─────────────────────────
        if self.display_window:
            cv2.imshow('YOLO Detections – TurtleBot 4', annotated_frame)
            cv2.waitKey(1)

    @staticmethod
    def _get_color(class_id: int):
        """Tạo màu riêng cho mỗi class dựa trên class_id."""
        np.random.seed(class_id + 42)
        return tuple(int(c) for c in np.random.randint(0, 255, 3))


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 Dừng YOLO Detector.')
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

