import unreal
import urllib.request
import os
import random
import zipfile

unreal.log("MARK1: Starting autonomous CC0 asset download and generation...")

# Target paths
temp_dir = "J:\\UnrealProjects\\NewNexus\\TempAssets"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# VUL HIER EEN RAW URL IN VAN EEN CC0 FBX/OBJ/ZIP (bijv. van je eigen Github repo, S3 bucket, of PolyHaven raw link)
# Voor deze proof of concept pakken we de url.
asset_url = "https://raw.githubusercontent.com/m0nklabs/kyberm0nk/main/grass.obj" # PLACEHOLDER
# Voor Fallback schrijven we de OBJ gewoon naar schijf als we hem niet kunnen downloaden (zodat de render niet crasht in demo)

download_path = os.path.join(temp_dir, "grass_asset.obj")

# 1. Download The External Asset headlessly
try:
    unreal.log(f"MARK1: Downloading asset from {asset_url}...")
    # Add a mock User-Agent to avoid simple blocks
    req = urllib.request.Request(asset_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(download_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    unreal.log(f"MARK1: Successfully downloaded to {download_path}")
except Exception as e:
    unreal.log_error(f"MARK1: Download failed: {e}. Falling back to generating the file on disk...")
    # Fallback to procedural grass if URL is a placeholder (so it doesn't break the build test)
    obj_content = "o GrassBlade\nv -1 0 0\nv 1 0 0\nv -0.8 1 5\nv 0.8 1 5\nv -0.5 2.5 10\nv 0.5 2.5 10\nv 0 4 15\nvt 0 0\nvt 1 0\nvt 0.1 0.33\nvt 0.9 0.33\nvt 0.25 0.66\nvt 0.75 0.66\nvt 0.5 1\nf 1/1 2/2 4/4 3/3\nf 3/3 4/4 6/6 5/5\nf 5/5 6/6 7/7\n"
    with open(download_path, 'w') as f:
        f.write(obj_content)

# 2. Import the OBJ/FBX via AssetImportTask
import_task = unreal.AssetImportTask()
import_task.filename = download_path
import_task.destination_path = '/Game/TopDown/Meshes'
import_task.destination_name = 'SM_FreeGrass'
import_task.replace_existing = True
import_task.automated = True
import_task.save = True

# Options
options = unreal.FbxImportUI()
options.import_mesh = True
options.import_materials = True # Enable materials in case the FBX/OBJ has them
options.import_textures = True
import_task.options = options

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])
unreal.log("MARK1: External asset imported into Unreal Engine.")

# Load original template map
original_path = '/Game/TopDown/Lvl_TopDown'
new_path = '/Game/TopDown/Lvl_Grasslands'
unreal.EditorLoadingAndSavingUtils.load_map(original_path)

mesh_asset = unreal.EditorAssetLibrary.load_asset('/Game/TopDown/Meshes/SM_FreeGrass')

if mesh_asset:
    # 3. Create HISM
    location = unreal.Vector(0, 0, 0)
    hism_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, unreal.Rotator())
    hism_actor.set_actor_label("MARK1_GrassField")
    
    hism_comp = unreal.HierarchicalInstancedStaticMeshComponent(hism_actor, "HISM_Grass")
    hism_comp.set_static_mesh(mesh_asset)
    
    # 4. Add instances scattered
    num_items = 100000
    spread = 10000.0
    transforms = []
    
    unreal.log(f"MARK1: Generating {num_items} instance transforms...")
    for i in range(num_items):
        x = random.uniform(-spread, spread)
        y = random.uniform(-spread, spread)
        z = 0.0
        loc = unreal.Vector(x,y,z)
        rot = unreal.Rotator(random.uniform(-5, 5), random.uniform(0, 360), 0)
        s_val = random.uniform(1.0, 3.0)
        scale = unreal.Vector(s_val, s_val, s_val * random.uniform(0.8, 1.5))
        transforms.append(unreal.Transform(location=loc, rotation=rot, scale=scale))
        
    hism_comp.add_instances(transforms, False)
    unreal.log("MARK1: HISM populated.")

# Safe duplication
if unreal.EditorAssetLibrary.does_asset_exist(new_path):
    unreal.EditorAssetLibrary.delete_asset(new_path)
    
success = unreal.EditorAssetLibrary.duplicate_asset(original_path, new_path)
if success:
    unreal.log(f"MARK1: Succesfully generated {new_path}")
    world_copy = unreal.EditorAssetLibrary.load_asset(new_path)
    unreal.EditorAssetLibrary.save_loaded_asset(world_copy)

    ini_file = "J:\\UnrealProjects\\NewNexus\\Config\\DefaultEngine.ini"
    try:
        with open(ini_file, 'r') as f:
            lines = f.readlines()
        with open(ini_file, 'w') as f:
            for line in lines:
                if line.startswith("GameDefaultMap="):
                    f.write("GameDefaultMap=/Game/TopDown/Lvl_Grasslands.Lvl_Grasslands\n")
                elif line.startswith("EditorStartupMap="):
                    f.write("EditorStartupMap=/Game/TopDown/Lvl_Grasslands.Lvl_Grasslands\n")
                else:
                    f.write(line)
    except Exception as e:
        unreal.log_error(f"MARK1: Could not update ini file. {e}")
