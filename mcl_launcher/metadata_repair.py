import os
import json

def repair_version_metadata(version_name, minecraft_dir=None):
    if minecraft_dir is None:
        if os.name == "nt":
            minecraft_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".minecraft")
        else:
            minecraft_dir = os.path.expanduser("~/.minecraft")
        
    version_json_path = os.path.join(minecraft_dir, "versions", version_name, f"{version_name}.json")
    
    if not os.path.exists(version_json_path):
        return False
        
    try:
        with open(version_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        repaired = False
        
        if "javaVersion" in data and isinstance(data["javaVersion"], dict):
            java_ver = data["javaVersion"]
            if "majorVersion" in java_ver:
                val = java_ver["majorVersion"]
                if isinstance(val, str):
                    try:
                        java_ver["majorVersion"] = int(val)
                        repaired = True
                    except ValueError:
                        pass
                        
        if repaired:
            with open(version_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
            
    except Exception:
        pass
        
    return False