import os
import sys
import subprocess

if os.name == "nt":
    os.system("")  # Enable ANSI terminal color support in Windows CMD/PowerShell

def read_key():
    """
    Reads user input across Windows (msvcrt) and Unix (termios/tty).
    Uses basic keys (Arrow keys, Enter, Backspace, Esc, simple letter shortcuts).
    """
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'up'
            if ch2 == b'P': return 'down'
            if ch2 == b'K': return 'left'
            if ch2 == b'M': return 'right'
            if ch2 == b'S': return 'delete'
            if ch2 == b'I': return 'page_up'
            if ch2 == b'Q': return 'page_down'
            if ch2 == b'G': return 'top'
            if ch2 == b'O': return 'bottom'
            return None
        if ch in (b'\r', b'\n'): return 'select'
        if ch == b'\x1b': return 'quit'
        if ch in (b'\x08', b'\x7f'): return 'back'
        
        char = ch.decode('utf-8', errors='ignore')
        if char == 'L': return 'select_with_logs'
        lower_char = char.lower()
        if lower_char == 'l': return 'launch_logs'
        if lower_char in ('e', 'f'): return 'open_explorer'
        if lower_char == 'd': return 'delete'
        if lower_char in ('n', 'i', 'o'): return 'download'
        if lower_char == 's': return 'settings'
        if lower_char == 'x': return 'quit'
        return lower_char
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'up'
                    elif ch3 == 'B': return 'down'
                    elif ch3 == 'C': return 'right'
                    elif ch3 == 'D': return 'left'
                    elif ch3 in ('5', '6'):
                        sys.stdin.read(1)
                        if ch3 == '5': return 'page_up'
                        if ch3 == '6': return 'page_down'
                return 'quit'
        except Exception:
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
        if ch == 'L': return 'select_with_logs'
        if ch == '\n' or ch == '\r': return 'select'
        if ch == '\x1b' or ch.lower() == 'x': return 'quit'
        if ch in ('\x7f', '\x08'): return 'back'
        
        lower_ch = ch.lower()
        if lower_ch in ('e', 'f'): return 'open_explorer'
        if lower_ch in ('n', 'i', 'o'): return 'download'
        if lower_ch == 'd': return 'delete'
        if lower_ch == 's': return 'settings'
        return lower_ch

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def open_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)
    if os.name == "nt":
        os.startfile(folder_path)
    elif sys.platform == "darwin":
        subprocess.run(["open", folder_path])
    else:
        subprocess.run(["xdg-open", folder_path])

def render_split_pane(title, options, selected_idx, start_viewport, viewport_size, settings, minecraft_dir):
    clear_screen()
    print("\033[1;36m================================================================================\033[0m")
    print(f"\033[1;35m             {title:<72}\033[0m")
    print("\033[1;36m================================================================================\033[0m")
    print()
    
    if selected_idx < start_viewport:
        start_viewport = selected_idx
    elif selected_idx >= start_viewport + viewport_size:
        start_viewport = selected_idx - viewport_size + 1
        
    selected_ver = options[selected_idx] if options else "N/A"
    if selected_ver == "[No installed versions. Press 'N' to install]":
        selected_ver_display = "None"
        sandbox_status = "N/A"
        worlds_status = "N/A"
        mod_count = 0
    else:
        selected_ver_display = selected_ver
        if settings.get("isolate_instances", True):
            safe_folder_name = selected_ver.replace(":", "_")
            instance_dir = os.path.join(minecraft_dir, "instances", safe_folder_name)
            mods_dir = os.path.join(instance_dir, "mods")
            sandbox_status = "YES (Isolated Workspace)"
        else:
            instance_dir = minecraft_dir
            mods_dir = os.path.join(minecraft_dir, "mods")
            sandbox_status = "NO (Using Global Directory)"
            
        worlds_status = "[Isolated]" if settings.get("isolate_saves", False) else "[Shared Global]"
        mod_count = 0
        if os.path.isdir(mods_dir):
            try:
                mod_count = len([f for f in os.listdir(mods_dir) if f.endswith(".jar")])
            except Exception:
                pass

    right_pane = [
        "\033[1;33m[ SELECTED INSTANCE DETAILS ]\033[0m",
        f"Name:       \033[1;32m{selected_ver_display}\033[0m",
        f"Sandbox:    {sandbox_status}",
        f"Worlds:     {worlds_status}",
        f"Active Mods:\033[1;34m {mod_count} jars\033[0m",
        f"Profile:    \033[1;32m{settings.get('username', 'Player')}\033[0m",
        "",
        "\033[1;33m[ KEYBOARD ACTIONS ]\033[0m",
        "  \033[1;32m[Enter]\033[0m Launch Game" if selected_ver_display != "None" else "  [Enter] (Disabled)",
        "  \033[1;35m[L]\033[0m Launch with Console Logs" if selected_ver_display != "None" else "  [L] (Disabled)",
        "  \033[1;32m[E]\033[0m Open Mods Folder in Explorer" if selected_ver_display != "None" else "  [E] (Disabled)",
        "  \033[1;31m[D]\033[0m Delete Instance from Disk" if selected_ver_display != "None" else "  [D] (Disabled)",
        "  \033[1;34m[N]\033[0m Install / Download New Version",
        "  \033[1;33m[S]\033[0m Settings | \033[1;30m[Esc/X]\033[0m Exit"
    ]
    
    while len(right_pane) < viewport_size:
        right_pane.append("")
        
    for i in range(viewport_size):
        opt_idx = start_viewport + i
        left_str = ""
        if opt_idx < len(options):
            prefix = " > " if opt_idx == selected_idx else "   "
            color = "\033[1;32m" if opt_idx == selected_idx else "\033[0m"
            left_str = f"{prefix}{color}{options[opt_idx][:32]:<32}\033[0m"
        else:
            left_str = " " * 35
            
        right_str = right_pane[i]
        print(f"{left_str}  \033[90m┃\033[0m  {right_str}")
        
    print()
    print("\033[90m" + "-" * 80 + "\033[0m")
    print("\033[90m[↑/↓] Navigate | [Enter] Launch | [E] Open Folder | [D] Delete | [N] Install | [S] Settings\033[0m")
    print("\033[90m" + "-" * 80 + "\033[0m")
    
    return start_viewport

