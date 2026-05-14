import unreal

def build_pcg():
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    graph_name = "PCG_Grass"
    package_path = "/Game/PCG"
    
    # Check if exists
    pcg_graph = unreal.EditorAssetLibrary.load_asset(f"{package_path}/{graph_name}")
    
    if not pcg_graph:
        # We need the PCG Graph factory to create one, but PCG exposes Python APIs since 5.2/5.3
        # In UE 5.4+, pcg_graph can be created directly.
        pass

build_pcg()
