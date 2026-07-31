import os
import subprocess

def create_link_or_junction(target, link_path):
    if os.path.exists(link_path) or os.path.islink(link_path):
        return
    try:
        os.symlink(target, link_path, target_is_directory=os.path.isdir(target))
    except Exception:
        if os.name == "nt" and os.path.isdir(target):
            try:
                subprocess.run(f'cmd /c mklink /J "{link_path}" "{target}"', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            except Exception:
                pass

def prepare_instance(version_name, settings, minecraft_dir=None):
    if minecraft_dir is None:
        if os.name == "nt":
            minecraft_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".minecraft")
        else:
            minecraft_dir = os.path.expanduser("~/.minecraft")
        
    safe_folder_name = version_name.replace(":", "_")
    instance_dir = os.path.join(minecraft_dir, "instances", safe_folder_name)
    os.makedirs(instance_dir, exist_ok=True)
    
    os.makedirs(os.path.join(instance_dir, "mods"), exist_ok=True)
    os.makedirs(os.path.join(instance_dir, "config"), exist_ok=True)
    
    to_link = []
    if not settings.get("isolate_saves", False):
        to_link.append("saves")
    if not settings.get("isolate_resourcepacks", False):
        to_link.append("resourcepacks")
        
    for item in to_link:
        global_path = os.path.join(minecraft_dir, item)
        instance_path = os.path.join(instance_dir, item)
        os.makedirs(global_path, exist_ok=True)
        create_link_or_junction(global_path, instance_path)
            
    global_servers = os.path.join(minecraft_dir, "servers.dat")
    instance_servers = os.path.join(instance_dir, "servers.dat")
    if os.path.exists(global_servers) and not os.path.exists(instance_servers) and not os.path.islink(instance_servers):
        try:
            os.symlink(global_servers, instance_servers)
        except Exception:
            pass
            
    return instance_dir