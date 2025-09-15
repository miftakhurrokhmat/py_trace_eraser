#!/usr/bin/env python3
"""
erase_today_browser_history.py

Utility untuk menghapus *history hari ini* di browser Chrome, Edge, dan Firefox.

📌 Cara Pakai:
    python erase_today_browser_history.py
        -> Hapus semua history hari ini (semua profile terdeteksi)

    python erase_today_browser_history.py --dry-run
        -> Cek berapa history hari ini, tanpa hapus

    python erase_today_browser_history.py --profile "Profile 32"
        -> Hapus hanya history dari profile Chrome "Profile 32"

    python erase_today_browser_history.py --dry-run --profile "abcd.default-release"
        -> Dry run hanya untuk Firefox profile "abcd.default-release"

    python erase_today_browser_history.py --list-profiles
        -> List semua profile yang terdeteksi (Chrome, Edge, Firefox) dengan email/nama

⚠️ Catatan:
- Script otomatis membuat backup `.bak.TIMESTAMP` sebelum menghapus.
- Jalankan dengan user yang sama pemilik browser.
- Tutup browser sebelum eksekusi agar hasil maksimal.
- Tidak menyentuh password, cookies, maupun bookmark.
"""

import os, sys, sqlite3, shutil, json
from datetime import datetime, time, timedelta, timezone

# --- Argumen ---
DRY_RUN = "--dry-run" in sys.argv
LIST_ONLY = "--list-profiles" in sys.argv
PROFILE_NAME = None
if "--profile" in sys.argv:
    try:
        PROFILE_NAME = sys.argv[sys.argv.index("--profile")+1]
    except IndexError:
        print("⚠️ Gunakan: --profile <NamaProfile>")
        sys.exit(1)

# --- Waktu hari ini ---
def local_midnights():
    now = datetime.now().astimezone()
    start = datetime.combine(now.date(), time.min).astimezone()
    return start, start + timedelta(days=1)

def to_chrome_time(dt):
    epoch = datetime(1601,1,1,tzinfo=timezone.utc)
    return int((dt.astimezone(timezone.utc)-epoch).total_seconds()*1_000_000)

def to_unix_usec(dt):
    epoch = datetime(1970,1,1,tzinfo=timezone.utc)
    return int((dt.astimezone(timezone.utc)-epoch).total_seconds()*1_000_000)

def safe_copy(path):
    tmp = path+".tmpcopy"
    if os.path.exists(tmp): os.remove(tmp)
    shutil.copy2(path, tmp)
    return tmp

def backup(path):
    bak = path+f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(path,bak)
    return bak

