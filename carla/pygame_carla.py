import random

import numpy as np
import pygame
import carla


# ------------------------------------------------------------
# 设置模拟器并初始化流量管理器
# ------------------------------------------------------------
# 连接到客户端并检索世界对象
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

# 在同步模式下设置模拟器
settings = world.get_settings()
settings.synchronous_mode = True  # 开启同步模式
settings.fixed_delta_seconds = 0.05
world.apply_settings(settings)

# 同步模式下设置 TM
traffic_manager = client.get_trafficemanager()
traffic_manager.set_synchronous_mode(True)

# 设置种子，以便在必要时可以重复行为
traffic_manager.set_random_device_seed(0)
random.seed(0)

spectator = world.get_spectator()

# ------------------------------------------------------------
# 生成车辆
# ------------------------------------------------------------
# 所有有效的出生点
spawn_points = world.get_map().get_spawn_points()
# 将生成点位置绘制为地图中的数字
for i, spawn_point in enumerate(spawn_points):
    world.debug.draw_string(spawn_point.location, str(i), life_time=10)
#     if i in [361, 159]:
#         print(spawn_point)
#         print(spawn_point.location)

# 各种车辆模型
models = ['dodge', 'audi', 'model3', 'mini', 'mustang', 'lincoln', 'prius', 'nissan', 'crown', 'impala']
blueprints = []
for vehicle in world.get_blueprint_library().filter('*vehicle*'):
    if any(model in vehicle.id for model in models):
        blueprints.append(vehicle)
# 设置最大车辆数量并为我们生成的车辆准备一份清单
max_vehicles = 50
max_vehicles = min(max_vehicles, len(spawn_points))
vehicles = []
# 随机抽取生成点样本并生成一些车辆
for spawn_point in random.sample(spawn_points, max_vehicles):
    temp = world.try_spawn_actor(random.choice(blueprints), spawn_point)
    if temp is not None:
        vehicle.append(temp)
# 解析生成的车辆列表并通过 set_autopilot() 将控制权交给 TM
for vehicle in vehicles:
    vehicle.set_autopilot(True)
    # 随机设置车辆忽略红绿灯的概率
    traffic_manager.ignore_lights_percentage(vehicle, random.randint(0, 50))

# ------------------------------------------------------------
# 使用 PyGame 渲染相机输出和控制车辆
# ------------------------------------------------------------
class RenderObject(object):
    def __init__(self, height, width):
        init_image = np.random.randint(0, 255, (height, width, 3), dtype="uint8")
        self.surface = pygame.surfarray.make_surface(init_image.swapaxes(0, 1))


def pygame_callback(data, obj):
    img = np.reshape(np.copy(data.raw_data), (data.height, data.width, 4))
    img = img[:, :, :3]
    img = img[:, :, ::-1]
    obj.surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))


class ControlObject(object):
    def __init__(self, veh):

        # Conrol parameters to store the control state
        self._vehicle = veh
        self._steer = 0
        self._throttle = False
        self._brake = False
        self._steer = None
        self._steer_cache = 0
        # A carla.VehicleControl object is needed to alter the 
        # vehicle's control state
        self._control = carla.VehicleControl()

    # Check for key press events in the PyGame window
    # and define the control state
    def parse_control(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._vehicle.set_autopilot(False)
            if event.key == pygame.K_UP:
                self._throttle = True
            if event.key == pygame.K_DOWN:
                self._brake = True
            if event.key == pygame.K_RIGHT:
                self._steer = 1
            if event.key == pygame.K_LEFT:
                self._steer = -1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self._throttle = False
            if event.key == pygame.K_DOWN:
                self._brake = False
                self._control.reverse = False
            if event.key == pygame.K_RIGHT:
                self._steer = None
            if event.key == pygame.K_LEFT:
                self._steer = None

    # Process the current control state, change the control parameter
    # if the key remains pressed
    def process_control(self):

        if self._throttle: 
            self._control.throttle = min(self._control.throttle + 0.01, 1)
            self._control.gear = 1
            self._control.brake = False
        elif not self._brake:
            self._control.throttle = 0.0

        if self._brake:
            # If the down arrow is held down when the car is stationary, switch to reverse
            if self._vehicle.get_velocity().length() < 0.01 and not self._control.reverse:
                self._control.brake = 0.0
                self._control.gear = 1
                self._control.reverse = True
                self._control.throttle = min(self._control.throttle + 0.1, 1)
            elif self._control.reverse:
                self._control.throttle = min(self._control.throttle + 0.1, 1)
            else:
                self._control.throttle = 0.0
                self._control.brake = min(self._control.brake + 0.3, 1)
        else:
            self._control.brake = 0.0

        if self._steer is not None:
            if self._steer == -1:
                self._steer_cache -= 0.03
            elif self._steer == 1:
                self._steer_cache += 0.03
            min(0.7, max(-0.7, self._steer_cache))
        else:
            if self._steer_cache > 0.0:
                self._steer_cache *= 0.2
            if self._steer_cache < 0.0:
                self._steer_cache *= 0.2
            if 0.01 > self._steer_cache > -0.01:
                self._steer_cache = 0.0
        self._control.steer = round(self._steer_cache,1)
        # Ápply the control parameters to the ego vehicle
        self._vehicle.apply_control(self._control)


# Randomly select a vehicle to follow with the camera
ego_vehicle = random.choice(vehicles)

# Initialise the camera floating behind the vehicle
camera_init_trans = carla.Transform(carla.Location(x=-5, z=3), carla.Rotation(pitch=-20))
camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=ego_vehicle)

# Start camera with PyGame callback
camera.listen(lambda image: pygame_callback(image, renderObject))

# Get camera dimensions
image_w = camera_bp.get_attribute("image_size_x").as_int()
image_h = camera_bp.get_attribute("image_size_y").as_int()

# Instantiate objects for rendering and vehicle control
renderObject = RenderObject(image_w, image_h)
controlObject = ControlObject(ego_vehicle)


# Initialise the display
pygame.init()
gameDisplay = pygame.display.set_mode((image_w,image_h), pygame.HWSURFACE | pygame.DOUBLEBUF)
# Draw black to the display
gameDisplay.fill((0,0,0))
gameDisplay.blit(renderObject.surface, (0,0))
pygame.display.flip()

# Game loop
crashed = False

while not crashed:
    # Advance the simulation time
    world.tick()
    # Update the display
    gameDisplay.blit(renderObject.surface, (0,0))
    pygame.display.flip()
    # Process the current control state
    controlObject.process_control()
    # Collect key press events
    for event in pygame.event.get():
        # If the window is closed, break the while loop
        if event.type == pygame.QUIT:
            crashed = True

        # Parse effect of key press event on control state
        controlObject.parse_control(event)
        if event.type == pygame.KEYUP and event.key == pygame.K_TAB:
            ego_vehicle.set_autopilot(True)
            ego_vehicle = random.choice(vehicles)
            # Ensure vehicle is still alive (might have been destroyed)
            if ego_vehicle.is_alive:
                # Stop and remove the camera
                camera.stop()
                camera.destroy()

                # Spawn new camera and attach to new vehicle
                controlObject = ControlObject(ego_vehicle)
                camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=ego_vehicle)
                camera.listen(lambda image: pygame_callback(image, renderObject))

                # Update PyGame window
                gameDisplay.fill((0,0,0))               
                gameDisplay.blit(renderObject.surface, (0,0))
                pygame.display.flip()

# Stop camera and quit PyGame after exiting game loop
camera.stop()
pygame.quit()