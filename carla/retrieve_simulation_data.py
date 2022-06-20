"""
 Author         : maxiaoming
 Date           : 2022-06-20 11:38:34
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-06-20 15:42:43
 FilePath       : retrieve_simulation_data.py
 Description    : 检索模拟数据
"""
import logging
import math
import random
import carla

try:
    actor_list = []

    client = carla.Client("localhost", 2000)
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    # ------------------------------------------------------------
    # 生成 model3 车辆
    # ------------------------------------------------------------
    # 查找 model3 蓝图
    model3_bp = blueprint_library.find("vehicle.tesla.model3")
    # 为 model3 设置 role_name 属性
    model3_bp.set_attribute("role_name", "model3")
    print("model3 role_name is setted.")
    model3_color = random.choice(model3_bp.get_attribute("color").recommended_values)
    # 为 model3 设置颜色属性
    # model3_bp.set_attribute("color", model3_color)
    model3_bp.set_attribute("color", "255,255,0")
    print("model3 color is setted.")

    # 推荐的生成点
    spawn_points = world.get_map().get_spawn_points()
    number_of_spawn_points = len(spawn_points)
    if number_of_spawn_points > 0:
        random.shuffle(spawn_points)
        model3_transform = spawn_points[0]
        # 生成 model3 车辆
        model3_vehicle = world.spawn_actor(model3_bp, model3_transform)
        print("model3 vehicle has been created.")
        actor_list.append(model3_vehicle)
    else:
        logging.warning("Could not found any spawn points.")

    # ------------------------------------------------------------
    # 天气
    # ------------------------------------------------------------
    weather = carla.WeatherParameters(
        cloudiness=0.0,         # 云彩， 0表示天空，100表示完全被云覆盖
        precipitation=50.0,     # 降雨强度，0完全没有，100大雨
        wind_intensity=0,       # 风，0完全没有，100强风
        sun_azimuth_angle=0,    # 太阳的方位角。值范围从 0 到 360
        sun_altitude_angle=0,   # 太阳的高度角。值范围从 -90 到 90，分别对应于午夜和中午
        
    )
    weather = world.get_weather()
    weather.sun_altitude_angle = -30
    weather.fog_density = 65
    weather.fog_distance = 10
    world.set_weather(weather)

    # ------------------------------------------------------------
    # 观察者
    # ------------------------------------------------------------
    spectator = world.get_spectator()
    world_snapshot = world.wait_for_tick()
    spectator.set_transform(model3_vehicle.get_transform())

    # ------------------------------------------------------------
    # 生成附加的 RGB相机
    # ------------------------------------------------------------
    IMAGE_SIZE_X = 1920
    IMAGE_SIZE_Y = 1080
    # 查找 rgb相机 蓝图
    rgb_camera_bp = blueprint_library.find("sensor.camera.rgb")
    # 设置图像分辨率
    rgb_camera_bp.set_attribute("image_size_x", str(IMAGE_SIZE_X))
    rgb_camera_bp.set_attribute("image_size_y", str(IMAGE_SIZE_Y))
    # 设置视野
    rgb_camera_bp.set_attribute("fov", str(110))
    cam_location = carla.Location(2, 0, 1)
    cam_rotation = carla.Rotation(0, 180, 0)
    cam_transform = carla.Transform(cam_location, cam_rotation)
    rgb_camera = world.spawn_actor(rgb_camera_bp, cam_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmentType.Rigid)
    print("RGB camera has been created.")
    actor_list.append(rgb_camera)
    rgb_camera.listen(lambda image: image.save_to_disk("output/%.6d.jpg" % image.frame))

    # ------------------------------------------------------------
    # 添加 碰撞传感器
    # ------------------------------------------------------------
    collision_bp = blueprint_library.find("sensor.other.collision")
    col_location = carla.Location(0, 0, 0)
    col_rotation = carla.Rotation(0, 0, 0)
    col_transform = carla.Transform(col_location, col_rotation)
    collision = world.spawn_actor(collision_bp, col_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmentType.Rigid)
    print("Collision has been created.")
    actor_list.append(collision)
    collision.listen(lambda event: collision_callback(event))
    
    def collision_callback(event):
        print(f"Collision detected:\n\t{event}")

    # ------------------------------------------------------------
    # 车道入侵传感器
    # ------------------------------------------------------------
    lane_bp = blueprint_library.find("sensor.other.lane_invasion")
    lane_location = carla.Location(0, 0, 0)
    lane_rotation = carla.Rotation(0, 0, 0)
    lane_transform = carla.Transform(lane_location, lane_rotation)
    lane_invasion = world.spawn_actor(lane_bp, lane_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmentType.Rigid)
    print("Lane invasion has been created.")
    actor_list.append(lane_invasion)
    lane_invasion.listen(lambda event: lane_callback(event))
    
    def lane_callback(event):
        print(f"Lane invasion detected:\n\t{event}")

    # ------------------------------------------------------------
    # 障碍物传感器
    # ------------------------------------------------------------
    obstacle_bp = blueprint_library.find("sensor.other.obstacle")
    # 确定是否应考虑静态对象
    obstacle_bp.set_attribute("only_dynamics", str(True))
    obstacle_location = carla.Location(0, 0, 0)
    obstacle_rotation = carla.Rotation(0, 0, 0)
    obstacle_transform = carla.Transform(obstacle_location, obstacle_rotation)
    obstacle = world.spawn_actor(obstacle_bp, obstacle_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmenType.Rigid)
    print("Obstacle has been created.")
    actor_list.append(obstacle)
    obstacle.listen(lambda event: obstacle_callback(event))
    
    def obstacle_callback(event):
        print(f"Obstacle detected:\n\t{event}")

    # ------------------------------------------------------------
    # 全球导航卫星系统传感器
    # ------------------------------------------------------------
    gnss_bp = blueprint_library.find("sensor.other.gnss")
    # 传感器捕获（滴答声）之间的模拟秒数
    gnss_bp.set_attribute("sensor_tick", str(3.0))
    gnss_location = carla.Location(0, 0, 0)
    gnss_rotation = carla.Rotation(0, 0, 0)
    gnss_transform = carla.Transform(gnss_location, gnss_rotation)
    gnss = world.spawn_actor(gnss_bp, gnss_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmenType.Rigid)
    print("GNSS has been created.")
    actor_list.append(gnss)
    gnss.listen(lambda event: gnss_callback(event))
    
    def gnss_callback(event):
        print(f"Gnss detected:\n\t{event}")

    # ------------------------------------------------------------
    # IMU传感器
    # ------------------------------------------------------------
    imu_bp = blueprint_library.find("sensor.other.imu")
    # 传感器捕获（滴答声）之间的模拟秒数
    imu_bp.set_attribute("sensor_tick", str(3.0))
    imu_location = carla.Location(0, 0, 0)
    imu_rotation = carla.Rotation(0, 0, 0)
    imu_transform = carla.Transform(imu_location, imu_rotation)
    imu = world.spawn_actor(imu_bp, imu_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmenType.Rigid)
    print("IMU has been created.")
    actor_list.append(imu)
    imu.listen(lambda event: imu_callback(event))
    
    def imu_callback(event):
        print(f"Imu detected:\n\t{event}")

    # ------------------------------------------------------------
    # 添加深度相机
    # ------------------------------------------------------------
    depth_camera_bp = blueprint_library.find("sensor.camera.depth")
    depth_location = carla.Location(2, 0, 1)
    depth_rotation = carla.Rotation(0, 180, 0)
    depth_transform = carla.Transform(depth_location, depth_rotation)
    depth_camera = world.spawn_actor(depth_camera_bp, depth_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmentType.Rigid)
    print("Depth camera has been created.")
    actor_list.append(depth_camera)
    # 对图像应用颜色转换器，得到语义分割视图
    depth_camera.listen(lambda image: image.save_to_disk("new_depth_output/%.6d.jpg" % image.frame, carla.ColorConverter.LogarithmicDepth))
    
    # ------------------------------------------------------------
    # 语义分割相机
    # ------------------------------------------------------------
    IMAGE_SIZE_X = 1920
    IMAGE_SIZE_Y = 1080
    semantic_segmentation_camera_bp = blueprint_library.find("sensor.camera.semantic_segmentation")
    semantic_segmentation_camera_bp.set_attribute("image_size_x", str(IMAGE_SIZE_X))
    semantic_segmentation_camera_bp.set_attribute("image_size_y", str(IMAGE_SIZE_Y))
    semantic_segmentation_camera_bp.set_attribute("fov", str(110))
    sem_location = carla.Location(2, 0, 1)
    sem_rotation = carla.Rotation(0, 180, 0)
    sem_transform = carla.Transform(sem_location, sem_rotation)
    semantic_segmentation_camera = world.spawn_actor(semantic_segmentation_camera_bp, sem_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmentType.Rigid)
    print("Semantic segmentation camera has been created.")
    actor_list.append(semantic_segmentation_camera)
    # 对图像应用颜色转换器，得到语义分割视图
    semantic_segmentation_camera.listen(lambda image: image.save_to_disk("new_sem_output/%.6d.jpg" % image.frame,carla.ColorConverter.CityScapesPalette))

    # ------------------------------------------------------------
    # 激光雷达传感器
    # ------------------------------------------------------------
    lidar_bp = blueprint_library.find("sensor.lidar.ray_cast")
    # 激光量
    lidar_bp.set_attribute("channels", str(32))
    # 每秒获得的点数
    lidar_bp.set_attribute("points_per_second", str(90000))
    # 激光雷达每秒旋转的次数
    lidar_bp.set_attribute("rotation_frequency", str(40))
    # 获取的最大距离
    lidar_bp.set_attribute("range", str(20))
    lidar_location = carla.Location(0, 0, 2)
    lidar_rotation = carla.Rotation(0, 0, 0)
    lidar_transform = carla.Transform(lidar_location, lidar_rotation)
    lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=model3_vehicle)
    print("Lidar camera has been created.")
    actor_list.append(lidar)
    lidar.listen(lambda point_cloud: point_cloud.save_to_disk("new_lidar_output/%.6d.ply" % point_cloud.frame))
    
    # ------------------------------------------------------------
    # 雷达传感器
    # ------------------------------------------------------------
    radar_bp = blueprint_library.find("sensor.other.radar")
    radar_bp.set_attribute("horizontal_fov", str(35))
    radar_bp.set_attribute("vertical_fov", str(20))
    radar_bp.set_attribute("range", str(20))
    radar_location = carla.Location(x=2.0, z=1.0)
    radar_rotation = carla.Rotation(pitch=5)
    radar_transform = carla.Transform(radar_location, radar_location)
    radar = world.spawn_actor(radar_bp, radar_transform, attach_to=model3_vehicle, attachment_type=carla.AttachmentType.Rigid)
    print("Radar has been created.")
    actor_list.append(radar)
    radar.listen(lambda radar_data: radar_callback(radar_data))
    def radar_callback(radar_data):
        velocity_range = 7.5 # m/s
        current_rot = radar_data.transform.rotation
        for detect in radar_data:
            azi = math.degrees(detect.azimuth)
            alt = math.degrees(detect.altitude)
            # 0.25 调整一点距离，所以点可以被正确看到
            fw_vec = carla.Vector3D(x=detect.depth - 0.25)
            carla.Transform(
                carla.Location(),
                carla.Rotation(
                    pitch=current_rot.pitch + alt,
                    yaw=current_rot.yaw + azi,
                    roll=current_rot.roll
                )
            ).transform(fw_vec)
            
            def clamp(min_v, max_v, value):
                return max(min_v, min(value, max_v))
            
            norm_velocity = detect.velocity / velocity_range  # range [-1, 1]
            r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
            g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
            b = int(abs(clamp(-1.0, 0.0, -1.0 - norm_velocity)) * 255.0)
            world.debug.draw_point(
                radar_data.transform.location + fw_vec,
                size=0.075,
                life_time=0.06,
                persistent_lines=False,
                color=carla.Color(r, g, b)
            )
finally:
    for actor in actor_list:
        actor.destroy()