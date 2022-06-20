import carla
import time
import random
import cv2
import numpy as np


# 存储生成的actor
actor_list = []
try:
    # 创建client链接到Carla当中
    client = carla.Client('localhost', 2000)
    # 设置超时时间
    client.set_timeout(10.0)
    # 获取世界
    world = client.get_world()
    # 通过world获取world中的蓝图
    blueprint_library = world.get_blueprint_library()

    #
    collision_sensor_bp = blueprint_library.find('sensor.other.collision')
    vehicle_bp = random.choice(blueprint_library.filter('vehicle.bmw.*'))
    camera_bp = blueprint_library.find('sensor.camera.rgb')

    # 设置RGB相机的分辨率和视野
    camera_bp.set_attribute('image_size_x', str(1920))
    camera_bp.set_attribute('image_size_y', str(1080))
    camera_bp.set_attribute('fov', '110')
    # 设置传感器捕捉数据时间间隔秒
    camera_bp.set_attribute('sensor_tick', '1.0')

    # 生成actors
    spawn_points_159 = carla.Transform(carla.Location(
        x=37.249432, y=-170.444504, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.326125, roll=0.000000))
    camera_init = carla.Transform(carla.Location(x=0.8, z=1.7))

    my_vehicle = world.spawn_actor(vehicle_bp, spawn_points_159)
    my_camera = world.spawn_actor(camera_bp, camera_init, attach_to=my_vehicle)
    actor_list.append(my_camera)
    actor_list.append(my_vehicle)

    # 车辆运动参数
    my_vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0))
    v = my_vehicle.get_velocity()
    print(dir(v))

    map = world.get_map()

    waypoint = map.get_waypoint(my_vehicle.get_location(), project_to_road=True,
                                lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))
    # 获取航路点所在的车道类型。
    lane_type = waypoint.lane_type
    # 找到左边的车道标记类型
    left_lanemarking_type = waypoint.left_lane_marking
    # 获取此航路点的可用车道更改
    lane_change = waypoint.lane_change
    print(waypoint.road_id)

    time.sleep(15)

finally:
    for actor in actor_list:
        actor.destroy()
        print(actor.id, ' is destroyed')
