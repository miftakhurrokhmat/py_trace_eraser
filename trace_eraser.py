import os
import json
import subprocess
import winreg
import sqlite3
import shutil
import glob

CONFIG_FILE = "config.json"


# --- Config Loader ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# --- Utility Functions ---
def clean_folder(path, whitelist=None):
    deleted_files, deleted_size = 0, 0
    if not os.path.exists(path):
        return deleted_files, deleted_size
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if whitelist and file in whitelist:
                continue
            try:
                deleted_size += os.path.getsize(file_path)
                os.remove(file_path)
                deleted_files += 1
            except:
                pass
    return deleted_files, deleted_size


# --- Clean Recent / Jumplist / Temp / Clipboard ---
def clean_recent():
    target = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Recent Items")
    return clean_folder(target)


def force_clean_recent():
    cmds = [
        r'del /f /s /q /a "%APPDATA%\Microsoft\Windows\Recent Items\*"',
        r'del /f /s /q /a "%APPDATA%\Microsoft\Windows\Recent\AutomaticDestinations\*"',
        r'del /f /s /q /a "%APPDATA%\Microsoft\Windows\Recent\CustomDestinations\*"'
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, text=True)
        except:
            pass
    return 0, 0


def clean_jumplist():
    targets = [
        os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Recent\AutomaticDestinations"),
        os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Recent\CustomDestinations"),
    ]
    total_files, total_size = 0, 0
    for t in targets:
        f, s = clean_folder(t)
        total_files += f
        total_size += s
    return total_files, total_size


def clean_temp():
    return clean_folder(os.getenv("TEMP"))


def clean_clipboard():
    try:
        subprocess.run("echo off | clip", shell=True)
        return 1, 0
    except:
        return 0, 0


# --- Browser Cache ---
def clean_browser_cache(config):
    total_files, total_size = 0, 0
    localapp = os.getenv("LOCALAPPDATA")

    if config.get("chrome", False):
        chrome_cache = os.path.join(localapp, r"Google\Chrome\User Data\Default\Cache")
        f, s = clean_folder(chrome_cache, whitelist=["Login Data", "Cookies"])
        total_files += f
        total_size += s

    if config.get("edge", False):
        edge_cache = os.path.join(localapp, r"Microsoft\Edge\User Data\Default\Cache")
        f, s = clean_folder(edge_cache, whitelist=["Login Data", "Cookies"])
        total_files += f
        total_size += s

    if config.get("firefox", False):
        firefox = os.path.join(os.getenv("APPDATA"), r"Mozilla\Firefox\Profiles")
        for root, dirs, _ in os.walk(firefox):
            for d in dirs:
                cache_path = os.path.join(root, d, "cache2")
                f, s = clean_folder(cache_path, whitelist=["logins.json", "key4.db"])
                total_files += f
                total_size += s
    return total_files, total_size


# --- Registry Cleanup ---
def clean_registry_keys(path):
    deleted = 0
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
        while True:
            try:
                subkey = winreg.EnumValue(key, 0)
                winreg.DeleteValue(key, subkey[0])
                deleted += 1
            except OSError:
                break
    except:
        pass
    return deleted


# --- Thumbnails ---
def clean_thumbnails():
    explorer = os.path.join(os.getenv("LOCALAPPDATA"), r"Microsoft\Windows\Explorer")
    deleted = 0
    if os.path.exists(explorer):
        for file in os.listdir(explorer):
            if file.startswith("thumbcache") and file.endswith(".db"):
                try:
                    os.remove(os.path.join(explorer, file))
                    deleted += 1
                except:
                    pass
    return deleted


# --- Event Logs ---
def clear_event_logs():
    logs = ["Application", "System", "Security"]
    cleared = 0
    for log in logs:
        try:
            subprocess.run(f"wevtutil cl {log}", shell=True, check=True)
            cleared += 1
        except:
            pass
    return cleared


# --- Restart Explorer ---
def restart_explorer():
    try:
        subprocess.run("taskkill /f /im explorer.exe >nul 2>&1", shell=True)
        subprocess.run("start explorer.exe", shell=True)
        return True
    except:
        return False


# --- Start Menu Recommended ---
def clear_startmenu_recent():
    deleted = 0
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartPage2",
            0,
            winreg.KEY_ALL_ACCESS
        )
        while True:
            try:
                name, _, _ = winreg.EnumValue(key, 0)
                winreg.DeleteValue(key, name)
                deleted += 1
            except OSError:
                break
    except:
        pass
    return deleted


def clear_startmenu_db():
    path = os.path.join(
        os.getenv("LOCALAPPDATA"),
        r"Packages\Microsoft.Windows.StartMenuExperienceHost_cw5n1h2txyewy\LocalState"
    )
    f, s = clean_folder(path)
    return f


