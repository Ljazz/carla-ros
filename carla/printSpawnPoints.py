import sys

sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

import carla


def main():
    actor_list = []
    try:
        # 创建client链接到Carla当中
        client = carla.Client('localhost', 2000)
        # 设置超时时间
        client.set_timeout(10.0)
        # 获取世界
        world = client.get_world()

        spawn_points = world.get_map().get_spawn_points()
        for i, spawn_point in enumerate(spawn_points):
            if i in [143]:
                print(spawn_points[i])
            world.debug.draw_string(spawn_point.location, str(i), life_time=100)

    finally:
        for actor in actor_list:
            actor.destroy()
            print(actor.id, ' is destroyed')


if __name__ == '__main__':
    main()
