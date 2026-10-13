#!/usr/bin/env bash
# --------------------------------------------------------------------------
# save_map.sh – Save the current SLAM map using nav2_map_server
#
# The map is saved into this package's maps/ directory so that it is
# picked up automatically by 3_navigation.launch.py after a rebuild.
#
# Usage:
#   1. Make sure 2_mapping.launch.py (SLAM) is still running.
#   2. Run:  bash save_map.sh            (or ./save_map.sh if executable)
#   3. Rebuild the workspace so the new map files are installed:
#        cd ~/Ros2/hri_ws && colcon build --packages-select tb4_autonav_system
# --------------------------------------------------------------------------

set -e

# Resolve the directory where this script lives (package source tree)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAP_DIR="${SCRIPT_DIR}/../maps"

# Create the maps directory if it doesn't exist
mkdir -p "${MAP_DIR}"

MAP_PATH="${MAP_DIR}/my_map"

echo ">>> Saving map to: ${MAP_PATH}"
ros2 run nav2_map_server map_saver_cli -f "${MAP_PATH}"
echo ">>> Map saved!  Files:"
ls -lh "${MAP_PATH}".*
echo ""
echo ">>> Now rebuild so the map is installed into the package share:"
echo "    cd ~/Ros2/hri_ws && colcon build --packages-select tb4_autonav_system"

