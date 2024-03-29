"""
 Author         : maxiaoming
 Date           : 2022-07-07 10:34:05
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-12 17:38:09
 FilePath       : changeTexturesThroughAPI.py
 Description    : 通过 API 更新纹理
"""

import imageio
from PIL import Image
import itertools
import sys

sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

import carla  # noqa


def main():
    actors = []
    try:
        # 链接模拟器
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)

        world = client.get_world()

        # 获取所有可用对象的名称
        object_names = world.get_names_of_all_objects()
        for name in object_names:
            print(name)

        # 加载新的纹理
        # image = Image.open("D:/CARLA/workspace/carla-ros/carla/duikangyangben.png")
        # height = image.height  # image.size[1]
        # width = image.width    # image.size[0]
        # height = image.size[1]
        # width = image.size[0]
        # # 实例化 carla.TextureColor 对象并填充包含修改后图像数据的像素
        # texture = carla.TextureColor(width, height)
        # a = 255
        # for x in range(width):
        #     for y in range(height):
        #         color = image.getpixel((x, y))
        #         r = int(color[0])
        #         g = int(color[1])
        #         b = int(color[2])
        #         texture.set(x, y, carla.Color(r, g, b, a))

        image = imageio.imread(
            "D:/CARLA/workspace/carla-ros/carla/duikangyangben.png")
        height = len(image)
        width = len(image[0])
        texture = carla.TextureColor(width, height)
        a = 1
        for x, y in itertools.product(range(width), range(height)):
            color = image[y][x]
            print(color)
            r = int(color[0])
            g = int(color[1])
            b = int(color[2])
            texture.set(x, height - y - 1, carla.Color(r, g, b, a))

        # 将纹理应用到资产
        world.apply_color_texture_to_object(
            'duikang01_2', carla.MaterialParameter.Diffuse, texture)
        print("地图中的对抗样本对象：", list(
            filter(lambda k: 'duikang01_2' in k, world.get_names_of_all_objects())))
        # 通过API查找世界中的对象名称
        # list(filter(lambda k: 'Apartment' in k, world.get_names_of_all_objects()))
    finally:
        for actor in actors:
            actor.destroy()


if __name__ == '__main__':
    main()
