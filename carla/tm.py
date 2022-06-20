from pyexpat import model
import carla
import random


# 链接carla并且初始化world对象
client = carla.Client('localhost', 2000)
world = client.get_world()
# world = client.reload_world('Town04')
blueprint_library = world.get_blueprint_library()

# ------------------------------------------------------------
# 设置模拟器并初始化流量管理器
# ------------------------------------------------------------
# 在同步模式下设置模拟器
settings = world.get_settings()
settings.synchronous_mode = True  # 开启同步模式
settings.fixed_delta_seconds = 0.05
world.apply_settings(settings)

# 在同步模式下设置 TM
traffic_manager = client.get_trafficmanager()
traffic_manager.set_synchronous_mode(True)
# 设置种子，以便在必要时可以重复行为
traffic_manager.set_random_device_seed(0)
random.seed(0)

# 观察者
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
for i, spawn_point in enumerate(random.sample(spawn_points, max_vehicles)):
    temp = world.try_spawn_actor(random.choice(blueprints), spawn_point)
    if temp is not None:
        vehicles.append(temp)

# ------------------------------------------------------------
# 使用 Traffic Manager 控制车辆
# ------------------------------------------------------------
# 解析生成的车辆列表并通过 set_autopilot() 将控制权交给 TM
for vehicle in vehicles:
    vehicle.set_autopilot(True)
    # 随机设置车辆忽略红绿灯的概率
    traffic_manager.ignore_lights_percentage(vehicle, random.randint(0, 50))

# ------------------------------------------------------------
# 指定位置生成model3，并设置为自动驾驶
# ------------------------------------------------------------
# model3出生点
# model3_spawn_points_159 = carla.Transform(carla.Location(
#     x=37.249432, y=-170.444504, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.326125, roll=0.000000))
# model3_bp = blueprint_library.find('vehicle.tesla.model3')
# model3_bp.set_attribute('color', '255,0,0')
# model3 = world.spawn_actor(model3_bp, model3_spawn_points_159)
# model3.set_autopilot(True)

# ------------------------------------------------------------
# 指定车辆路线
# ------------------------------------------------------------
# Route 1
spawn_point_1 = spawn_points[32]
# 从选定的生成点创建路线 1
route_1_indices = [129, 28, 124, 33, 97, 119, 58, 154, 147]
route_1 = []
for ind in route_1_indices:
    route_1.append(spawn_points[ind].location)

# Route 2
spawn_point_2 = spawn_points[149]
# 从选定的生成点创建路线 2
route_2_indices = [21, 76, 38, 34, 90, 3]
route_2 = []
for ind in route_2_indices:
    route_2.append(spawn_points[ind].location)

# 在地图上打印路线
world.debug.draw_string(spawn_point_1.location, 'Spawn point 1', life_time=30, color=carla.Color(255, 0, 0))
world.debug.draw_string(spawn_point_2.location, 'Spawn point 2', life_time=30, color=carla.Color(0, 0, 255))

for ind in route_1_indices:
    spawn_points[ind].location
    world.debug.draw_string(spawn_points[ind].location, str(ind), life_time=60, color=carla.Color(255, 0, 0))

for ind in route_2_indices:
    spawn_points[ind].location
    world.debug.draw_string(spawn_points[ind].location, str(ind), life_time=60, color=carla.Color(0, 0, 255))

# 设置延迟以在生成时间之间创建间隙
spawn_delay = 20
counter = spawn_delay

# 设置最大车辆（为低硬件规格设置较小）
max_vehicles = 200
# 在生成点之间交替
alt = False

# spawn_points = world.get_map().get_spawn_points()
# while True:
#     world.tick()

#     n_vehicles = len(world.get_actors().filter('*vehicle*'))
#     vehicle_bp = random.choice(blueprints)

#     # 仅在延迟后生成车辆
#     if counter == spawn_delay and n_vehicles < max_vehicles:
#         # 备用重生点
#         if alt:
#             vehicle = world.try_spawn_actor(vehicle_bp, spawn_point_1)
#         else:
#             vehicle = world.try_spawn_actor(vehicle_bp, spawn_point_2)

#         if vehicle: # 如果车辆成功生成
#             vehicle.set_autopilot(True) # 让 TM 控制车辆

#             # 设置TM车辆控制的参数，我们不要变道
#             traffic_manager.update_vehicle_lights(vehicle, True)
#             traffic_manager.random_left_lanechange_percentage(vehicle, 0)
#             traffic_manager.random_right_lanechange_percentage(vehicle, 0)
#             traffic_manager.auto_lane_change(vehicle, False)

#             # 在路线之间交替
#             if alt:
#                 traffic_manager.set_path(vehicle, route_1)
#                 alt = False
#             else:
#                 traffic_manager.set_path(vehicle, route_2)
#                 alt = True

#             vehicle = None

#         counter -= 1
#     elif counter > 0:
#         counter -= 1
#     elif counter == 0:
#         counter = spawn_delay

while True:
    world.tick()
