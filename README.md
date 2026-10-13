# 🤖 TB4 AutoNav System – Hệ thống Điều hướng Tự động TurtleBot 4
Gói wrapper ROS 2 (Humble) cho bài thực hành **Mô phỏng, SLAM và Điều hướng tự động** với TurtleBot 4.
## 📋 Yêu cầu hệ thống
- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- GPU hỗ trợ OpenGL (cho RViz2 và Gazebo)
## 📦 Cài đặt
### 1. Cài đặt các gói phụ thuộc
```bash
sudo apt update
sudo apt install -y \
  ros-humble-turtlebot4-simulator \
  ros-humble-turtlebot4-desktop \
  ros-humble-turtlebot4-navigation \
  ros-humble-teleop-twist-keyboard \
  ros-humble-nav2-map-server \
  xterm
```
  
### 2. Clone và build workspace

  
```bash
mkdir -p ~/Ros2/hri_ws/src && cd ~/Ros2/hri_ws/src
git clone -b tuan_4 https://github.com/QuanJB/hri_thuc_hanh.git .
cd ~/Ros2/hri_ws
colcon build --packages-select tb4_autonav_system
source install/setup.bash
```
  

  

Lưu ý: Sau mỗi lần mở terminal mới, cần chạy lại lệnh source:


  ```
bash
source /opt/ros/humble/setup.bash
source ~/Ros2/hri_ws/install/setup.bash

  ```

  

  
## 🚀 Hướng dẫn Chạy

  

Quy trình gồm 3 giai đoạn thực hiện lần lượt:


  
Giai đoạn 1: Khởi chạy Mô phỏng

  

Mở Terminal 1 và chạy:


  ```
bash
ros2 launch tb4_autonav_system 1_sim.launch.py

  ```

Lệnh này sẽ:


  

  
- Khởi động Ignition Gazebo với thế giới warehouse

  
- Mở RViz2 để hiển thị robot và cảm biến

  

  

Tuỳ chọn: Thay đổi thế giới mô phỏng:


```  
bash
ros2 launch tb4_autonav_system 1_sim.launch.py world:=depot

  ```

  

⏳ Đợi cho đến khi Gazebo và RViz2 hiển thị đầy đủ trước khi sang giai đoạn 2.


  

  

  
Giai đoạn 2: Lập bản đồ (SLAM)

  

Mở Terminal 2 và chạy:


  
bash
ros2 launch tb4_autonav_system 2_mapping.launch.py

  

Lệnh này sẽ:


  

  
Khởi động SLAM Toolbox (chế độ async) để xây dựng bản đồ

  
Mở cửa sổ xterm với teleop_twist_keyboard để điều khiển robot

  

  

Điều khiển robot bằng bàn phím:


  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
Phím	Hành động
i	Tiến
,	Lùi
j	Rẽ trái
l	Rẽ phải
k	Dừng
q / z	Tăng / Giảm tốc độ

  

👉 Di chuyển robot quanh toàn bộ khu vực cần lập bản đồ. Quan sát bản đồ được xây dựng dần trên RViz2.


  
Lưu bản đồ

  

Khi bản đồ đã hoàn chỉnh, mở Terminal 3 và chạy:


  
bash
cd ~/Ros2/hri_ws/src/tb4_autonav_system/scripts
./save_map.sh

  

Bản đồ sẽ được lưu tại tb4_autonav_system/maps/my_map.yaml và my_map.pgm.


  

Sau khi lưu, build lại để cài đặt bản đồ vào package:


  
bash
cd ~/Ros2/hri_ws
colcon build --packages-select tb4_autonav_system
source install/setup.bash

  

  

✅ Sau khi lưu bản đồ thành công, tắt Terminal 2 (Ctrl+C) để dừng SLAM và teleop.


  

  

  
Giai đoạn 3: Điều hướng Tự động (Nav2)

  

Mở Terminal 2 (hoặc terminal mới) và chạy:


  
bash
ros2 launch tb4_autonav_system 3_navigation.launch.py

  

Lệnh này sẽ:


  

  
Khởi động Nav2 với bản đồ đã lưu

  
Sử dụng AMCL để định vị robot trên bản đồ

  

  
Các bước thực hiện trên RViz2:

  

  

  

Đặt vị trí ban đầu: Nhấn nút "2D Pose Estimate" trên thanh công cụ RViz2, sau đó click và kéo trên bản đồ để chỉ định vị trí và hướng hiện tại của robot.


  

  

  

Đặt điểm đích: Nhấn nút "Nav2 Goal", sau đó click và kéo trên bản đồ để chỉ định vị trí đích. Robot sẽ tự động lập kế hoạch đường đi và di chuyển đến đích.


  

  

  

Tuỳ chọn: Sử dụng bản đồ khác:


  
bash
ros2 launch tb4_autonav_system 3_navigation.launch.py map:=/đường/dẫn/đến/bản_đồ.yaml

  

  
📁 Cấu trúc Gói

  
tb4_autonav_system/
├── launch/
│   ├── 1_sim.launch.py          # Khởi chạy mô phỏng Gazebo + RViz
│   ├── 2_mapping.launch.py      # SLAM + Teleop để lập bản đồ
│   └── 3_navigation.launch.py   # Nav2 + AMCL điều hướng tự động
├── maps/                         # Thư mục lưu bản đồ
├── scripts/
│   └── save_map.sh              # Script lưu bản đồ
├── package.xml                   # Khai báo phụ thuộc
├── setup.py                      # Cấu hình cài đặt
└── setup.cfg
