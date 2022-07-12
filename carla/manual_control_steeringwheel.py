# @File    :   
# @Time    :   2022/7/12
# @Author  :   maxiaoming
# @Version :   1.0
# @Contact :   xiaoming.ma@realai.ai
# @Desc    :   None
import sys

sys.path.insert(0, "./PythonAPI/carla/dist/carla-0.9.13-py3.9-win-amd64.egg")
sys.path.append("./PythonAPI")

import carla

import pygame
from pygame.locals import K_a  # 左转 ⬅️
from pygame.locals import K_d  # 右转 ➡️
from pygame.locals import K_r  # 倒车 🚗
from pygame.locals import K_q  # 停车 🅿️
from pygame.locals import K_w  # 前进
from pygame.locals import K_SPACE  # 刹车


from carla import image_converter


WINDOWS_WIDTH = 1920
WINDOWS_HEIGHT = 1080


def make_carla_settings(args):
    settings = CarlaSettings()
    settings.set(
        SyscrhonousMode=False,
        SendNonPlayerAgentsInfo=True,

    )