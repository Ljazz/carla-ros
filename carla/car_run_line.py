"""
 Author         : maxiaoming
 Date           : 2022-06-22 10:39:50
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-04 11:35:11
 FilePath       : car_run_line.py
 Description    : Carla车辆跑直线并录视频
"""
import argparse
import copy
import random

import cv2
import numpy as np

import carla


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

        points = {
            'Town01': (carla.Transform(carla.Location(x=295.081757, y=199.060303, z=0.300000), carla.Rotation(pitch=0.000000, yaw=-0.000092, roll=0.000000)), carla.Transform(carla.Location(x=142.360550, y=198.759995, z=0.300000), carla.Rotation(pitch=0.000000, yaw=-0.000092, roll=0.000000))),
            'Town02': (carla.Transform(carla.Location(x=189.929993, y=142.190002, z=0.500000), carla.Rotation(pitch=0.000000, yaw=89.999954, roll=0.000000)), carla.Transform(carla.Location(x=189.929993, y=293.540009, z=0.500000), carla.Rotation(pitch=0.000000, yaw=89.999954, roll=0.000000))),
            'Town03': (carla.Transform(carla.Location(x=-18.582256, y=-204.674316, z=0.275307), carla.Rotation(pitch=0.000000, yaw=-178.560471, roll=0.000000)), carla.Transform(carla.Location(x=129.905441, y=-201.210129, z=0.275307), carla.Rotation(pitch=0.000000, yaw=-178.560471, roll=0.000000))),
            'Town04': (carla.Transform(carla.Location(x=-9.890791, y=-211.274689, z=0.281942), carla.Rotation(pitch=0.000000, yaw=89.775124, roll=0.000000)), carla.Transform(carla.Location(x=-8.437963, y=128.214111, z=0.281942), carla.Rotation(pitch=0.000000, yaw=89.710899, roll=0.000000))),
            'Town05': (carla.Transform(carla.Location(x=28.046694, y=163.645676, z=0.300000), carla.Rotation(pitch=0.000000, yaw=90.022896, roll=0.000000)), carla.Transform(carla.Location(x=32.147095, y=-176.243668, z=0.300000), carla.Rotation(pitch=0.000000, yaw=91.532082, roll=0.000000))),
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
        town01_weather = carla.WeatherParameters(
            # cloudiness=60.000000,               # 云彩。0～100，0 表示晴朗的天空，100 表示完全被云覆盖。
            precipitation=50.000000,            # 降雨量。0～100，0 完全没有，100 大雨。
            # precipitation_deposits=40.000000,   # 水坑的创建。0～100，0 完全没有，100 道路完全被水覆盖。
            # wind_intensity=10.000000,           # 风的强度。0～100， 0 表示完全没有风，100 强风。
            # sun_azimuth_angle=275.000000,       # 太阳方位角。0～360.
            sun_altitude_angle=0.000000,       # 太阳的高度角。-90～90，分别对应午夜和中午。
            # fog_density=5.000000,               # 雾的浓度或厚度。0～100，只影响RGB相机传感器。
            # fog_distance=0.750000,              # 雾开始距离。0～∞
            # fog_falloff=0.100000,               # 雾的密度 0:雾会比空气轻，并且会覆盖整个场景；1:大约与空气一样稠密，并达到正常大小的建筑物；>5:空气将非常稠密，以至于在地面上会被压缩
            wetness=80.000000,                  # 湿度。0～100，只影响RGB相机传感器
            # scattering_intensity=1.000000,      # 控制光对体积雾的贡献程度。0时，没有贡献
            # mie_scattering_scale=0.030000,      # 控制光与花粉或空气污染等大颗粒的相互作用，从而导致光源周围有光晕的朦胧天空。0时，没有贡献
            # rayleigh_scattering_scale=0.033100,  # 控制光与空气分子等小颗粒的相互作用
            # dust_storm=20,                      # 沙尘暴强度。0～100
        )
        town04_weather = carla.WeatherParameters(
            # cloudiness=10.0,
            # sun_azimuth_angle=150.0,
            sun_altitude_angle=0,
            fog_density=40.000000,
            fog_distance=60.000000,
            fog_falloff=2.000000,
            # wetness=30.000000,
            # scattering_intensity=1.000000,
        )
        weather = carla.WeatherParameters(
            # cloudiness=10.0,
            # precipitation=10.0,
            sun_altitude_angle=0
        )
        if map_name == 'Town01':
            weather = town01_weather
        if map_name == 'Town04':
            weather = town04_weather
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
        vehicle_bp = blueprint_library.find('vehicle.bmw.grandtourer')
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
        # my_vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=0))  # 油门控制
        my_vehicle.enable_constant_velocity(carla.Vector3D(3, 0, 0))

        width, height = int(image_size_x), int(image_size_y)  # 宽高
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 视频编解码器
        # fps = 30
        fps = 24
        writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        try:
            i = 0
            while True:
                if Image_Array is not None:
                    i += 1
                    image = copy.copy(Image_Array)
                    if 21 <= i <= 260:
                        writer.write(image)
                    if i > 250:
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
