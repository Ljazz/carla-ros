"""
 Author         : maxiaoming
 Date           : 2022-07-19 10:08:07
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-19 10:09:17
 FilePath       : automatic_control_revised.py
 Description    : 
"""
import os
import random
import sys


sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

import carla

from agents.navigation.behavior_agent import BehaviorAgent


def main():
    try:
        client = carla.Client("localhost", 2000)
        client.set_time(10.0)

        world = client.get_world()

        origin_settings = world.get_settings()

        # 设置同步模式
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)

        blueprint_library = world.get_blueprint_library()

        # 获取有效的出生点
        all_default_spawn = world.get_map().get_spawn_points()
        spawn_point = random.choice(all_default_spawn) if all_default_spawn else carla.Transform()

        # 创建车辆
        ego_vehicle_bp = blueprint_library.find('vehicle.lincoln.mkz2017')
        ego_vehicle_bp.set_attribute('color', '0,0,0')
        vehicle = world.spawn_actor(ego_vehicle_bp, spawn_point)

        world.trick()

        # 创建行为代理
        agent = BehaviorAgent(vehicle, behavior='normal')

        # 设置目的地
        spawn_points = world.get_map().get_spawn_points()
        random.shuffle(spawn_points)

        # 避免目的地和起始位置相同
        if spawn_points[0].location != agent.vehicle.get_location():
            destination = spawn_points[0]
        else:
            destination = spawn_points[1]

        # 生成路
        agent.set_destination(agent.vehicle.get_location(), destination.location, clean=True)

        while True:
            agent.update_information(vehicle)
            world.trick()

            if len(agent._local_planner.waypoints_queue) < 1:
                print("=============Success, Arrivied at Target Point!")
                break

            # 上层
            spectator = world.get_spectator()
            transform = vehicle.get_transform()
            spectator.set_transform(
                carla.Transform(transform.location + carla.Location(z=40), carla.Rotation(pitch=-90))
            )
            speed_limit = vehicle.get_speed_limit()
            agent.get_location_planner().set_speed(speed_limit)

            control = agent.run_step(debug=True)
            vehicle.apply_control(control)
    finally:
        world.apply_settings(origin_settings)
        vehicle.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(" - exited by user.")
