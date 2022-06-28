import argparse
import datetime
import subprocess


def main(vehicle):
    map_names = ['Town01', 'Town02', 'Town03', 'Town04', 'Town05']

    for map_name in map_names:
        filename = f'./video/{datetime.datetime.now().strftime("%Y%m%d")}/{map_name.lower()}_{vehicle}.mp4'
        print(filename)
        command = f"python car_run_line.py --map {map_name} --vehicle {vehicle} --filename {filename}"
        print(command)
        ex = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        out, err = ex.communicate()
        print("*" * 40)
        print("out ==> ", out)
        print("err ==> ", err)
        print(f"地图:{map_name}，车:{vehicle},视频生成{['失败','成功'][err is not None]}！")


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--vehicles",
        help="车辆",
    )
    args = argparser.parse_args()
    vehicles = args.vehicles.split(',')  # ['none01', 'test01']
    print(vehicles, type(vehicles))
    for vehicle in vehicles:
        main(vehicle)