def clear_recommended_cache():
    """Hapus aktivitas dari database yang dipakai Recommended di Start Menu (dengan backup)."""
    db_pattern = os.path.join(
        os.getenv("LOCALAPPDATA"),
        r"ConnectedDevicesPlatform\L.*\ActivitiesCache.db"
    )
    deleted = 0
    for db in glob.glob(db_pattern):
        try:
            backup = db + ".bak"
            shutil.copy2(db, backup)

            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("DELETE FROM Activity")
            deleted += cur.rowcount
            conn.commit()
            conn.close()
            print(f"📂 Backup created: {backup}")
        except Exception as e:
            print(f"⚠️ Gagal bersihin {db}: {e}")
    return deleted


# --- Explorer History + Privacy ---
def clear_explorer_history():
    deleted = 0
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
            while True:
                try:
                    name, _, _ = winreg.EnumValue(key, 0)
                    winreg.DeleteValue(key, name)
                    deleted += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass

        subprocess.run("Rundll32.exe inetcpl.cpl,ClearMyTracksByProcess 255", shell=True)

    except Exception as e:
        print(f"⚠️ Gagal clear Explorer history: {e}")
    return deleted


def set_explorer_privacy(disable_recent=True, disable_frequent=True, disable_recommended=True):
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        )
        if disable_recent:
            winreg.SetValueEx(key, "Start_TrackDocs", 0, winreg.REG_DWORD, 0)
        if disable_frequent:
            winreg.SetValueEx(key, "Start_TrackProgs", 0, winreg.REG_DWORD, 0)
        if disable_recommended:
            winreg.SetValueEx(key, "Start_ShowRecommendedSection", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"⚠️ Gagal set Explorer Privacy: {e}")
        return False


# --- Disable Recommended Section ---
def disable_recommended_section():
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Policies\Microsoft\Windows\Explorer"
        )
        winreg.SetValueEx(key, "HideRecommendedSection", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"⚠️ Gagal disable Recommended: {e}")
        return False


# --- Main Execution ---
if __name__ == "__main__":
    config = load_config()
    total_files, total_size = 0, 0

    if config.get("recent", False):
        f, s = clean_recent()
        total_files += f
        total_size += s
        print(f"🗑️ Recent: {f} files, {s//1024//1024} MB")

    if config.get("force_recent", False):
        force_clean_recent()
        print("🧹 Forced deletion: Recent Items + Destinations")

    if config.get("jumplist", False):
        f, s = clean_jumplist()
        total_files += f
        total_size += s
        print(f"🗑️ Jumplist: {f} files, {s//1024//1024} MB")

    if config.get("temp", False):
        f, s = clean_temp()
        total_files += f
        total_size += s
        print(f"🗑️ Temp: {f} files, {s//1024//1024} MB")

    if config.get("clipboard", False):
        f, _ = clean_clipboard()
        total_files += f
        print("📋 Clipboard cleared")

    if "browser_cache" in config:
        f, s = clean_browser_cache(config["browser_cache"])
        total_files += f
        total_size += s
        print(f"🌐 Browser Cache: {f} files, {s//1024//1024} MB")

    if config.get("search_history", False):
        reg_deleted = clean_registry_keys(r"Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery")
        print(f"🔍 Search History cleared: {reg_deleted} keys")

    if config.get("run_history", False):
        reg_deleted = clean_registry_keys(r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU")
        print(f"⚡ Run Dialog History cleared: {reg_deleted} keys")

    if config.get("thumbnails", False):
        thumbs = clean_thumbnails()
        total_files += thumbs
        print(f"🖼️ Thumbnails cleared: {thumbs} files")

    if config.get("event_logs", False):
        cleared_logs = clear_event_logs()
        print(f"📄 Event Logs cleared: {cleared_logs} logs")

    if config.get("startmenu_recent", False):
        reg_deleted = clear_startmenu_recent()
        db_deleted = clear_startmenu_db()
        cache_deleted = clear_recommended_cache()
        print(f"📌 Start Menu cleared: {reg_deleted} registry, {db_deleted} files, {cache_deleted} cache rows")
        
    if config.get("disable_recommended", False):
        cleared = clear_explorer_history()
        if disable_recommended_section() and set_explorer_privacy():
            print(f"🚫 Start Menu Recommended disabled + Explorer privacy updated ({cleared} history cleared)")

    if config.get("restart_explorer", False):
        if restart_explorer():
            print("🔄 Explorer restarted")

    print(f"\n✅ Total cleaned: {total_files} files, {total_size//1024//1024} MB")