def run_settings_menu(settings, save_callback):
    selected = 0
    while True:
        options = [
            f"Username: {settings['username']}",
            f"Isolate Instances: {'[YES]' if settings['isolate_instances'] else '[NO]'}",
            f"Isolate Worlds (Saves): {'[YES]' if settings['isolate_saves'] else '[NO]'}",
            f"Isolate Resource Packs: {'[YES]' if settings['isolate_resourcepacks'] else '[NO]'}",
            "Back to Main Menu"
        ]
        clear_screen()
        print("\033[1;36m==================================================\033[0m")
        print("\033[1;35m             SETTINGS - CONFIGURATION             \033[0m")
        print("\033[1;36m==================================================\033[0m")
        print()
        for idx, opt in enumerate(options):
            prefix = " > " if idx == selected else "   "
            color = "\033[1;32m" if idx == selected else "\033[0m"
            print(f"{prefix}{color}{opt}\033[0m")
        print()
        print("\033[90m" + "-" * 50 + "\033[0m")
        print("\033[90m[↑/↓] Navigate | [Enter] Change | [Esc/X] Back\033[0m")
        print("\033[90m" + "-" * 50 + "\033[0m")
        
        key = read_key()
        if key == 'up':
            selected = (selected - 1) % len(options)
        elif key == 'down':
            selected = (selected + 1) % len(options)
        elif key == 'select':
            if selected == 0:
                clear_screen()
                print("Enter new Username:")
                new_user = input("> ").strip()
                if new_user:
                    settings["username"] = new_user
                    save_callback(settings)
            elif selected == 1:
                settings["isolate_instances"] = not settings["isolate_instances"]
                save_callback(settings)
            elif selected == 2:
                settings["isolate_saves"] = not settings["isolate_saves"]
                save_callback(settings)
            elif selected == 3:
                settings["isolate_resourcepacks"] = not settings["isolate_resourcepacks"]
                save_callback(settings)
            elif selected == 4:
                break
        elif key in ('back', 'quit', 'esc'):
            break

def fetch_mojang_releases():
    fallback_releases = [
        "1.21.4", "1.21.1", "1.20.1", "1.19.2", "1.18.2", "1.16.5", 
        "1.12.2", "1.8.9", "1.7.10"
    ]
    try:
        cmd = [sys.executable, "-m", "portablemc", "search", "-k", "mojang"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3.0)
        if res.returncode != 0:
            return fallback_releases
            
        releases = []
        for line in res.stdout.splitlines():
            if "│" in line:
                parts = [p.strip() for p in line.split("│")]
                if len(parts) >= 3 and parts[1] == "release":
                    ver = parts[2]
                    if ver and not any(x in ver.lower() for x in ["pre", "rc", "snapshot"]):
                        releases.append(ver)
                        
        if releases:
            return releases
    except Exception:
        pass
    return fallback_releases

def run_version_picker(category_name, releases):
    selected = 0
    start_view = 0
    viewport_size = 15
    
    while True:
        clear_screen()
        print("\033[1;36m==================================================\033[0m")
        print(f"\033[1;35m       SELECT VERSION FOR: {category_name.upper()}\033[0m")
        print("\033[1;36m==================================================\033[0m")
        print()
        
        if selected < start_view:
            start_view = selected
        elif selected >= start_view + viewport_size:
            start_view = selected - viewport_size + 1
            
        for i in range(viewport_size):
            idx = start_view + i
            if idx < len(releases):
                prefix = " > " if idx == selected else "   "
                color = "\033[1;32m" if idx == selected else "\033[0m"
                print(f"{prefix}{color}{releases[idx]}\033[0m")
            else:
                print()
                
        print()
        print("\033[90m" + "-" * 50 + "\033[0m")
        print("\033[90m[↑/↓] Navigate | [Enter] Confirm | [Esc/Backspace] Back\033[0m")
        print("\033[90m" + "-" * 50 + "\033[0m")
        
        key = read_key()
        if key == 'up':
            selected = (selected - 1) % len(releases)
        elif key == 'down':
            selected = (selected + 1) % len(releases)
        elif key == 'page_up':
            selected = max(0, selected - 10)
        elif key == 'page_down':
            selected = min(len(releases) - 1, selected + 10)
        elif key == 'top':
            selected = 0
        elif key == 'bottom':
            selected = len(releases) - 1
        elif key == 'select':
            return releases[selected]
        elif key in ('back', 'quit', 'esc'):
            return None

