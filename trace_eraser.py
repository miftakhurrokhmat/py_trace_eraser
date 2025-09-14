import os
import json
import subprocess

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total

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

def clean_recent():
    targets = [os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Recent Items")]
    total_files, total_size = 0, 0
    for t in targets:
        f, s = clean_folder(t)
        total_files += f
        total_size += s
    return total_files, total_size

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
    temp = os.getenv("TEMP")
    return clean_folder(temp)

def clean_clipboard():
    try:
        subprocess.run("echo off | clip", shell=True)
        return 1, 0
    except:
        return 0, 0

def clean_browser_cache(config):
    total_files, total_size = 0, 0
    localapp = os.getenv("LOCALAPPDATA")

    # Chrome
    if config.get("chrome", False):
        chrome_cache = os.path.join(localapp, r"Google\Chrome\User Data\Default\Cache")
        f, s = clean_folder(chrome_cache, whitelist=["Login Data", "Cookies"])
        total_files += f
        total_size += s

    # Edge
    if config.get("edge", False):
        edge_cache = os.path.join(localapp, r"Microsoft\Edge\User Data\Default\Cache")
        f, s = clean_folder(edge_cache, whitelist=["Login Data", "Cookies"])
        total_files += f
        total_size += s

    # Firefox (opsional)
    if config.get("firefox", False):
        firefox = os.path.join(os.getenv("APPDATA"), r"Mozilla\Firefox\Profiles")
        for root, dirs, _ in os.walk(firefox):
            for d in dirs:
                cache_path = os.path.join(root, d, "cache2")
                f, s = clean_folder(cache_path, whitelist=["logins.json", "key4.db"])
                total_files += f
                total_size += s
    return total_files, total_size

if __name__ == "__main__":
    config = load_config()
    total_files, total_size = 0, 0

    if config.get("recent", False):
        f, s = clean_recent()
        total_files += f
        total_size += s
        print(f"🗑️ Recent: {f} files, {s//1024//1024} MB")

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

    print("\n✅ Selesai!")
    print(f"Total dibersihkan: {total_files} files, {total_size//1024//1024} MB")
