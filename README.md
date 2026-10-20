# 🤖 TB4 AutoNav System – Hệ thống Điều hướng Tự động TurtleBot 4

Gói wrapper ROS 2 (Humble) cho bài thực hành **Mô phỏng, SLAM, Điều hướng tự động và Nhận diện vật thể** với TurtleBot 4.

## 📋 Mục lục

- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cấu trúc gói](#-cấu-trúc-gói)
- [Hướng dẫn chạy](#-hướng-dẫn-chạy)
  - [Phần 1 – Mô phỏng & Localization](#phần-1--khởi-chạy-simulation--load-bản-đồ-localization)
  - [Phần 2 – Khảo sát tọa độ mục tiêu](#phần-2--khảo-sát-và-lấy-tọa-độ-mục-tiêu-trên-bản-đồ)
  - [Phần 3 – Điều hướng tự động](#phần-3--điều-hướng-tự-động-với-nav2)
  - [Phần 4 – Nhận diện vật thể YOLO](#phần-4--nhận-diện-vật-thể-từ-camera-với-yolo)
- [Xử lý sự cố](#-xử-lý-sự-cố)

---

## 💻 Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|------------|----------|
| Hệ điều hành | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| GPU | Hỗ trợ OpenGL (cho RViz2 và Gazebo) |
| Python | 3.10+ |

---

## 📦 Cài đặt

### 1. Cài đặt các gói ROS 2 phụ thuộc

```bash
sudo apt update
sudo apt install -y \
  ros-humble-turtlebot4-simulator \
  ros-humble-turtlebot4-desktop \
  ros-humble-turtlebot4-navigation \
  ros-humble-teleop-twist-keyboard \
  ros-humble-nav2-map-server \
  ros-humble-nav2-simple-commander \
  xterm
```

### 2. Cài đặt thư viện Python (cho YOLO)

```bash
pip3 install ultralytics opencv-python
```

> **Lưu ý:** Lần đầu chạy YOLO, mô hình `yolov8n.pt` sẽ được tự động tải về (~6MB).

### 3. Clone và build workspace

```bash
mkdir -p ~/Ros2/hri_ws/src && cd ~/Ros2/hri_ws/src
git clone -b tuan_4 https://github.com/QuanJB/hri_thuc_hanh.git .
cd ~/Ros2/hri_ws
colcon build --packages-select tb4_autonav_system
source install/setup.bash
```

> **Lưu ý:** Sau mỗi lần mở terminal mới, cần chạy lại:
> ```bash
> source /opt/ros/humble/setup.bash
> source ~/Ros2/hri_ws/install/setup.bash
> ```

---

## 📁 Cấu trúc gói

```
tb4_autonav_system/
├── launch/
│   ├── 1_sim.launch.py              # Khởi chạy mô phỏng Gazebo + RViz
│   ├── 2_mapping.launch.py          # SLAM + Teleop để lập bản đồ
│   ├── 3_navigation.launch.py       # Nav2 + AMCL Localization
│   └── 4_autonav_yolo.launch.py     # Điều hướng tự động + YOLO Detection
├── maps/                             # Thư mục lưu bản đồ (.yaml + .pgm)
├── scripts/
│   └── save_map.sh                   # Script lưu bản đồ từ SLAM
├── tb4_autonav_system/
│   ├── __init__.py
│   ├── auto_navigator.py            # Node điều hướng tự động qua waypoints
│   └── yolo_detector.py             # Node nhận diện vật thể bằng YOLO
├── package.xml
├── setup.py
└── setup.cfg
```

---

## 🚀 Hướng dẫn chạy

### Phần 1 – Khởi chạy Simulation & Load bản đồ (Localization)

#### Bước 1.1: Khởi chạy mô phỏng Gazebo

Mở **Terminal 1**:

```bash
ros2 launch tb4_autonav_system 1_sim.launch.py
```

Lệnh này sẽ khởi động TurtleBot 4 trong thế giới `warehouse` trên Ignition Gazebo kèm RViz2.

**Tuỳ chọn:** Thay đổi thế giới mô phỏng:
```bash
ros2 launch tb4_autonav_system 1_sim.launch.py world:=depot
```

> ⏳ Đợi cho Gazebo và RViz2 khởi động hoàn tất trước khi sang bước tiếp theo.

#### Bước 1.2: Khởi chạy Nav2 + Localization (AMCL)

Mở **Terminal 2**:

```bash
ros2 launch tb4_autonav_system 3_navigation.launch.py
```

Lệnh này sẽ nạp bản đồ (`my_map.yaml`) và khởi chạy Nav2 với AMCL để thực hiện Localization.

**Tuỳ chọn:** Sử dụng bản đồ khác:
```bash
ros2 launch tb4_autonav_system 3_navigation.launch.py map:=/đường/dẫn/đến/bản_đồ.yaml
```

#### Bước 1.3: Thiết lập vị trí ban đầu (Initial Pose)

Trên cửa sổ **RViz2**:

1. Nhấn nút **"2D Pose Estimate"** trên thanh công cụ.
2. Click và kéo trên bản đồ để chỉ định vị trí và hướng hiện tại của robot.
3. **Kiểm tra:** Dữ liệu quét LiDAR (`/scan`) phải trùng khớp với các bức tường trên bản đồ.

> ⚠️ Nếu vị trí robot trên RViz2 không khớp với Gazebo, hãy đặt lại Initial Pose cho chính xác.

---

### Phần 2 – Khảo sát và lấy tọa độ mục tiêu trên bản đồ

Trước khi lập trình điều hướng tự động, cần xác định tọa độ **(x, y, yaw)** của **ít nhất 3 điểm mục tiêu** trên bản đồ.

#### Cách 1: Dùng Publish Point trên RViz2

1. Nhấn nút **"Publish Point"** trên thanh công cụ RViz2.
2. Click vào vị trí mong muốn trên bản đồ.
3. Mở **Terminal 3** để đọc tọa độ:

```bash
ros2 topic echo /clicked_point
```

Kết quả hiển thị dạng:
```
header:
  frame_id: "map"
point:
  x: 1.234
  y: -0.567
  z: 0.0
```

#### Cách 2: Xem vị trí hiện tại của robot

Di chuyển robot đến vị trí mong muốn (bằng teleop hoặc Nav2 Goal), sau đó:

```bash
ros2 topic echo /amcl_pose
```

#### Ghi nhận tọa độ

Ghi lại ít nhất 3 điểm mục tiêu, ví dụ:

| Điểm | x | y | yaw (độ) |
|------|---|---|----------|
| Goal 1 | 1.0 | 0.5 | 0 |
| Goal 2 | 2.0 | -1.0 | 90 |
| Goal 3 | -0.5 | 1.5 | 180 |

---

### Phần 3 – Điều hướng tự động với Nav2

#### Bước 3.1: Cập nhật tọa độ waypoints

Mở file `tb4_autonav_system/auto_navigator.py` và cập nhật danh sách `WAYPOINTS` (dòng 28–32) với tọa độ đã khảo sát:

```python
WAYPOINTS = [
    # (x,     y,     yaw_degrees)
    ( 1.0,   0.5,    0.0),    # Goal 1
    ( 2.0,  -1.0,   90.0),    # Goal 2
    (-0.5,   1.5,  180.0),    # Goal 3
]
```

#### Bước 3.2: Build lại package

```bash
cd ~/Ros2/hri_ws
colcon build --packages-select tb4_autonav_system
source install/setup.bash
```

#### Bước 3.3: Chạy Node điều hướng tự động

**Cách 1:** Chạy riêng node (chỉ navigation, không có YOLO):

```bash
ros2 run tb4_autonav_system auto_navigator
```

**Cách 2:** Chạy cùng YOLO qua launch file (xem Phần 4).

**Kết quả mong đợi trên Terminal:**
```
[INFO] ⏳ Đang đợi Nav2 khởi động...
[INFO] ✅ Nav2 đã sẵn sàng!
[INFO] 🚀 Đang di chuyển đến Goal 1/3: x=1.00, y=0.50, yaw=0.0°
[INFO]    📍 Goal 1 – ETA: 12.3s
[INFO] ✅ Goal 1 – Đã đến nơi thành công!
[INFO] 🚀 Đang di chuyển đến Goal 2/3: x=2.00, y=-1.00, yaw=90.0°
...
[INFO] 🏁 Đã hoàn thành tất cả các điểm mục tiêu!
```

> **Lưu ý:** Robot sẽ tự lập kế hoạch đường đi và di chuyển. **Không điều khiển thủ công** và **không dùng chuột đặt goal trên RViz2** khi node đang chạy.

---

### Phần 4 – Nhận diện vật thể từ Camera với YOLO

#### Chạy cả Auto Navigation + YOLO Detection

Mở **Terminal 3** (trong khi Terminal 1 chạy Sim và Terminal 2 chạy Nav2):

```bash
ros2 launch tb4_autonav_system 4_autonav_yolo.launch.py
```

Lệnh này sẽ đồng thời:
- Khởi chạy **YOLO Detector** – subscribe camera, chạy inference, vẽ bounding box
- Khởi chạy **Auto Navigator** (delay 5s) – robot tự động di chuyển qua các waypoints

**Tuỳ chọn launch arguments:**

```bash
# Sử dụng mô hình YOLO lớn hơn (chính xác hơn, nhưng chậm hơn)
ros2 launch tb4_autonav_system 4_autonav_yolo.launch.py yolo_model:=yolov8s.pt

# Thay đổi ngưỡng độ tin cậy
ros2 launch tb4_autonav_system 4_autonav_yolo.launch.py confidence:=0.3

# Tắt cửa sổ OpenCV (chỉ publish lên topic)
ros2 launch tb4_autonav_system 4_autonav_yolo.launch.py display_window:=false
```

#### Chạy riêng YOLO Detector (không có Auto Navigation)

```bash
ros2 run tb4_autonav_system yolo_detector
```

Hoặc với các tham số tuỳ chỉnh:

```bash
ros2 run tb4_autonav_system yolo_detector --ros-args \
  -p model:=yolov8s.pt \
  -p confidence_threshold:=0.3 \
  -p camera_topic:=/oakd/rgb/preview/image_raw
```

#### Xem kết quả YOLO

**Trên Terminal:** Log hiển thị thông tin vật thể phát hiện được:
```
[INFO] 🔍 Phát hiện: person | Độ tin cậy: 0.87 | Vị trí: [120, 45, 280, 390]
[INFO] 🔍 Phát hiện: chair  | Độ tin cậy: 0.72 | Vị trí: [340, 200, 450, 380]
```

**Trên cửa sổ OpenCV:** Hiển thị hình ảnh camera với bounding box và label.

**Trên RViz2:** Có thể thêm Image display, chọn topic `/yolo/detections_image` để xem ảnh đã annotate.

---

## 📑 Tóm tắt các lệnh chạy

| Terminal | Lệnh | Mô tả |
|----------|-------|--------|
| **Terminal 1** | `ros2 launch tb4_autonav_system 1_sim.launch.py` | Khởi chạy Gazebo + RViz |
| **Terminal 2** | `ros2 launch tb4_autonav_system 3_navigation.launch.py` | Nav2 + AMCL Localization |
| _RViz2_ | _Nhấn "2D Pose Estimate" → set vị trí robot_ | _Thiết lập Initial Pose_ |
| **Terminal 3** | `ros2 launch tb4_autonav_system 4_autonav_yolo.launch.py` | Auto Nav + YOLO Detection |

---

## 🗺️ Phụ lục: Lập bản đồ mới (SLAM)

Nếu cần xây dựng bản đồ mới thay vì sử dụng bản đồ có sẵn:

### Bước 1: Khởi chạy mô phỏng (Terminal 1)
```bash
ros2 launch tb4_autonav_system 1_sim.launch.py
```

### Bước 2: Khởi chạy SLAM + Teleop (Terminal 2)
```bash
ros2 launch tb4_autonav_system 2_mapping.launch.py
```

Điều khiển robot bằng bàn phím trong cửa sổ xterm:

| Phím | Hành động |
|------|-----------|
| `i` | Tiến |
| `,` | Lùi |
| `j` | Rẽ trái |
| `l` | Rẽ phải |
| `k` | Dừng |
| `q` / `z` | Tăng / Giảm tốc độ |

### Bước 3: Lưu bản đồ (Terminal 3)
```bash
cd ~/Ros2/hri_ws/src/tb4_autonav_system/scripts
./save_map.sh
```

### Bước 4: Build lại để cài đặt bản đồ
```bash
cd ~/Ros2/hri_ws
colcon build --packages-select tb4_autonav_system
```

---

## 🔧 Xử lý sự cố

| Lỗi | Nguyên nhân | Cách khắc phục |
|-----|-------------|----------------|
| `package not found` | Chưa cài đặt gói phụ thuộc | Chạy lại lệnh `sudo apt install` ở phần Cài đặt |
| `Failed to create OpenGL context` | Driver GPU không tương thích | Chạy `sudo reboot` sau khi cập nhật driver |
| Cửa sổ xterm không mở | Chưa cài đặt xterm | `sudo apt install xterm` |
| Robot không di chuyển | Nav2 chưa active hoặc chưa set Initial Pose | Kiểm tra Terminal 2 và set "2D Pose Estimate" trên RViz2 |
| `ultralytics not installed` | Chưa cài thư viện YOLO | `pip3 install ultralytics` |
| YOLO không nhận được ảnh | Topic camera không đúng | Kiểm tra topic bằng `ros2 topic list \| grep image` |
| Bản đồ không hiển thị trong Nav2 | Chưa build lại sau khi lưu bản đồ | `colcon build --packages-select tb4_autonav_system` |
| LiDAR không khớp với bản đồ | Initial Pose không chính xác | Đặt lại "2D Pose Estimate" cho khớp với vị trí robot trong Gazebo |

