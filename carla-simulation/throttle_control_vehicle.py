"""
 Author         : maxiaoming
 Date           : 2022-06-22 10:39:50
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-13 15:05:35
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

VEHICLE_VEL = 5


class PIDControl():
    def __init__(self, world, vehicle, vel_ref=VEHICLE_VEL, max_throttle=0.75, max_brake=0.3, max_steer=0.8):
        self.world = world
        self.max_throttle = max_throttle
        self.max_brake = max_brake
        self.max_steer = max_steer
        self.vehicle = vehicle
        self.spectator = world.get_spectator()

        dt = 1.0 / 20.0
        args_lateral_dict = {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': dt}
        args_longitudinal_dict = {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0, 'dt': dt}
        offset = 0

        self.controller = VehiclePIDController(
            self.vehicle,
            args_lateral=args_lateral_dict,
            args_longitudinal=args_longitudinal_dict,
            offset=offset,
            max_throttle=max_throttle,
            max_brake=max_brake,
            max_steering=max_steer,
        )
        self.vel_ref = vel_ref
        self.waypointsList = []
        self.current_pos = self.vehicle.get_transform().location
        self.past_pos = self.vehicle.get_transform().location

    def dist2waypoint(self, waypoint):
        vehicle_transform = self.vehicle_get_transform()
        vehicle_x = vehicle_transform.location.x
        vehicle_y = vehicle_transform.location.y
        waypoint_x = waypoint.transform.location.x
        waypoint_y = waypoint.transform.location.y
        return math.sqrt((vehicle_x - waypoint_x) ** 2 + (vehicle_y - waypoint_y) ** 2)

    def go2waypoint(self, waypoint, draw_waypoint=True, threshold=0.3):
        if draw_waypoint:
            self.world.debug.draw_string(waypoint.transform.location, '0', draw_shadow=False,
                                         color=carla.Color(r=255, g=0, b=0), life_time=10.0,
                                         persistent_lines=True)
        current_pos_np = np.array([self.current_pos.x, self.current_pos.y])
        past_pos_np = np.array([self.past_pos.x, self.past_pos.y])
        waypoint_np = np.array([waypoint.transform.location.x, waypoint.transform.location.y])
        vec2wp = waypoint_np - current_pos_np
        motion_vec = current_pos_np - past_pos_np
        dot = np.dot(vec2wp, motion_vec)
        if (dot >= 0):
            while self.dist2waypoint(waypoint) > threshold:
                control_signal = self.controller.run_step(self.vel_ref, waypoint)
                self.vehicle.apply_control(control_signal)
                self.update_spectator()

    def getLeftLaneWaypoints(self, offset=2 * VEHICLE_VEL, separation=0.3):
        current_waypoint = self.world.get_map().get_waypoint(self.vehicle.get_location())
        left_lane = current_waypoint.get_left_lane()
        self.waypointsList = left_lane.previous(offset)[0].previous_until_lane_start(separation)

    def getRightLaneWaypoints(self, offset=2 * VEHICLE_VEL, separation=0.3):
        current_waypoint = self.world.get_map().get_waypoint(self.vehicle.get_location())
        right_lane = current_waypoint.get_left_lane()
        self.waypointsList = right_lane.next(offset)[0].next_until_lane_end(separation)

    def do_left_lane_change(self):
        self.getLeftLaneWaypoints()
        for i in range(len(self.waypointsList) - 1):
            self.current_pos = self.vehicle.get_location()
            self.go2waypoint(self.waypointsList[i])
            self.past_pos = self.current_pos
            self.update_spectator()

    def do_right_lane_change(self):
        self.getRightLaneWaypoints()
        for i in range(len(self.waypointsList) - 1):
            self.current_pos = self.vehicle.get_location()
            self.go2waypoint(self.waypointsList[i])
            self.past_pos = self.current_pos
            self.update_spectator()

    def update_spectator(self):
        new_yaw = math.radians(self.vehicle.get_transform().rotation.yaw)
        spectator_transform = self.vehicle.get_transform()
        spectator_transform.location += carla.Location(x=-10 * math.cos(new_yaw), y=-10 * math.sin(new_yaw), z=5.0)

        self.spectator.set_transform(spectator_transform)
        self.world.tick()

    def is_waypoint_in_direction_of_motion(self, waypoint):
        current_pos = self.vehicle.get_location()

    def draw_waypoints(self):
        for waypoint in self.waypointsList:
            self.world.debug.draw_string(waypoint.transform.location, 'O', draw_shadow=False,
                                         color=carla.Color(r=255, g=0, b=0), life_time=10.0,
                                         persistent_lines=True)


def main():
    """
        主函数
    """
    # 存储生成的actor
    actor_list = []
    try:
        # 创建client链接到Carla当中
        client = carla.Client('localhost', 2000)
        # 设置超时时间
        client.set_timeout(10.0)
        # 获取世界
        world = client.get_world()
        spectator = world.get_spectator()
        actor_list.append(spectator)
        # weather = carla.WeatherParameters(
        #     sun_altitude_angle=0
        # )
        # world.set_weather(weather)
        # 通过world获取world中的蓝图
        blueprint_library = world.get_blueprint_library()
        spawn_points = world.get_map().get_spawn_points()

        # 生成车辆
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.bmw.grandtourer'))
        model3_spawn_point = spawn_points[81]
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

        my_camera = world.spawn_actor(camera_bp, camera_init, attach_to=my_vehicle)

        my_camera.listen(lambda image: parse_image(image))

        def parse_image(self):
            global Image_Array
            array = np.frombuffer(self.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (self.height, self.width, 4))
            array = array[:, :, :3]

            Image_Array = array

        actor_list.extend((my_camera, my_vehicle))

        # 碰撞传感器
        collision_sensor_bp = blueprint_library.find('sensor.other.collision')
        collision_sensor = world.spawn_actor(collision_sensor_bp, carla.Transform(), attach_to=my_vehicle)
        collision_sensor.listen(lambda event: parse_event(event))

        def parse_event(event):
            print(event)
            print("碰。。。")

        actor_list.append(collision_sensor)

        # 车辆运动参数
        # my_vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=0))
        my_vehicle.enable_constant_velocity(carla.Vector3D(2.5, 0, 0))

        width, height = int(image_size_x), int(image_size_y)  # 宽高
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 视频编解码器
        # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        # fps = 40
        fps = 30
        writer = cv2.VideoWriter('result.mp4', fourcc, fps, (width, height))
        try:
            i = 0
            while True:
                if Image_Array is not None:
                    i += 1
                    image = copy.copy(Image_Array)
                    if 1 <= i <= 600:
                        writer.write(image)
                    cv2.imshow('Carla Tutorial', image)
                    if cv2.waitKey(25) & 0xFF == ord('a'):
                        my_vehicle.apply_control(carla.VehicleControl(steer=1))
                        time.sleep(1)
                        my_vehicle.apply_control(carla.VehicleControl(steer=-1))
                        time.sleep(1)
                        my_vehicle.apply_control(carla.VehicleControl(steer=0))
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
