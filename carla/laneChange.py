"""
 Author         : maxiaoming
 Date           : 2022-06-22 10:39:50
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-11 10:41:44
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
sys.path.append("/home/realai/zhujianwei/vehicle_automation/realautomation/yolov3")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/realautomation/mmdetection3d")


import carla


def get_speed(vehicle):
    vel = vehicle.get_velocity()
    return 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)


class VehiclePIDController():
    def __init__(self, vehicle, args_lateral, args_longitudnal, max_throttle=0.75, max_break=0.3, max_steering=0.8) -> None:
        self.max_break = max_break
        self.max_steering = max_steering
        self.max_throttle = max_throttle

        self.vehicle = vehicle
        self.world = vehicle.get_world()
        self.past_steering = self.vehicle.get_control().steer
        self.long_controller = PIDLongitudnalControl(self.vehicle, **args_longitudnal)
        self.lat_controller = PIDLateralControl(self.vehicle, **args_lateral)

    def run_step(self, target_speed, waypoint):
        acceleration = self.long_controller.run_step(target_speed)
        current_steering = self.lat_controller.run_step(waypoint)
        control = carla.VehicleControl()

        if acceleration >= 0.0:
            control.throttle = min(abs(acceleration), self.max_break)
            control.brake = 0.0
        else:
            control.throttle = 0.0
            control.brake = min(abs(acceleration), self.max_break)

        if current_steering > self.past_steering + 0.1:
            current_steering = self.past_steering + 0.1
        elif current_steering < self.past_steering - 0.1:
            current_steering = self.past_steering - 0.1

        if current_steering >= 0:
            steering = min(self.max_steering, current_steering)
        else:
            steering = max(-self.max_steering, current_steering)

        control.steer = steering
        control.hand_brake = False
        control.manual_gear_shift = False
        self.past_steering = steering

        return control


class PIDLongitudnalControl():
    def __init__(self, vehicle, K_P=1.0, K_D=0.0, K_I=0.0, dt=0.03) -> None:
        self.vehicle = vehicle
        self.K_D = K_D
        self.K_P = K_P
        self.K_I = K_I
        self.dt = dt
        self.errorBuffer = queue.deque(maxlen=10)

    def run_step(self, target_speed):
        current_speed = get_speed(self.vehicle)
        return self.pid_controller(target_speed, current_speed)

    def pid_controller(self, target_speed, current_speed):
        error = target_speed - current_speed
        self.errorBuffer.append(error)

        if len(self.errorBuffer) >= 2:
            de = (self.errorBuffer[-1] - self.errorBuffer[-2]) / self.dt
            ie = sum(self.errorBuffer) * self.dt
        else:
            de = 0.0
            ie = 0.0
        return np.clip(self.K_P * error + self.K_D * de + self.K_I * ie, -1.0, 1.0)


class PIDLateralControl():
    def __init__(self, vehicle, K_P=1.0, K_D=0.0, K_I=0.0, dt=0.03) -> None:
        self.vehicle = vehicle
        self.K_D = K_D
        self.K_P = K_P
        self.K_I = K_I
        self.dt = dt
        self.errorBuffer = queue.deque(maxlen=10)

    def run_step(self, waypoint):
        return self.pid_controller(waypoint, self.vehicle.get_transform())

    def pid_controller(self, waypoint, vehicle_transform):
        v_begin = vehicle_transform.location
        v_end = v_begin + carla.Location(x=math.cos(math.radians(vehicle_transform.rotation.yaw)),
                                         y=math.sin(math.radians(vehicle_transform.rotation.yaw)))
        v_vec = np.array([v_end.x - v_begin.x, v_end.y - v_begin.y, 0.0])
        w_vec = np.array([waypoint.transform.location.x - v_begin.x, waypoint.transform.y - v_begin.y, 0.0])

        dot = math.acos(np.clip(np.dot(w_vec, v_vec) / np.linalg.norm(w_vec) * np.linalg.norm(v_vec), -1.0, 1.0))
        cross = np.cross(v_vec, w_vec)
        if cross[2] < 0:
            dot *= -1

        self.errorBuffer.append(dot)

        if len(self.errorBuffer) >= 2:
            de = (self.errorBuffer[-1] - self.errorBuffer[-2]) / self.dt
            ie = sum(self.errorBuffer) * self.dt
        else:
            de = 0.0
            ie = 0.0

        return np.clip((self.K_P * dot) + (self.K_I * ie) + (self.K_D * de), -1.0, 1.0)


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
        world = client.load_world("Town04")
        weather = carla.WeatherParameters(
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

        my_camera.listen(lambda image: parse_image(image, n=0))

        actor_list.extend((my_camera, my_vehicle))

        def parse_image(image, n):
            global Image_Array
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]

            Image_Array = array

        # 车辆运动参数
        # my_vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=0))
        my_vehicle.enable_constant_velocity(carla.Vector3D(2.5, 0, 0))
        my_vehicle.set_autopilot(True)
        limit_speed = my_vehicle.get_speed_limit()
        print("limit_speed => ", limit_speed)

        control_vehicle = VehiclePIDController(my_vehicle, args_lateral={'K_P': 1, 'K_D': 0.0, 'K_I': 0.0},
                                               args_longitudnal={'K_P': 1, 'K_D': 0.0, 'K_I': 0.0})

        # bian dao canshu
        tm = client.get_trafficmanager()
        location = carla.Location(x=-9.895893, y=-212.574677, z=0.281942)
        current_w = world.get_map().get_waypoint(location)
        print("current_w ==> ", current_w)
        print("current_w->next", current_w.next(1))
        print(current_w.lane_change)
        print(carla.LaneChange.Right)

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

                    # if cv2.waitKey(25) & 0xFF == ord('a'):
                    #     if current_w.lane_change & carla.LaneChange.Right:
                    #         right_w = current_w.get_right_lane()
                    #         if right_w and right_w.lane_type == carla.LaneType.Driving:
                    #             print('change right')
                    #             tm.force_lane_change(my_vehicle, True)

                    #             next_w = world.get_map().get_waypoint(my_vehicle.get_location())
                    #             location = next_w.get_right_lane()
                    #             print("location => ", location)
                    if cv2.waitKey(25) & 0xFF == ord('a'):
                        waypoints = world.get_map().get_waypoint(my_vehicle.get_location())
                        waypoint = waypoints.next(0.3)[0]
                        control_signal = control_vehicle.run_step(5, waypoint)
                        my_vehicle.apply_control(control_signal)
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
