"""
 Author         : maxiaoming
 Date           : 2022-06-22 10:39:50
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-06-27 10:39:52
 FilePath       : car_run_line.py
 Description    : Carla车辆跑直线并录视频
"""
import os
import sys

sys.path.insert(0,
    "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

from csv import writer
import numpy as np
import cv2
import random
import carla
import copy
import argparse


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
            help='map name'
        )
        argparser.add_argument(
            '--vehicle',
            help='vehicle name'
        )
        argparser.add_argument(
            '--filename',
            help="视频名称"
        )

        # points = {
        #     'Town01': (carla.Transform(carla.Location(x=295.081757, y=199.060303, z=0.300000), carla.Rotation(pitch=0.000000, yaw=-0.000092, roll=0.000000)), carla.Transform(carla.Location(x=142.360550, y=198.759995, z=0.300000), carla.Rotation(pitch=0.000000, yaw=-0.000092, roll=0.000000))),
        #     'Town02': (carla.Transform(carla.Location(x=189.929993, y=142.190002, z=0.500000), carla.Rotation(pitch=0.000000, yaw=89.999954, roll=0.000000)), carla.Transform(carla.Location(x=189.929993, y=293.540009, z=0.500000), carla.Rotation(pitch=0.000000, yaw=89.999954, roll=0.000000))),
        #     'Town03': (carla.Transform(carla.Location(x=-18.582256, y=-204.674316, z=0.275307), carla.Rotation(pitch=0.000000, yaw=-178.560471, roll=0.000000)), carla.Transform(carla.Location(x=129.905441, y=-201.210129, z=0.275307), carla.Rotation(pitch=0.000000, yaw=-178.560471, roll=0.000000))),
        #     'Town04': (carla.Transform(carla.Location(x=-9.890791, y=-211.274689, z=0.281942), carla.Rotation(pitch=0.000000, yaw=89.775124, roll=0.000000)), carla.Transform(carla.Location(x=-8.437963, y=128.214111, z=0.281942), carla.Rotation(pitch=0.000000, yaw=89.710899, roll=0.000000))),
        #     'Town05': (carla.Transform(carla.Location(x=28.046694, y=163.645676, z=0.300000), carla.Rotation(pitch=0.000000, yaw=90.022896, roll=0.000000)), carla.Transform(carla.Location(x=32.147095, y=-176.243668, z=0.300000), carla.Rotation(pitch=0.000000, yaw=91.532082, roll=0.000000))),
        # }

        points = {
            'Town01': (
                carla.Transform(carla.Location(x=170.547531, y=59.902679, z=0.300000), carla.Rotation(pitch=0.000000, yaw=0.000061, roll=0.000000)),
                carla.Transform(carla.Location(x=272.290009, y=57.330036, z=0.300000), carla.Rotation(pitch=0.000000, yaw=89.999756, roll=0.000000)),
            ),
            'Town02': (
                carla.Transform(carla.Location(x=55.410027, y=109.399986, z=0.500000), carla.Rotation(pitch=0.000000, yaw=-0.000183, roll=0.000000)),
                carla.Transform(carla.Location(x=151.750061, y=107.400040, z=0.500000), carla.Rotation(pitch=0.000000, yaw=89.999817, roll=0.000000)),
            ),
            'Town03': (
                carla.Transform(carla.Location(x=65.516594, y=7.808423, z=0.275307), carla.Rotation(pitch=0.000000, yaw=0.855823, roll=0.000000)),
                carla.Transform(carla.Location(x=174.432999, y=9.808371, z=0.275307), carla.Rotation(pitch=0.000000, yaw=90.855804, roll=0.000000)),
            ),
            'Town04': (
                carla.Transform(carla.Location(x=-13.030336, y=-140.432274, z=0.281942), carla.Rotation(pitch=0.000000, yaw=89.775162, roll=0.000000)),
                carla.Transform(carla.Location(x=-12.754474, y=-49.132839, z=0.281942), carla.Rotation(pitch=0.000000, yaw=179.775162, roll=0.000000)),
            ),
            'Town05': (
                carla.Transform(carla.Location(x=-128.395874, y=-42.550396, z=0.300000), carla.Rotation(pitch=0.000000, yaw=90.393547, roll=0.000000)),
                carla.Transform(carla.Location(x=-127.747406, y=53.414654, z=0.300000), carla.Rotation(pitch=0.000000, yaw=179.488602, roll=0.000000)),
            ),
        }
        args = argparser.parse_args()

        map_name = args.map
        main_vehicle_spawn_point, test_vehicle_spawn_point = points[map_name]
        vehicle_name = args.vehicle
        filename = args.filename

        # 创建client链接到Carla当中
        client = carla.Client('localhost', 2000)
        # 设置超时时间
        client.set_timeout(10.0)
        # 获取世界
        # world = client.get_world()
        world = client.load_world(map_name)
        # 设置天气
        weather = carla.WeatherParameters(
            #cloudiness=10.0,
            #precipitation=10.0,
            sun_altitude_angle=0
        )
        world.set_weather(weather)
        # 通过world获取world中的蓝图
        blueprint_library = world.get_blueprint_library()

        # 碰撞传感器
        collision_sensor_bp = blueprint_library.find('sensor.other.collision')
        #collision_sensor = world.spawn_actor(collision_sensor_bp, carla.Transform(), attach_to=my_vehicle)
        #collision_sensor_bp.listen(lambda event: parse_event(event))

        def parse_event(event):
            pass

        # 生成车辆
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.bmw.*'))
        test_vehicle_bp = random.choice(blueprint_library.filter(vehicle_name))
        my_vehicle = world.spawn_actor(vehicle_bp, main_vehicle_spawn_point)
        test_vehicle = world.try_spawn_actor(test_vehicle_bp, test_vehicle_spawn_point)

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
        my_camera = world.spawn_actor(camera_bp, camera_init, attach_to=my_vehicle)
        my_camera.listen(lambda image: parse_image(image, n=0))
        actor_list.extend((my_camera, my_vehicle, test_vehicle))

        def parse_image(image, n):
            global Image_Array
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]

            Image_Array = array

        # 车辆运动参数
        # my_vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=0))
        my_vehicle.enable_constant_velocity(carla.Vector3D(5, 0, 0))

        width, height = int(image_size_x), int(image_size_y)  # 宽高
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 视频编解码器
        # fps = 40
        fps = 30
        writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        try:
            i = 0
            while True:
                if Image_Array is not None:
                    i += 1
                    image = copy.copy(Image_Array)
                    if 10 <= i <= 300:
                        writer.write(image)
                    if i > 300:
                        break
                    cv2.imshow('Carla Tutorial', image)
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                        break
        finally:
            writer.release()

    finally:
        for actor in actor_list:
            actor.destroy()
            print(actor.id, ' is destroyed')


if __name__ == '__main__':
    Image_Array = None
    main()
