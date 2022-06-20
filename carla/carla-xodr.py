# sourcery skip: avoid-builtin-shadow
import copy
import os
import pathlib
import random
import sys
import time
import xml.etree.ElementTree as ET

import cv2
import numpy as np

sys.path.append(
    "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg"
)
import carla

# myfile = ET.parse(
#     "/home/realai/zhujianwei/vehicle_automation/carla/Unreal/CarlaUE4/Content/Carla/Maps/OpenDrive/Town01.xodr")
# root = myfile.getroot()
# xodrStr = ET.tostring(root, encoding="utf-8", method="xml")
try:
    data = pathlib.Path("/home/realai/zhujianwei/vehicle_automation/carla/Unreal/CarlaUE4/Content/Carla/Maps/OpenDrive/Town01.xodr").read_text()
except OSError:
    sys.exit()


actor_list = []

try:
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    vertex_distance = 2.0  # in meters
    max_road_length = 500.0 # in meters
    wall_height = 0.0      # in meters
    extra_width = 0.6      # in meters
    # world = client.generate_opendrive_world(
    #     data, carla.OpendriveGenerationParameters(
    #         vertex_distance=vertex_distance,
    #         max_road_length=max_road_length,
    #         wall_height=wall_height,
    #         additional_width=extra_width,
    #         smooth_junctions=True,
    #         enable_mesh_visibility=True))

    # Traffic Manager
    traffic_manager = client.get_trafficmanager() # port
    # tm里的每一辆车都要和前车保持至少3m的距离来保持完全
    traffic_manager.set_global_distance_to_leading_vehicle(3.0)
    # tm里的每一辆车都是混合物里模式
    traffic_manager.set_hybrid_physics_mode(True)
    # tm里的每辆车都是默认速度的80%
    traffic_manager.global_percentage_speed_difference(80)

    # 获取观众对象
    spectator = world.get_spectator()
    print(spectator)
    # 通过其变换获取观众的位置和旋转
    transform = spectator.get_transform()
    location = transform.location
    rotation = transform.rotation
    spectator.set_transform(carla.Transform())

    ###### 添加NPC
    vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')
    # 获取预定义的生成点
    spawn_points = world.get_map().get_spawn_points()
    # 生成 50 辆随机分布在地图上的车辆
    for _ in range(50):
        v_actor = world.try_spawn_actor(random.choice(vehicle_blueprints, random.choices(spawn_points)))
        v_actor.set_autopilot(True)
        actor_list.append(v_actor)
    # 使所有车辆自动驾驶
    for vehicle in world.get_actors().filter('vehicle'):
        vehicle.set_autopilot(True)
    # 生成控制车辆
    ego_vehicle = world.spawn_actor(random.choice(vehicle_blueprints, random.choices(spawn_points)))
    actor_list.append(ego_vehicle)

    ######### 添加传感器
    # 创建将相机且放置在车辆顶部
    camera_init_trans = carla.Transform(carla.Location(z=1.5))
    # 通过蓝图创建rgb相机
    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    # 生成相机且绑定到 ego_vehicle 车辆上
    camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=ego_vehicle)
    actor_list.append(camera)
    camera.listen(lambda image: image.save_to_disk('out/%06d.png'%image.frame))
        
    # 行人
    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    world.SpawnActor(walker_controller_bp, carla.Transform())
except Exception as e:
    print(e)
    client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
    # for actor in actor_list:
    #     actor.destroy()
