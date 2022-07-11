"""
 Author         : maxiaoming
 Date           : 2022-07-07 10:34:05
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-08 11:46:23
 FilePath       : changeTexturesThroughAPI.py
 Description    : 通过 API 更新纹理
"""

import sys

sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

from PIL import Image

import carla


def main():
    actors = []
    try:
        # 链接模拟器
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)

        world = client.get_world()

        # 加载新的纹理
        image = Image.open("1.jpg")
        height = image.height  # image.size[1]
        width = image.width    # image.size[1]

        # 实例化 carla.TextureColor 对象并填充包含修改后图像数据的像素
        texture = carla.TextureColor(width, height)
        a = 255
        for x in range(width):
            for y in range(height):
                color = image.getpixel((x, y))
                r = int(color[0])
                g = int(color[1])
                b = int(color[2])
                texture.set(x, y, carla.Color(r, g, b, a))

        # 将纹理应用到建筑资产
        world.apply_color_texture_to_object("duikang01_4")
        # 通过API查找世界中的对象名称
        # list(filter(lambda k: 'Apartment' in k, world.get_names_of_all_objects()))
    except Exception:
        for actor in actors:
            actor.destroy()
