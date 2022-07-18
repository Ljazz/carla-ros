"""
 Author         : maxiaoming
 Date           : 2022-07-18 11:05:30
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-18 11:31:52
 FilePath       : basic_api.py
 Description    : 基本API使用
"""
import sys
import time

sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

import carla


def main():
    actor_list = []
    sensor_list = []

    try:
        # 创建客户端
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)     # 设置超时时间

        # 获取正在运行的仿真世界
        world = client.get_world()
        # 加载特定的仿真世界
        # world = client.load_world('Town02')

        # 设置天气
        weather = carla.WeatherParameters(
            cloudiness=10.0,
            precipitation=10.0,
            fog_density=10.0
        )
        world.set_weather(weather)

        # 获取仿真世界的所有物体的蓝图
        blueprint_library = world.get_blueprint_library()

        # 找特斯拉的蓝图
        ego_vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        # 给车辆加上特定颜色
        ego_vehicle_bp.set_attribute('color', '0,0,0')

        # 找到所有出生点，并随机选择一个
        # transform = random.choice(world.get_map().get_spawn_points())
        transform = world.get_map().get_spawn_points()[80]
        # 生成车辆
        ego_vehicle = world.spawn_actor(ego_vehicle_bp, transform)
        # 设置车辆自动驾驶
        ego_vehicle.set_autopilot(True)
        actor_list.append(ego_vehicle)

        # 手动移动移动车辆
        # location = ego_vehicle.get_location()
        # location.x += 10
        # ego_vehicle.set_location(location)  # 设置车辆位置
        # 中途通过抹杀车辆的物理仿真“冻住”车辆
        # time.sleep(3)
        # ego_vehicle.set_simulate_physics(False)

        # rgb相机
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)
        camera.listen(lambda image: image.save_to_disk('./output/rgb/%06d.png' % image.frame))
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
        lidar.listen(lambda point_cloud: point_cloud.save_to_disk('./output/lidar/%06d.ply' % point_cloud.frame))
        sensor_list.append(lidar)

        while True:
            spectator = world.get_spectator()
            transform = ego_vehicle.get_transform()
            spectator.set_transform(carla.Transform(transform.location +
                                    carla.Location(z=20), carla.Rotation(pitch=-90)))

    finally:
        print('destroying actors')
        # 批量销毁
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        # 注销单个
        for sensor in sensor_list:
            sensor.destroy()
        print('done.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' - Exited by user.')
