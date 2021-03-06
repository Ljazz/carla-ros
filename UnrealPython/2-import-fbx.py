'''
Author         : maxiaoming
Date           : 2022-06-14 12:21:28
LastEditors    : xiaoming.ma
LastEditTime   : 2022-06-14 15:06:43
Description    : 导入fbx
'''
import os

import unreal


def import_myassets():
    # ! 静态网格
    static_mesh_task = build_import_task(static_mesh_fbx, "/Game/MyAsset/StaticMeshes", build_static_mesh_import_options())
    # ! 带骨骼的网格
    skeletal_mesh_task = build_import_task(skeletal_mesh_fbx, "/Game/MyAsset/SkeletalMeshes", build_skeletal_mesh_import_options())
    execute_import_tasks([static_mesh_task, skeletal_mesh_task])
    

def build_import_task(filename, destination_path, options=None):
    task = unreal.AssetImportTask()
    task.set_editor_property("automated", True)
    task.set_editor_property("destination_name", "")
    task.set_editor_property("destination_path", destination_path)
    task.set_editor_property("filename", filename)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    task.set_editor_property("options", options)
    return task


def execute_import_tasks(tasks):
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for task in tasks:
        for path in tasks:
            for path in task.get_editor_property("imported_object_paths"):
                print(f"Imported {path}.")


def build_static_mesh_import_options():
    options = unreal.FbxImportUI()
    
    # ! unreal.FbxImportUI
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("import_materials", True)
    options.set_editor_property("import_as_skeletal", False)  # Static Mesh
    
    # ! unreal.FbxMeshImportData
    options.static_mesh_import_data.set_editor_property("import_translation", unreal.Vector(50.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property("import_rotation", unreal.Rotator(0.0, 110.0, 0.0))
    options.static_mesh_import_data.set_editor_property("import_uniform_scale", 1.0)
    
    # ! unreal.FbxStaticMeshImportData
    options.static_mesh_import_data.set_editor_property("combine_meshes", True)
    options.static_mesh_import_data.set_editor_property("generate_lightmap_u_vs", True)
    options.static_mesh_import_data.set_editor_property("auto_generate_collision", True)
    return options


def build_skeletal_mesh_import_options():
    options = unreal.FbxImportUI()
    
    # ! unreal.FbxImportUI
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_textures", True)
    options.set_editor_property("import_materials", True)
    options.set_editor_property("import_as_skeletal", True)  # Skeletal Mesh
    
    # ! unreal.FbxMeshImportData
    options.static_mesh_import_data.set_editor_property("import_translation", unreal.Vector(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property("import_rotation", unreal.Rotator(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property("import_uniform_scale", 1.0)
    
    # ! unreal.FbxStaticMeshImportData
    options.static_mesh_import_data.set_editor_property("import_morph_targets", True)
    options.static_mesh_import_data.set_editor_property("update_skeleton_reference_pose", False)
    return options


if __name__ =="__main__":
    asset_folder = "D:/CARLA/workspace/images"  # 资源路径
    static_mesh_fbx = os.path.join(asset_folder, 'static_fbx.fbx').replace("\\", "/")
    skeletal_mesh_fbx = os.path.join(asset_folder, "skeletal_fbx.fbx").replace("\\", "/")
    import_myassets()
