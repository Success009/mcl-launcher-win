import os
import sys
import re
from mcl_launcher import config
from mcl_launcher.tui import run_tui
from mcl_launcher.launcher import launch_game

def get_default_minecraft_dir():
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".minecraft")
    return os.path.expanduser("~/.minecraft")

def get_version_tuple(version_str):
    if isinstance(version_str, tuple):
        version_str = version_str[1]
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?(?:\.(\d+))?", version_str)
    if match:
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3)) if match.group(3) else 0
        build = int(match.group(4)) if match.group(4) else 0
        return (major, minor, patch, build)
    return (0, 0, 0, 0)

def map_folder_to_version_id(folder_name):
    folder_lower = folder_name.lower()
    if "fabric" in folder_lower:
        match = re.search(r"(\d+\.\d+(?:\.\d+)?)", folder_name)
        if match:
            return f"fabric:{match.group(1)}"
    elif "forge" in folder_lower:
        match = re.search(r"(\d+\.\d+(?:\.\d+)?)", folder_name)
        if match:
            return f"forge:{match.group(1)}"
    elif "neoforge" in folder_lower:
        match = re.search(r"(\d+\.\d+(?:\.\d+)?)", folder_name)
        if match:
            return f"neoforge:{match.group(1)}"
    elif "quilt" in folder_lower:
        match = re.search(r"(\d+\.\d+(?:\.\d+)?)", folder_name)
        if match:
            return f"quilt:{match.group(1)}"
            
    match = re.search(r"^(\d+\.\d+(?:\.\d+)?)$", folder_name)
    if match:
        return match.group(1)
        
    return folder_name

def exists_on_disk(ver_id, installed_folders):
    ver_id_lower = ver_id.lower()
    if ":" in ver_id_lower:
        loader, mc_ver = ver_id_lower.split(":", 1)
        for f in installed_folders:
            f_lower = f.lower()
            if loader in f_lower and mc_ver in f_lower:
                return True
        return False
    else:
        for f in installed_folders:
            if f.lower() == ver_id_lower:
                return True
        return False

def get_local_versions(minecraft_dir, settings):
    if "explicitly_installed" in settings:
        cleaned_list = []
        for item in settings["explicitly_installed"]:
            if isinstance(item, (list, tuple)):
                for subitem in item:
                    if isinstance(subitem, str) and subitem not in cleaned_list and subitem not in ("background", "foreground"):
                        cleaned_list.append(subitem)
            elif isinstance(item, str):
                if item not in cleaned_list:
                    cleaned_list.append(item)
        settings["explicitly_installed"] = cleaned_list
        
    if "last_played_version" in settings:
        lp = settings["last_played_version"]
        if isinstance(lp, (list, tuple)):
            for subitem in lp:
                if isinstance(subitem, str) and subitem not in ("background", "foreground"):
                    settings["last_played_version"] = subitem
                    break

    if "explicitly_installed" not in settings or not settings["explicitly_installed"]:
        settings["explicitly_installed"] = []
        versions_dir = os.path.join(minecraft_dir, "versions")
        if os.path.isdir(versions_dir):
            try:
                folders = os.listdir(versions_dir)
                modloader_dependencies = set()
                for item in folders:
                    full_path = os.path.join(versions_dir, item)
                    if os.path.isdir(full_path):
                        folder_lower = item.lower()
                        if any(x in folder_lower for x in ["fabric", "forge", "neoforge", "quilt"]):
                            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", item)
                            if match:
                                modloader_dependencies.add(match.group(1))
                                
                for item in folders:
                    full_path = os.path.join(versions_dir, item)
                    if os.path.isdir(full_path) and "error" not in item.lower():
                        ver_id = map_folder_to_version_id(item)
                        if ver_id in modloader_dependencies:
                            continue
                        if ver_id not in settings["explicitly_installed"]:
                            settings["explicitly_installed"].append(ver_id)
            except Exception:
                pass
        config.save_settings(settings)
        
    versions_dir = os.path.join(minecraft_dir, "versions")
    installed_folders = []
    if os.path.isdir(versions_dir):
        try:
            installed_folders = os.listdir(versions_dir)
        except Exception:
            pass
            
    valid_versions = []
    for ver_id in settings["explicitly_installed"]:
        if exists_on_disk(ver_id, installed_folders):
            if ver_id not in valid_versions:
                valid_versions.append(ver_id)
                
    valid_versions.sort(key=get_version_tuple, reverse=True)
    return valid_versions

def fuzzy_find_version(query, local_versions):
    query_lower = query.lower()
    matches = []
    for ver in local_versions:
        if query_lower in ver.lower():
            matches.append(ver)
            
    if not matches:
        return None
        
    for match in matches:
        if match.lower() == query_lower:
            return match
            
    return matches[0]

def main():
    minecraft_dir = get_default_minecraft_dir()
    settings = config.load_settings()
    
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        local_versions = get_local_versions(minecraft_dir, settings)
        
        if args[0] in ("-h", "--help", "help"):
            print("Minecraft CLI Launcher (mcl-win)")
            print("Usage:")
            print("  mcl                   - Start the interactive version selector (Arrow Keys!)")
            print("  mcl <version>         - Launch a specific local version (e.g. mcl \"fabric:1.20.1\")")
            print("  mcl <query>           - Fuzzy-launch a matched version (e.g. mcl fabric)")
            print("  mcl -u <username>     - Set username for launcher")
            return
            
        if args[0] == "-u" and len(args) > 2:
            settings["username"] = args[1]
            args = args[2:]
            if args:
                query = " ".join(args)
                best_match = fuzzy_find_version(query, local_versions) or query
                if "explicitly_installed" not in settings:
                    settings["explicitly_installed"] = []
                if best_match not in settings["explicitly_installed"]:
                    settings["explicitly_installed"].append(best_match)
                config.save_settings(settings)
                launch_game(best_match, settings, minecraft_dir, mode="foreground")
                return
                
        query = " ".join(args)
        best_match = fuzzy_find_version(query, local_versions)
        if best_match:
            print(f"[SMART-MATCH] Fuzzy-matched query \"{query}\" to installed version: \"{best_match}\"")
            launch_game(best_match, settings, minecraft_dir, mode="foreground")
        else:
            print(f"[REMOTE] Version \"{query}\" not found locally. Preparing download...")
            if "explicitly_installed" not in settings:
                settings["explicitly_installed"] = []
            if query not in settings["explicitly_installed"]:
                settings["explicitly_installed"].append(query)
            config.save_settings(settings)
            launch_game(query, settings, minecraft_dir, mode="foreground")
        return
        
    while True:
        local_versions = get_local_versions(minecraft_dir, settings)
        selected_res = run_tui(local_versions, settings, config.save_settings)
        if selected_res == "__REFRESH__":
            continue
        if selected_res:
            mode, selected_version = selected_res
            if "explicitly_installed" not in settings:
                settings["explicitly_installed"] = []
            if selected_version not in settings["explicitly_installed"]:
                settings["explicitly_installed"].append(selected_version)
            settings["last_played_version"] = selected_version
            config.save_settings(settings)
            launch_game(selected_version, settings, minecraft_dir, mode=mode)
        break

if __name__ == "__main__":
    main()