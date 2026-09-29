Mỗi terminal mới đều phải chạy trước:

```bash
source /opt/ros/humble/setup.bash
source ~/ur_ws/install/setup.bash
```

---

## 0. Build

```bash
cd ~/ur_ws
source /opt/ros/humble/setup.bash
rosdep install --ignore-src --from-paths src -y
colcon build --packages-select ur_llm_planner ur_letter_writer
source install/setup.bash
```


---

## 1. Cấu hình mã sinh viên (bắt buộc trước khi demo)

Sửa file `src/ur_llm_planner/config/student_config.yaml`:

```yaml
/**:
  ros__parameters:
    student:
      name: "Ho Ten Cua Ban"
      id: "MSSV_CUA_BAN"
```

Build lại để nạp file:

```bash
colcon build --packages-select ur_llm_planner
```


## 2. Chạy mô phỏng (Terminal 1)

```bash
source ~/ur_ws/install/setup.bash
ros2 launch ur_llm_planner sim.launch.py                 # UR3e (mặc định)
# ros2 launch ur_llm_planner sim.launch.py ur_type:=ur3   # hoặc UR3
```

---

## 3. Thao tác cơ bản (Terminal 2)

Thao tác 1 vật, ví dụ: *"Please put the red cube in zone B."*

```bash
source ~/ur_ws/install/setup.bash
export NINEROUTER_API_KEY=<api_key_cua_ban>
ros2 run ur_llm_planner llm_planner_node.py --ros-args -p llm.model:=<ten_model> -p llm.api_key:=""
```

Gõ lệnh tại dấu nhắc `>>>`:

```
>>> Please put the red cube in zone B.
>>> Đưa khối màu vàng vào vùng A.
```


## 4. Robot thao tác nâng cao (Terminal 2 — cùng lệnh chạy như mục 3)

Phối hợp nhiều skill + nhiều vật trong một câu lệnh, kể cả khi vùng đích đang bị chiếm:

```
>>> Arrange all objects according to my student ID.
>>> Move the blue cube to zone A and the yellow cube to zone C.
>>> Swap the red cube and the blue cube.
```

Nếu vùng đích đang có vật khác, hệ thống tự chèn bước dọn vùng (chuyển vật đó về đích của nó,
hoặc sang vùng tạm `zone_tmp`) trước khi đặt vật cần đặt.

---

## 5. Gắp vật sắp xếp theo mã sinh viên (cá nhân hoá)

Dùng đúng câu lệnh ở mục 4 (`Arrange all objects according to my student ID.`) sau khi đã khai
báo MSSV thật ở mục 1. Khi planner khởi động, terminal in ra nhiệm vụ cá nhân của bạn để đối
chiếu kết quả:

```
STUDENT: Ho Ten Cua Ban | ID: MSSV | P = XX mod 6 = P
PERSONAL TASK: zone_a <- ...cube | zone_b <- ...cube | zone_c <- ...cube
```

Kiểm tra kết quả cuối cùng (vật nào đang ở vùng nào) bằng lệnh ở mục 7.2.

---

## 6. Viết chữ cái đầu tên (`ur_letter_writer`)

Không cần LLM, không cần API key — chỉ một terminal:

```bash
source ~/ur_ws/install/setup.bash
ros2 launch ur_letter_writer ur3_letter_writer.launch.py ur_type:=ur3e name:=Son
# ros2 launch ur_letter_writer ur3_letter_writer.launch.py ur_type:=ur3 name:=Son   # dùng UR3

# Chỉ định trực tiếp chữ cần vẽ (bỏ qua "name")
ros2 launch ur_letter_writer ur3_letter_writer.launch.py ur_type:=ur3e letter:=A

# Đổi kích thước / vị trí chữ
ros2 launch ur_letter_writer ur3_letter_writer.launch.py name:=Son \
  letter_width:=0.25 letter_height:=0.3 plane_center_x:=0.4 plane_center_z:=0.35
```

Xem nét chữ trên RViz: **Add → By topic → `letter_writer/markers` → MarkerArray**.

---

## 7. Tiện ích khác

### 7.1. Gọi trực tiếp từng skill (không cần LLM, chỉ cần mô phỏng ở mục 2 đang chạy)

