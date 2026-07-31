import urllib.request
import json
import os
import sys
import zipfile
import shutil
from mcl_launcher import __version__

GITHUB_REPO = "Success009/mcl-launcher-win"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def check_for_updates():
    """
    Checks GitHub for newer releases of mcl-launcher-win.
    Returns (has_update, latest_version_tag, download_url)
    """
    try:
        req = urllib.request.Request(
            RELEASES_API,
            headers={"User-Agent": "MCL-Launcher-AutoUpdater"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").lstrip("v")
                
                # Compare semantic versioning
                if tag_name and tag_name != __version__:
                    # Find portable zip download asset
                    download_url = None
                    for asset in data.get("assets", []):
                        if asset.get("name", "").endswith(".zip"):
                            download_url = asset.get("browser_download_url")
                            break
                    return True, tag_name, download_url
    except Exception:
        pass
    return False, __version__, None

def perform_auto_update(download_url):
    """
    Downloads and extracts the latest update package over the current installation directory.
    """
    if not download_url:
        return False
        
    try:
        current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        temp_zip = os.path.join(os.environ.get("TEMP", current_dir), "mcl_update.zip")
        
        print("\n\033[1;33m[AUTO-UPDATE] Downloading latest launcher update...\033[0m")
        req = urllib.request.Request(
            download_url,
            headers={"User-Agent": "MCL-Launcher-AutoUpdater"}
        )
        with urllib.request.urlopen(req) as resp, open(temp_zip, "wb") as out_file:
            shutil.copyfileobj(resp, out_file)
            
        print("\033[1;32m[AUTO-UPDATE] Update downloaded. Applying changes...\033[0m")
        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            zip_ref.extractall(current_dir)
            
        os.remove(temp_zip)
        print("\033[1;32m[AUTO-UPDATE] Update complete! Restarting launcher...\033[0m\n")
        return True
    except Exception as e:
        print(f"\033[1;31m[AUTO-UPDATE ERROR] Update failed: {e}\033[0m")
        return False