def run_install_menu(settings, save_callback):
    modloaders = ["Fabric", "Forge", "NeoForge", "Quilt", "Vanilla (Plain)"]
    selected = 0
    
    while True:
        clear_screen()
        print("\033[1;36m==================================================\033[0m")
        print("\033[1;35m           INSTALL NEW MINECRAFT VERSION          \033[0m")
        print("\033[1;36m==================================================\033[0m")
        print()
        print("Select ModLoader or Platform:")
        print()
        for idx, loader in enumerate(modloaders):
            prefix = " > " if idx == selected else "   "
            color = "\033[1;32m" if idx == selected else "\033[0m"
            print(f"{prefix}{color}{loader}\033[0m")
        print()
        print("\033[90m" + "-" * 50 + "\033[0m")
        print("\033[90m[↑/↓] Navigate | [Enter] Select | [Esc] Cancel\033[0m")
        print("\033[90m" + "-" * 50 + "\033[0m")
        
        key = read_key()
        if key == 'up':
            selected = (selected - 1) % len(modloaders)
        elif key == 'down':
            selected = (selected + 1) % len(modloaders)
        elif key == 'select':
            loader_choice = modloaders[selected]
            releases = fetch_mojang_releases()
            mc_ver = run_version_picker(loader_choice, releases)
            if mc_ver:
                if loader_choice == "Vanilla (Plain)":
                    ver_id = mc_ver
                else:
                    ver_id = f"{loader_choice.lower()}:{mc_ver}"
                return ver_id
        elif key in ('back', 'quit', 'esc'):
            return None

def run_tui(local_versions, settings, save_callback):
    if os.name == "nt":
        minecraft_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".minecraft")
    else:
        minecraft_dir = os.path.expanduser("~/.minecraft")
        
    options = list(local_versions) if local_versions else ["[No installed versions. Press 'N' to install]"]
    selected_idx = 0
    start_viewport = 0
    viewport_size = 14
    
    while True:
        start_viewport = render_split_pane(
            "MINECRAFT LAUNCHER",
            options,
            selected_idx,
            start_viewport,
            viewport_size,
            settings,
            minecraft_dir
        )
        
        key = read_key()
        
        if key == 'up':
            if options:
                selected_idx = (selected_idx - 1) % len(options)
        elif key == 'down':
            if options:
                selected_idx = (selected_idx + 1) % len(options)
        elif key in ('select', 'launch'):
            if options and options[selected_idx] != "[No installed versions. Press 'N' to install]":
                return ("background", options[selected_idx])
        elif key == 'select_with_logs':
            if options and options[selected_idx] != "[No installed versions. Press 'N' to install]":
                return ("foreground", options[selected_idx])
        elif key == 'open_explorer':
            if options and options[selected_idx] != "[No installed versions. Press 'N' to install]":
                ver = options[selected_idx]
                safe_folder_name = ver.replace(":", "_")
                if settings.get("isolate_instances", True):
                    folder = os.path.join(minecraft_dir, "instances", safe_folder_name, "mods")
                else:
                    folder = os.path.join(minecraft_dir, "mods")
                open_folder(folder)
        elif key == 'delete':
            if options and options[selected_idx] != "[No installed versions. Press 'N' to install]":
                ver_to_del = options[selected_idx]
                clear_screen()
                print(f"\033[1;31mAre you sure you want to delete {ver_to_del}? (y/N)\033[0m")
                confirm = read_key()
                if confirm == 'y':
                    if "explicitly_installed" in settings and ver_to_del in settings["explicitly_installed"]:
                        settings["explicitly_installed"].remove(ver_to_del)
                        save_callback(settings)
                    
                    safe_folder_name = ver_to_del.replace(":", "_")
                    inst_dir = os.path.join(minecraft_dir, "instances", safe_folder_name)
                    if os.path.exists(inst_dir):
                        import shutil
                        shutil.rmtree(inst_dir, ignore_errors=True)
                    return "__REFRESH__"
        elif key == 'download':
            new_ver = run_install_menu(settings, save_callback)
            if new_ver:
                from mcl_launcher.launcher import install_game_version
                install_game_version(new_ver, settings, minecraft_dir)
                return "__REFRESH__"
        elif key == 'settings':
            run_settings_menu(settings, save_callback)
            return "__REFRESH__"
        elif key in ('quit', 'esc'):
            clear_screen()
            sys.exit(0)