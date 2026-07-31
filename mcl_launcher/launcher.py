import os
import sys
import subprocess
from mcl_launcher.instance_manager import prepare_instance
from mcl_launcher.metadata_repair import repair_version_metadata

def get_default_minecraft_dir():
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".minecraft")
    return os.path.expanduser("~/.minecraft")

def install_game_version(version_name, settings, minecraft_dir=None):
    if minecraft_dir is None:
        minecraft_dir = get_default_minecraft_dir()
        
    cmd = [sys.executable, "-m", "portablemc"]
    
    if settings.get("isolate_instances", True):
        instance_dir = prepare_instance(version_name, settings, minecraft_dir)
        cmd += ["--work-dir", instance_dir]
    else:
        cmd += ["--work-dir", minecraft_dir]
        
    cmd += ["start", version_name, "--dry"]
    
    launch_env = os.environ.copy()
    if os.name != "nt":
        launch_env.pop("XMODIFIERS", None)
        launch_env.pop("GTK_IM_MODULE", None)
        launch_env.pop("QT_IM_MODULE", None)
    
    print(f"\n==================================================")
    print(f"        DOWNLOADING & INSTALLING: {version_name}")
    print("==================================================\n")
    print("Downloading all required assets, libraries, and loaders...")
    
    try:
        subprocess.run(cmd, env=launch_env)
        if "explicitly_installed" not in settings:
            settings["explicitly_installed"] = []
        if version_name not in settings["explicitly_installed"]:
            settings["explicitly_installed"].append(version_name)
    except Exception as e:
        print(f"\nError during installation: {e}")
        input("Press Enter to return...")

def launch_game(version_name, settings, minecraft_dir=None, mode="background"):
    if minecraft_dir is None:
        minecraft_dir = get_default_minecraft_dir()
        
    repaired = repair_version_metadata(version_name, minecraft_dir)
    if repaired:
        print(f"[REPAIR] Fixed corrupted majorVersion metadata for {version_name} in-place.")
        
    cmd = [sys.executable, "-m", "portablemc"]
    
    if settings.get("isolate_instances", True):
        instance_dir = prepare_instance(version_name, settings, minecraft_dir)
        cmd += ["--work-dir", instance_dir]
        print(f"[SANDBOX] Game workspace isolated to: {instance_dir}")
    else:
        cmd += ["--work-dir", minecraft_dir]
        print(f"[GLOBAL] Game workspace running globally at: {minecraft_dir}")
        
    cmd += ["start", version_name]
    cmd += ["-u", settings.get("username", "Player")]
    
    if settings.get("jvm_args"):
        cmd += ["--jvm-args", settings["jvm_args"]]
        
    launch_env = os.environ.copy()
    if os.name != "nt":
        launch_env.pop("XMODIFIERS", None)
        launch_env.pop("GTK_IM_MODULE", None)
        launch_env.pop("QT_IM_MODULE", None)
    
    if mode == "background":
        print(f"Launching {version_name} in background...")
        if os.name == "nt":
            # Windows detached process creation flags
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            subprocess.Popen(
                cmd,
                env=launch_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            )
        else:
            subprocess.Popen(
                cmd,
                env=launch_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        sys.exit(0)
    else:
        print(f"Launching {version_name} in foreground with real-time logs...\n")
        try:
            subprocess.run(cmd, env=launch_env)
        except KeyboardInterrupt:
            print("\nGame launch interrupted by user.")
        except Exception as e:
            print(f"\nError running PortableMC process: {e}")