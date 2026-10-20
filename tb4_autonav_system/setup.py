import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'tb4_autonav_system'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # ament index registration
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # package manifest
        ('share/' + package_name, ['package.xml']),
        # launch files
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        # map files (yaml + pgm)
        (os.path.join('share', package_name, 'maps'),
            glob(os.path.join('maps', '*'))),
        # scripts
        (os.path.join('share', package_name, 'scripts'),
            glob(os.path.join('scripts', '*.sh'))),
    ],
    install_requires=['setuptools', 'ultralytics'],
    zip_safe=True,
    maintainer='jack',
    maintainer_email='jack@todo.todo',
    description='TurtleBot 4 Autonomous Navigation System – Simulation, SLAM & Nav2 wrapper.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'auto_navigator = tb4_autonav_system.auto_navigator:main',
            'yolo_detector = tb4_autonav_system.yolo_detector:main',
        ],
    },
)

