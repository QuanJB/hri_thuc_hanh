from setuptools import setup

package_name = 'ur3_text_drawer'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/demo_launch.py',
            'launch/ur3_sim_bringup.launch.py',
            'launch/draw_text_app.launch.py',
        ]),
        ('share/' + package_name + '/config', ['config/placeholder.yaml']),
        ('share/' + package_name + '/images', ['images/placeholder.txt']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='UR3 text drawer package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'text_to_waypoints = ur3_text_drawer.text_to_waypoints_node:main',
            'moveit_executor = ur3_text_drawer.moveit_executor_node:main',
            'text_to_waypoints_node = ur3_text_drawer.text_to_waypoints_node:main',
            'moveit_executor_node = ur3_text_drawer.moveit_executor_node:main',
        ],
    },
)
