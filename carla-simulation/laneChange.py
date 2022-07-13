"""
 Author         : maxiaoming
 Date           : 2022-06-22 10:39:50
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-13 14:22:27
 FilePath       : laneChange.py
 Description    : 车辆自主变道并录视频
"""
import argparse
import copy
import math
import queue
import random
import sys
import time

import cv2
import numpy as np

sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")
sys.path.append('D:/CARLA/carla/PythonAPI/')
sys.path.append('D:/CARLA/carla/PythonAPI/carla')


import carla
from agents.navigation.controller import VehiclePIDController


def get_speed(vehicle):
    vel = vehicle.get_velocity()
    return 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)


VEHICLE_VEL = 5


class Player():
    def __init__(self, world, bp, verl_ref=VEHICLE_VEL, max_throttle=0.75, max_brake=0.3, max_steer=0.8):
        self.max_throt = max_throt
        self.max_brake = max_brake
        self.max_steer = max_steer
        self.vehicle = None
        self.bp = bp


def main():
    """
        主函数
    """
    # 存储生成的actor
    actor_list = []
    try:
        argparser = argparse.ArgumentParser()
        argparser.add_argument(
            '--map',
            help='map name',
            default='Town04',
        )
        argparser.add_argument(
            '--vehicle',
            help='vehicle name',
            default='bmw',
        )
        argparser.add_argument(
            '--filename',
            help="视频名称",
            default='result.mp4'
        )

        args = argparser.parse_args()

        map_name = args.map
        filename = args.filename

        # 创建client链接到Carla当中
        client = carla.Client('localhost', 2000)
        # 设置超时时间
        client.set_timeout(10.0)
        # 获取世界
        # world = client.get_world()
        world = client.load_world(map_name)
        # weather = carla.WeatherParameters(
        #     sun_altitude_angle=0
        # )
        # world.set_weather(weather)
        # 通过world获取world中的蓝图
        blueprint_library = world.get_blueprint_library()

        # 碰撞传感器
        collision_sensor_bp = blueprint_library.find('sensor.other.collision')
        #collision_sensor = world.spawn_actor(collision_sensor_bp, carla.Transform(), attach_to=my_vehicle)
        #collision_sensor_bp.listen(lambda event: parse_event(event))

        def parse_event(event):
            pass

        # 生成车辆
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.bmw.grandtourer'))
        model3_spawn_point = carla.Transform(carla.Location(
            x=-9.895893, y=-212.574677, z=0.281942), carla.Rotation(pitch=0.000000, yaw=89.775124, roll=0.000000))
        my_vehicle = world.spawn_actor(vehicle_bp, model3_spawn_point)

        # 设置RGB相机的分辨率和视野
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        image_size_x = 1920
        image_size_y = 1080
        camera_bp.set_attribute('image_size_x', str(image_size_x))
        camera_bp.set_attribute('image_size_y', str(image_size_y))
        camera_bp.set_attribute('fov', '110')
        # 设置传感器捕捉数据时间间隔秒
        camera_bp.set_attribute('sensor_tick', '1.0')

        # 生成actors
        camera_init = carla.Transform(carla.Location(x=0.8, z=1.7))
        my_camera = world.spawn_actor(camera_bp,
                                      carla.Transform(carla.Location(x=0.8, z=1.7)),
                                      my_vehicle,
                                      )
        my_camera_fushi = world.spawn_actor(
            camera_bp,
            carla.Transform(carla.Location(z=25), carla.Rotation(pitch=-90)),
            my_vehicle,
        )

        my_camera = world.spawn_actor(camera_bp, camera_init, attach_to=my_vehicle)

        my_camera.listen(lambda image: parse_image(image))

        actor_list.extend((my_camera, my_vehicle))

        def parse_image(image):
            global Image_Array
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]

            Image_Array = array

        # 车辆运动参数
        # my_vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=0))
        my_vehicle.enable_constant_velocity(carla.Vector3D(2.5, 0, 0))

        width, height = int(image_size_x), int(image_size_y)  # 宽高
        if filename.split('.')[-1] == 'mp4':
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 视频编解码器
        else:
            fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        # fps = 40
        fps = 30
        writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        try:
            i = 0
            while True:
                if Image_Array is not None:
                    i += 1
                    image = copy.copy(Image_Array)
                    if 1 <= i <= 600:
                        writer.write(image)
                    cv2.imshow('Carla Tutorial', image)
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                        break
        finally:
            writer.release()

    finally:
        # client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        for actor in actor_list:
            actor.destroy()
            print(actor.id, ' is destroyed')


if __name__ == '__main__':
    Image_Array = None
    main()
