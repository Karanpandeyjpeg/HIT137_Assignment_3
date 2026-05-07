# Spot The Difference Game

A Tkinter game that loads an image, creates five visual differences, and lets the player find them.

## Requirements

- Python 3.9 or newer
- Tk 8.6 or newer
- Python packages listed in `requirements.txt`

On macOS, avoid the built-in `/usr/bin/python3` if it uses Tk 8.5. Install Python from python.org, then run the commands below with that Python.

## Run

```bash
/opt/homebrew/bin/python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python spot_difference_game.py
```

If the app says Tk is too old, install a newer Python that includes Tk 8.6 or newer.
