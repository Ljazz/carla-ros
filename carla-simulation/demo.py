"""
 Author         : maxiaoming
 Date           : 2022-07-13 10:25:34
 LastEditors    : xiaoming.ma
 LastEditTime   : 2022-07-13 10:25:39
 FilePath       : demo.py
 Description    : CARLA manual control
        W            : throttle
        S            : brake
        AD           : steer
        Q            : toggle reverse
        Space        : hand-brake
        P            : toggle autopilot
        R            : restart level
"""

import argparse
import logging
import random
import time
import sys

sys.path.insert(0,
                "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg")
sys.path.append("/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI")

try:
    import pygame
    from pygame.locals import (K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP, K_a,
                               K_d, K_p, K_q, K_r, K_s, K_w)
except ImportError as e:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed') from e

try:
    import numpy as np
except ImportError as e:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed') from e


WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

import carla


def make_carla_settings(client, args):
    settings = client.get_
