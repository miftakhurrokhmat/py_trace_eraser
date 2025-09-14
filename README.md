# py_trace_eraser

Python-based tool to erase activity traces on Windows.
Cleans Recent Items, Jump Lists, Temp files, Clipboard, Browser cache, Registry entries, Event Logs.

## Features
- 🗑️ Clean Recent Items
- 🗑️ Clean Jump Lists
- 🗑️ Clean Temp files
- 📋 Clear Clipboard
- 🌐 Clear Browser cache (Chrome, Edge, optional Firefox)
- 🔍 Clear File Explorer Search History
- ⚡ Clear Run Dialog History (Win + R)
- 📄 Clear Windows Event Logs (System, Application, Security)
- 📊 Summary of deleted files and size

## Usage
1. Install Python 3.10+
2. Clone this repository or extract the zip
3. Run:
   ```bash
   python trace_eraser.py
   ```
   Or double click `run_cleaner.bat`

## Configuration
Edit `config.json` to enable/disable cleaning options.

Example:
```json
{
  "recent": true,
  "jumplist": true,
  "temp": true,
  "clipboard": true,
  "browser_cache": {
    "chrome": true,
    "edge": true,
    "firefox": false
  },
  "preserve_passwords": true,
  "search_history": true,
  "run_history": true,
  "event_logs": true
}
```

## License
MIT License
