'''
Author         : maxiaoming
Date           : 2022-06-14 12:16:23
LastEditors    : xiaoming.ma
LastEditTime   : 2022-06-14 15:06:56
Description    : 导入贴图和音频🧃
'''
import os

import unreal


def importMyAssets():
    texture_task = buildImportTask(texture_jpg, "/Game/duikang01/Texture")
    executeImportTasks([texture_task])


def buildImportTask(filename, destination_path):
    task = unreal.AssetImportTask()  # AssetImportTask: 包含要导入的一组资产的数据
    """
    automated (bool): 避免对话
    destination_name (str): 可选的自定义名称导入为
    destination_path (str): 资产将被导入到的路径
    factory (Factory): 可选工厂使用
    filename (str): 要导入的文件名
    imported_object_paths (Array(str)): 导入后创建或更新的对象的路径
    options (Object): 特定于资产类型的导入选项
    replace_existing (bool): 覆盖现有资产
    replace_existing_settings (bool): 覆盖现有资产时替换现有设置
    result (Array(Object)): 导入的对象
    save (bool): 导入后保存
    """
    task.set_editor_property('automated', True)
    task.set_editor_property('destination_name', '')
    task.set_editor_property('destination_path', destination_path)
    task.set_editor_property('filename', filename)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    return task


def executeImportTasks(tasks):
    """
    - AssetTools: 资产工具
        - import_asset_tasks(): 使用指定的任务导入资产
            - 参数
                - import_tasks: 指定如何导入每个文件的任务
            - 返回值
                - None

    AssetToolsHelpers: 资产工具助手
        - get_asset_tools(): 获取资产工具
            - 参数
            - 返回值
                - 资产工具

    """
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for task in tasks:
        # print(len(task.get_editor_property('imported_object_paths')))
        for path in task.get_editor_property('imported_object_paths'):
            print(f"imported {path}")


if __name__ == '__main__':
    asset_folder = "D:/CARLA/workspace/carla-ros/carla"
    texture_jpg = os.path.join(asset_folder, "duikangyangben.png").replace("\\", "/")
    importMyAssets()
