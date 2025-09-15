import os
import glob
import shutil

def restore_recommended_cache():
    db_pattern = os.path.join(
        os.getenv("LOCALAPPDATA"),
        r"ConnectedDevicesPlatform\L.*\ActivitiesCache.db"
    )
    restored = 0
    for db in glob.glob(db_pattern):
        bak_file = db + ".bak"
        if os.path.exists(bak_file):
            try:
                shutil.copy2(bak_file, db)
                print(f"✅ Restored: {db} from {bak_file}")
                restored += 1
            except Exception as e:
                print(f"⚠️ Gagal restore {db}: {e}")
        else:
            print(f"❌ Backup not found for {db}")
    return restored


if __name__ == "__main__":
    count = restore_recommended_cache()
    if count > 0:
        print(f"🎉 Success: {count} database(s) restored")
    else:
        print("ℹ️ Tidak ada database yang direstore")
