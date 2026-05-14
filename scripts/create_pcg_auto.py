import unreal

def create_pcg_graph():
    # 1. Create PCG Graph Asset
    factory = unreal.PCGGraphFactory()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    graph_path = "/Game/PCG"
    graph_name = "PCG_WildGrassAuto"
    
    # Try creating directory if not exists
    unreal.EditorAssetLibrary.make_directory(graph_path)
    
    pcg_graph = asset_tools.create_asset(graph_name, graph_path, unreal.PCGGraph, factory)
    
    if pcg_graph:
        unreal.log("Autonomously created PCG Graph at: " + pcg_graph.get_path_name())
        # Apply it to the actor we created earlier
        editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actors = editor_subsystem.get_all_level_actors()
        for actor in actors:
            if "PCG_Grass_Generator" in actor.get_actor_label():
                pcg_comp = actor.get_component_by_class(unreal.PCGComponent)
                if pcg_comp:
                    pcg_comp.set_editor_property("graph", pcg_graph)
                    unreal.log("Successfully attached PCG Graph to the generator component in the world.")
                    break
    else:
        unreal.log_error("Failed to create PCG Graph autonomously.")

create_pcg_graph()
