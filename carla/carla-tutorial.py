"""
 Author         : maxiaoming
 Date           : 2022-06-21 10:34:13
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-06-24 18:43:44
 FilePath       : carla-tutorial.py
 Description    : carla整合
"""

import copy
import math
import random
import time
from typing import Dict
import cv2
import numpy as np
from pyparsing import Optional
import carla
import contextlib


# ====================================================================================================
# -- 全局函数 -----------------------------------------------------------------------------------------
# ====================================================================================================


def get_actor_blueprints(world, filter: str, generation: str):
    """获取actor蓝图

    Args:
        world (_type_): 世界对象
        filter (str): 需要筛选的蓝图对象
        generation (str): _description_

    Returns:
        _type_: _description_
    """
    bps = world.get_blueprint_library().filter(filter)

    if generation == "all":
        return bps

    if len(bps) == 1:
        return bps

    with contextlib.suppress(Exception):
        int_generation = int(generation)
        if int_generation in {1, 2}:
            bps = [x for x in bps if int(x.get_attribute("generation")) == int_generation]
            return bps
        else:
            print("Warning! acotr")


# ====================================================================================================
# -- Opencv 生成视频 ----------------------------------------------------------------------------------
# ====================================================================================================
class GenerateVideo:
    def __init__(self, fps=40, width=1080, height=1920) -> None:
        self._fps = fps
        self._width = width
        self._height = height

    def save_video(self, filename, data):
        # fourcc = cv2.VideoWriter_fourcc(*"XVID")
        # writer = cv2.VideoWriter(f"{filename}.avi", fourcc, self._fps, (self._width, self._height))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(f"{filename}.mp4", fourcc, self._fps, (self._width, self._height), True)
        try:
            print("writer...")
            while True:
                if data:
                    frame = copy.copy(data)
                    writer.write(frame)  # 写入帧
                    cv2.imshow("Carla Tutorial", frame)
                    if cv2.waitKey(25) & 0xFF == ord("q"):
                        cv2.destroyAllWindows()
        finally:
            writer.release()


# ====================================================================================================
# -- Weather -----------------------------------------------------------------------------------------
# ====================================================================================================
class Sun(object):
    """晴天☀️"""

    def __init__(self, azimuth, altitude) -> None:
        self.azimuth = azimuth
        self.altitude = altitude
        self._t = 0.0

    def tick(self, delta_seconds):
        self._t += 0.008 * delta_seconds
        self._t %= 2.0 * math.pi
        self.azimuth += 0.25 * delta_seconds
        self.azimuth %= 360.0
        self.altitude = (70 * math.sin(self._t)) - 20

    def __str__(self) -> str:
        return f"Sun(alt: {round(self.altitude, 2)}, azm: {round(self.azimuth, 2)})"


# ====================================================================================================
# -- World -------------------------------------------------------------------------------------------
# ====================================================================================================
class CarlaWorld(object):
    def __init__(self, carla_world) -> None:
        self.world = carla_world
        self.bluteprint_library = self.world.get_blueprint_library()

    def set_weather(self, weather):
        """设置天气"""
        self.world.set_weather(weather)

    def generate_vehicle(self, vehicle_filter: str, spawn_point: Optional[carla.Transform] = None):
        """随机生成某个蓝图类型中的某一个"""
        vehicle_bps = self.bluteprint_library().filter(vehicle_filter)
        spawn_points = self.world.get_map().get_spawn_points()
        spawn_point = spawn_point or random.choice(spawn_points)
        return self.world.spawn_actor(random.choice(vehicle_bps), spawn_point)

    def generate_specific_vehicle(self, vehicle: str, spawn_point: Optional[carla.Transform] = None):
        vehicle_bp = self.bluteprint_library().find(vehicle)
        spawn_points = self.world.get_map().get_spawn_points()
        spawn_point = spawn_point or random.choice(spawn_points)
        return self.world.spawn_actor(vehicle_bp, spawn_point)

    def generate_rgb_camera(self, vehicle):
        camera_bp = self.bluteprint_library().find('sensor.camera.rgb')
        attrs = {
            'image_size_x': '1920',
            'image_size_y': '1080',
            'sensor_tick': '1.0',
        }
        self.set_actor_attribute(camera_bp, attrs)
        return self.world.spawn_actor(camera_bp, carla.Transform(carla.Location(x=0.8, z=1.7)), vehicle)

    def set_actor_attribute(self, actor_bp, attrs: Dict):
        for item in attrs.item():
            actor_bp.set_attribute(*item)


# ====================================================================================================
# -- function ----------------------------------------------------------------------------------------
# ====================================================================================================

def send_control_command(client, throttle, steer, brake, hand_brake=False, reverse=False):
    """Send control command to Carla client

    Args:
        client (_type_): The Carla client object
        throttle (_type_): Throttle command for the sim car [0, 1]
        steer (_type_): Steer command for the sim car [-1, 1]
        brake (_type_): Brake command for the sim car [0, 1]
        hand_brake (bool, optional): Whether the hand brake is engaged. Defaults to False.
        reverse (bool, optional): Whether the sim car is int the reverse gear. Defaults to False.

    Returns:
        _type_: _description_
    """
    control = carla.VehicleControl()
    steer = np.fmax(np.fmin(steer, 1.0), -1.0)
    throttle = np.fmax(np.fmin(throttle, 1.0), 0)
    brake = np.fmax(np.fmin(brake, 1.0), 0)

    control.steer = steer
    control.throttle = throttle
    control.brake = brake
    control.hand_brake = hand_brake
    control.reverse = reverse
    client.set_control(control)


im_width = 640
im_height = 480


def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((im_height, im_width, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("", i3)
    cv2.waitKey(1)
    return i3/255.0


def main():
    actor_list = []
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.get_world()

        blueprint_library = world.get_blueprint_library()
        bp = blueprint_library.filter('bmw')[0]
        print(bp)

        spawn_point = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(bp, spawn_point)
        actor_list.append(vehicle)

        # sleep for 5 seconds, then finish:
        time.sleep(5)

    finally:
        print("Destroying actors!!!")
        for actor in actor_list:
            actor.destroy()
            print(actor.id, "is destroyed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!!!")
