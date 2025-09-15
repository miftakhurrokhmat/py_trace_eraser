# py_trace_eraser

Python-based tool to erase activity traces on Windows.\
Cleans Recent Items, Jump Lists, Temp files, Clipboard, Browser cache,
Registry entries, Event Logs, Start Menu history, Thumbnails, and more.

## Features

-   🗑️ Clean **Recent Items**
-   🧹 Force clean **Recent + Destinations** (brute force delete)
-   🗑️ Clean **Jump Lists**
-   🗑️ Clean **Temp files**
-   📋 Clear **Clipboard**
-   🌐 Clear **Browser cache** (Chrome, Edge, optional Firefox)
-   🔍 Clear **File Explorer Search History**
-   ⚡ Clear **Run Dialog History (Win + R)**
-   🖼️ Clear \*\*Thumbnail cache (thumbcache\*.db)\*\*
-   📄 Clear **Windows Event Logs** (System, Application, Security)
-   📌 Clear **Start Menu recent apps & recommended cache**
-   🚫 Disable **Recommended section** in Start Menu + update Explorer
    privacy settings
-   🔄 Restart **Windows Explorer** automatically (optional)
-   📊 Summary of deleted files and size

## Usage

1.  Install **Python 3.10+**

2.  Clone this repository or extract the zip

3.  Run:

    ``` bash
    python trace_eraser.py
    ```

    Or double click `run_cleaner.bat`

## Configuration

Edit `config.json` to enable/disable cleaning options.

Example:

``` json
{
  "recent": true,
  "force_recent": true,
  "jumplist": true,
  "temp": true,
  "clipboard": true,
  "browser_cache": {
    "chrome": true,
    "edge": true,
    "firefox": false
  },
  "search_history": true,
  "run_history": true,
  "thumbnails": true,
  "event_logs": true,
  "startmenu_recent": true,
  "disable_recommended": true,
  "restart_explorer": true
}
```

## Notes

-   Browser cleanup skips **passwords & cookies** by default.
-   Explorer privacy settings can disable **recent documents**,
    **frequent programs**, and **recommended section**.
-   Start Menu cache cleanup automatically creates a **backup** of
    `ActivitiesCache.db`.

## License

MIT License