# --- List Profiles ---
def list_chromium_profiles(base, browser_name):
    results = []
    if not os.path.exists(base): return results
    for prof in ["Default"] + [d for d in os.listdir(base) if d.startswith("Profile")]:
        pref_path = os.path.join(base, prof, "Preferences")
        emails = []
        pname = prof
        if os.path.exists(pref_path):
            try:
                with open(pref_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pname = data.get("profile", {}).get("name", prof)
                emails = [acc.get("email") for acc in data.get("account_info", []) if "email" in acc]
            except: pass
        results.append((browser_name, prof, pname, emails))
    return results

def list_firefox_profiles(appdata):
    results = []
    ff=os.path.join(appdata,"Mozilla","Firefox","Profiles")
    if not os.path.exists(ff): return results
    for d in os.listdir(ff):
        results.append(("Firefox", d, d, []))
    return results

def show_profiles():
    local=os.getenv("LOCALAPPDATA"); app=os.getenv("APPDATA")
    if not local or not app:
        print("❌ LOCALAPPDATA / APPDATA tidak ada (script hanya untuk Windows).")
        return
    profiles=[]
    profiles+=list_chromium_profiles(os.path.join(local,"Google","Chrome","User Data"),"Chrome")
    profiles+=list_chromium_profiles(os.path.join(local,"Microsoft","Edge","User Data"),"Edge")
    profiles+=list_firefox_profiles(app)
    if not profiles:
        print("Tidak ada profile terdeteksi.")
    for b,folder,name,emails in profiles:
        print(f"🌐 {b} | 📂 {folder} | Nama: {name} | Email: {', '.join(emails) if emails else '-'}")

# --- Chromium (Chrome / Edge) ---
def process_chromium(history, start, end):
    print(f"-> Chromium DB: {history}")
    if not os.path.exists(history): return
    if DRY_RUN:
        conn=sqlite3.connect(history);cur=conn.cursor()
        cur.execute("SELECT COUNT(*) FROM visits WHERE visit_time BETWEEN ? AND ?",
                    (to_chrome_time(start),to_chrome_time(end)))
        print(f"[DRY RUN] {cur.fetchone()[0]} visits today.")
        conn.close(); return
    bak=backup(history)
    tmp=safe_copy(history)
    conn=sqlite3.connect(tmp);cur=conn.cursor()
    cur.execute("DELETE FROM visits WHERE visit_time BETWEEN ? AND ?",
                (to_chrome_time(start),to_chrome_time(end)))
    conn.commit()
    cur.execute("DELETE FROM urls WHERE id NOT IN (SELECT url FROM visits)")
    conn.commit()
    cur.close()
    conn.execute("VACUUM");conn.close()
    shutil.copy2(tmp,history);os.remove(tmp)
    print(f"Deleted visits. Backup: {bak}")

def find_chromium_profiles(base):
    if not os.path.exists(base): return []
    if PROFILE_NAME:
        path=os.path.join(base,PROFILE_NAME,"History")
        return [path] if os.path.exists(path) else []
    else:
        results=[]
        for d in ["Default"]+[f for f in os.listdir(base) if d.startswith("Profile")]:
            h=os.path.join(base,d,"History")
            if os.path.exists(h): results.append(h)
        return results

# --- Firefox ---
def process_firefox(places, start, end):
    print(f"-> Firefox DB: {places}")
    if not os.path.exists(places): return
    if DRY_RUN:
        conn=sqlite3.connect(places);cur=conn.cursor()
        cur.execute("SELECT COUNT(*) FROM moz_historyvisits WHERE visit_date BETWEEN ? AND ?",
                    (to_unix_usec(start),to_unix_usec(end)))
        print(f"[DRY RUN] {cur.fetchone()[0]} visits today.")
        conn.close(); return
    bak=backup(places)
    tmp=safe_copy(places)
    conn=sqlite3.connect(tmp);cur=conn.cursor()
    cur.execute("DELETE FROM moz_historyvisits WHERE visit_date BETWEEN ? AND ?",
                (to_unix_usec(start),to_unix_usec(end)))
    conn.commit()
    cur.execute("DELETE FROM moz_places WHERE id NOT IN (SELECT place_id FROM moz_historyvisits)")
    conn.commit()
    cur.close()
    conn.execute("VACUUM");conn.close()
    shutil.copy2(tmp,places);os.remove(tmp)
    print(f"Deleted visits. Backup: {bak}")

def find_firefox_profiles(appdata):
    ff=os.path.join(appdata,"Mozilla","Firefox","Profiles")
    if not os.path.exists(ff): return []
    results=[]
    for d in os.listdir(ff):
        if PROFILE_NAME and PROFILE_NAME!=d: continue
        places=os.path.join(ff,d,"places.sqlite")
        if os.path.exists(places): results.append(places)
    return results

# --- Main ---
def main():
    if LIST_ONLY:
        show_profiles()
        return  # ⬅️ fix: berhenti setelah list

    start,end=local_midnights()
    print(f"{'DRY RUN - ' if DRY_RUN else ''}History today: {start} → {end}")

    local=os.getenv("LOCALAPPDATA")
    app=os.getenv("APPDATA")
    if not local or not app:
        print("❌ Environment tidak ditemukan. Script ini hanya untuk Windows (butuh LOCALAPPDATA & APPDATA).")
        sys.exit(1)

    # Chrome
    for h in find_chromium_profiles(os.path.join(local,"Google","Chrome","User Data")):
        process_chromium(h,start,end)

    # Edge
    for h in find_chromium_profiles(os.path.join(local,"Microsoft","Edge","User Data")):
        process_chromium(h,start,end)

    # Firefox
    for p in find_firefox_profiles(app):
        process_firefox(p,start,end)

if __name__=="__main__":
    main()
