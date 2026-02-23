# PYMUS
**PY-MUS** is a lightweight and minimalist music player that lives entirely in your terminal. Designed for those who prefer the command line, it offers smooth folder navigation, dynamic progress bars, and **Discord Rich Presence** support.

[Spanish Version](https://github.com/Ars-byte/Pymus/blob/main/README.md)

---

## Features
* **TUI Interface:** Visual navigation via terminal with ANSI colors and highlight effects.
* **File Browser:** Explore directories and select music folders in real time.
* **Full Control:** Pause, track skip (`n`/`p`), volume adjustment (`+`/`-`), and time seeking (`h`/`l`).
* **Discord RPC:** Automatically shows what song you're listening to on your Discord profile.
* **Multi-format Support:** Compatible with `.mp3`, `.wav`, `.ogg`, `.flac`, and `.opus`.
* **Efficiency:** Uses `__slots__` to minimize RAM consumption.
* **Modular Architecture:** Clear separation between playback logic (`backend/`) and terminal interface (`frontend/`).

Resource usage:
<img width="991" height="25" alt="image" src="https://github.com/user-attachments/assets/b15fd805-555c-438c-b6a5-7d99fb5f120c" />

## Preview:
On immutable systems:
<img width="1087" height="679" alt="image" src="https://github.com/user-attachments/assets/e6100d2a-e6b5-4884-abec-e4f74aef80f4" />

On mutable systems:
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e7db1c77-f007-41a7-a046-2442ce150030" />

---

## Compatibility
This player is designed to be hardware-agnostic and works anywhere there is a terminal:
* **TTY:** Works without a graphical environment (X11/Wayland).
* **Steam Deck:** Perfect for "Desktop Mode" or via a terminal in game mode to save resources while you play.
* **Termux:** Thanks to its text-based interface, it is ideal for Android devices using Termux.
* **Terminals:** Fully compatible with Linux.

---

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Ars-byte/Pymus.git && cd Pymus
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```
```bash
sudo apt install vlc ffmpeg
```

3. **Run the player:**
```bash
python3 main.py
```

---

## Project Structure

```
Pymus/
├── main.py                   # Entry point — orchestrates backend and frontend
├── backend/
│   ├── __init__.py
│   ├── audio.py              # Audio backends: VLCBackend, FFPlayBackend, make_backend()
│   └── player.py             # Player class: playback state and operations
└── frontend/
    ├── __init__.py
    ├── colors.py             # ANSI codes, W(), hline(), fmt_time()
    ├── input.py              # Raw mode keyboard input
    ├── browser.py            # Directory browser UI
    └── player_view.py        # Player UI (track list + progress bar)
```

### backend/
| File | Responsibility |
| --- | --- |
| `audio.py` | Hardware abstraction: `VLCBackend` and `FFPlayBackend`. Automatically detects which one to use via `make_backend()`. |
| `player.py` | Domain logic: folder scanning, playback, pause, seek, volume, and Discord RPC. No terminal imports. |

### frontend/
| File | Responsibility |
| --- | --- |
| `colors.py` | ANSI constants and formatting utilities (`fmt_time`, `hline`). |
| `input.py` | Isolated keyboard capture (`read_key`). |
| `browser.py` | Interactive file browser view. |
| `player_view.py` | Player screen rendering. |

---

## Controls

### Browser
| Key | Action |
| --- | --- |
| `↑` / `↓` or `k` / `j` | Move cursor |
| `Enter` / `→` / `l` | Open folder or select directory |
| `Backspace` / `←` / `h` | Go to parent folder |
| `o` | Go to home folder ($HOME) |
| `q` | Cancel / Quit |

### Player
| Key | Action |
| --- | --- |
| `Space` | Pause / Resume |
| `Enter` | Play selected song |
| `n` / `p` | Next / Previous track |
| `←` / `→` or `h` / `l` | Seek backward / forward 5 seconds |
| `+` / `-` | Increase / Decrease volume |
| `o` | Open file browser |
| `q` | Quit the program |
