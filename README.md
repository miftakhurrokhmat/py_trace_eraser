# py_trace_eraser

Python-based tool to erase activity traces on Windows.  
Cleans Recent Items, Jump Lists, Temp files, Clipboard, and Browser cache (without touching saved passwords or cookies).

## Features
- 🗑️ Clean Recent Items
- 🗑️ Clean Jump Lists
- 🗑️ Clean Temp files
- 📋 Clear Clipboard
- 🌐 Clear Browser cache (Chrome, Edge, optional Firefox)
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
  "preserve_passwords": true
}
```

## License
MIT License
