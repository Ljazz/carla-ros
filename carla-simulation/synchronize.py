"""
 Author         : maxiaoming
 Date           : 2022-07-18 11:48:33
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-18 14:40:12
 FilePath       : synchronize.py
 Description    : 同步模式
"""
import random
import sys
from queue import Empty, Queue

sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

import carla


def sensor_callback(sensor_data, sensor_queue, sensor_name):
    if 'lidar' in sensor_name:
        sensor_data.save_to_disk('./outputs/output_synchronized/%06d.ply' % sensor_data.frame)
    if 'camera' in sensor_name:
        sensor_data.save_to_disk('./outputs/output_synchronized/%06d.png' % sensor_data.frame)
    sensor_queue.put((sensor_data.frame, sensor_name))


def main():
    actor_list = []
    sensor_list = []
    try:
        # 创建客户端并设置超时时间
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)

        # 获取正在运行的仿真世界
        world = client.get_world()
        # 获取仿真世界的蓝图库
        blueprint_library = world.get_blueprint_library()
        # 设置仿真世界的天气
        weather = carla.WeatherParameters(
            cloudiness=10.0,
            precipitation=10.0,
            fog_density=10.0
        )
        world.set_weather(weather)

        # 设置同步模式
        original_settings = world.get_settings()
        settings = world.get_settings()
        settings.fixec_delta_seconds = 0.05
        settings.synchronous_mode = True
        world.apply_settings(settings)

        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)

        sensor_queue = Queue()

        # 添加车辆
        ego_vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        ego_vehicle_bp.set_attribute('color', '0, 0, 0')
        transform = world.get_map().get_spawn_points()[80]
        ego_vehicle = world.spawn_actor(ego_vehicle_bp, transform)
        ego_vehicle.set_autopilot(True)
        actor_list.append(ego_vehicle)

        # 添加相机
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)
        camera.listen(lambda image: sensor_callback(image, sensor_queue, "camera"))
        sensor_list.append(camera)

        # lidar
        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('channels', str(32))
        lidar_bp.set_attribute('points_per_second', str(90000))
        lidar_bp.set_attribute('rotation_frequency', str(40))
        lidar_bp.set_attribute('range', str(20))

        lidar_location = carla.Location(0, 0, 2)
        lidar_rotation = carla.Rotation(0, 0, 0)
        lidar_transform = carla.Transform(lidar_location, lidar_rotation)
        lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=ego_vehicle)
        lidar.listen(lambda point_cloud: sensor_callback(point_cloud, sensor_queue, 'lidar'))
        sensor_list.append(lidar)

        while True:
            world.tick()
            spectator = world.get_spectator()
            transform = ego_vehicle.get_transform()

            spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20),
                                                    carla.Rotation(pitch=-90)))

            try:
                for _ in sensor_list:
                    s_frame = sensor_queue.get(True, 1.0)
                    print("    Frame: %d   Sensor: %s" % (s_frame[0], s_frame[1]))

            except Empty:
                print("   Some of the sensor information is missed")
    finally:
        world.apply_settings(original_settings)
        print("destroying actors")
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        for sensor in sensor_list:
            sensor.destroy()
        print('done.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exited by user.')