```bash
ros2 service call /execute_skill ur_llm_planner/srv/ExecuteSkill "{skill: home}"
ros2 service call /execute_skill ur_llm_planner/srv/ExecuteSkill "{skill: pick, object: red_cube}"
ros2 service call /execute_skill ur_llm_planner/srv/ExecuteSkill "{skill: place, object: red_cube, zone: zone_b}"
ros2 service call /execute_skill ur_llm_planner/srv/ExecuteSkill "{skill: move_above, object: blue_cube}"
ros2 service call /execute_skill ur_llm_planner/srv/ExecuteSkill "{skill: close_gripper}"
ros2 service call /execute_skill ur_llm_planner/srv/ExecuteSkill "{skill: move_to_zone, zone: zone_a}"
ros2 service call /execute_skill ur_llm_planner/srv/ExecuteSkill "{skill: open_gripper}"
```

### 7.2. Theo dõi trạng thái

```bash
ros2 topic echo /scene_state          # vị trí các khối, khối đang cầm, khối nằm ở vùng nào
ros2 topic echo /llm_planner/result   # kết quả mỗi câu lệnh (SUCCESS/FAILED/REJECTED/LLM_ERROR)
```

Trên RViz: **Add → By topic → `/skill_server/markers` → MarkerArray** để hiện nhãn vùng A/B/C.

### 7.3. Gửi lệnh / kế hoạch từ terminal khác (không gõ trực tiếp ở Terminal 2)

```bash
source ~/ur_ws/install/setup.bash

# Câu lệnh ngôn ngữ tự nhiên (planner ở Terminal 2 đang chạy, interactive hoặc không)
ros2 topic pub --once /nl_command std_msgs/msg/String "{data: 'Move the blue cube to zone C.'}"

# Gửi thẳng kế hoạch JSON, bỏ qua LLM (kiểm thử Validator/Executor)
ros2 topic pub --once /plan_json std_msgs/msg/String \
  "{data: '{\"plan\": [{\"skill\": \"pick\", \"object\": \"red_cube\"}, {\"skill\": \"place\", \"object\": \"red_cube\", \"zone\": \"zone_b\"}, {\"skill\": \"home\"}]}'}"
```

### 7.4. Chạy dry-run (chỉ kiểm tra kế hoạch, không di chuyển robot)

```bash
ros2 run ur_llm_planner llm_planner_node.py --ros-args -p llm.model:=<ten_model> -p execute:=false
```

### 7.5. Chạy unit test

```bash
cd ~/ur_ws
colcon test --packages-select ur_llm_planner --event-handlers console_direct+
colcon test-result --verbose
# hoặc nhanh hơn, không qua colcon:
python3 -m pytest src/ur_llm_planner/test -q
```

---

## 8. Dừng mô phỏng và xử lý sự cố

Dừng: **Ctrl+C** ở terminal chạy `ros2 launch`. Nếu Gazebo cũ không tắt hẳn, hai phiên mô phỏng
chạy cùng lúc sẽ tranh nhau `/clock` (robot báo `EXECUTION_FAILED`). Dọn tiến trình còn sót:

```bash
ps -eo pid,comm | grep -E "ruby|move_group|skill_server|parameter_bridg|robot_state_pub|rviz2"
kill -9 <pid> <pid> ...
```

| Hiện tượng | Cách xử lý |
|---|---|
| `Service /execute_skill chua san sang` | Terminal 1 chưa xong; đợi dòng `Skill server san sang` |
| `LLM_ERROR: Khong ket noi duoc ...` | 9Router chưa chạy hoặc sai `llm.base_url` |
| `LLM_ERROR: HTTP 401` | Sai/thiếu API key. Xoá key trong `config/llm.yaml`, dùng `-p llm.api_key:=""` + `NINEROUTER_API_KEY` |
| `LLM_ERROR: Chua cau hinh llm.model` | Thêm `-p llm.model:=<ten_model>` |
| `Nhiem vu ca nhan dung vat/vung khong co...` hoặc lỗi MSSV | Sửa lại `config/student_config.yaml` (mục 1) |
| Khối trong Gazebo không đi theo robot | Kiểm tra `ros2 service list \| grep set_pose` |
| `ros2: command not found` / không thấy package | Thiếu `source /opt/ros/humble/setup.bash` và `source ~/ur_ws/install/setup.bash` |
| VSCode gạch đỏ `#include` | Build với `--cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`, sau đó *Developer: Reload Window* |

Chi tiết kiến trúc, luồng LLM → validator → skill, danh sách skill và mã trạng thái:
`src/ur_llm_planner/README.md`. Chi tiết font chữ và mặt phẳng vẽ: `src/ur_letter_writer/README.md`.
