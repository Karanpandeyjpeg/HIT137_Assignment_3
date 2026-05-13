# Spot The Difference Game

A Tkinter game that loads an image, creates five visual differences, and lets the player find them.

## Requirements

- Python 3.9 or newer
- Tk 8.6 or newer
- Python packages listed in `requirements.txt`

On macOS, avoid the built-in `/usr/bin/python3` if it uses Tk 8.5. Install Python from python.org, then run the commands below with that Python.

## Run

### macOS

```bash
/opt/homebrew/bin/python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python spot_difference_game.py
```

If the app says Tk is too old, install a newer Python that includes Tk 8.6 or newer.

### Windows

Open PowerShell and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python spot_difference_game.py
```

If `python` points to an older version, use the full path to a Python 3.9+ install, for example:

```powershell
C:\Python39\python.exe -m venv .venv
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe spot_difference_game.py
```
````
This is the code block that represents the suggested code change:
```markdown
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python spot_difference_game.py
```
