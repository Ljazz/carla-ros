# sourcery skip: avoid-builtin-shadow
import sys

sys.path.append(
    "/home/realai/zhujianwei/vehicle_automation/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg"
)
import carla


# Read the .osm data
with open("path/to/osm/file", 'r') as f:
    osm_data = f.read()
# Define the desired settings. In this case, default values.
settings = carla.Osm2OdrSettings()
# Set OSM road types to export to OpenDRIVE
settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])

# 启用从 OSM 数据生成红绿灯
settings.generate_traffic_lights = True
# 所有路口以使用交通灯进行控制
settings.all_junctions_with_traffic_lights = True
# 排除某些道路
settings.set_traffic_light_excluded_way_types(["motorway_link"])

# Convert to .xodr
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
with open("path/to/output/file", 'w') as f:
    f.write(xodr_data)


client = carla.Client('localhost', 2000)

vertex_distance = 2.0  # in meters
max_road_length = 500.0 # in meters
wall_height = 0.0      # in meters
extra_width = 0.6      # in meters
world = client.generate_opendrive_world(
    xodr_data, carla.OpendriveGenerationParameters(
        vertex_distance=vertex_distance,
        max_road_length=max_road_length,
        wall_height=wall_height,
        additional_width=extra_width,
        smooth_junctions=True,
        enable_mesh_visibility=True))
