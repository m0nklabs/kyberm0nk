import unreal

def create_pcg_setup():
    # Load level elements to place the PCG Volume
    editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    
    # Check if a volume already exists, clear old ones if any
    actors = editor_subsystem.get_all_level_actors()
    for actor in actors:
        if "PCGVolume" in actor.get_name():
            editor_subsystem.destroy_actor(actor)
            
    # Assuming PCG plugin is enabled...
    try:
        # Spawn a PCG Volume in the center of the level
        pcg_volume_class = unreal.EditorAssetLibrary.load_blueprint_class('/Script/PCG.PCGVolume')
        if not pcg_volume_class:
            unreal.log_error("Could not load PCGVolume class")
            return
            
        spawn_location = unreal.Vector(0.0, 0.0, 0.0)
        pcg_volume = editor_subsystem.spawn_actor_from_class(pcg_volume_class, spawn_location)
        if pcg_volume:
            pcg_volume.set_actor_scale3d(unreal.Vector(50.0, 50.0, 10.0))
            unreal.log("Spawned PCG Volume successfully.")
    except Exception as e:
        unreal.log_error(f"Error setting up PCG volume: {e}")

create_pcg_setup()
