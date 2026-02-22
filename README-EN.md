# PY-MUS

**PY-MUS** is a lightweight and minimalist music player that lives entirely in your terminal. Designed for those who prefer the command line, it offers fluid folder navigation, dynamic progress bars, and **Discord Rich Presence** support.

---

## Features

* **TUI Interface:** Visual terminal navigation with ANSI colors and highlighting effects.
* **File Browser:** Explore directories and select music folders in real-time.
* **Total Control:** Pause, skip tracks (`n`/`p`), volume adjustment (`+`/`-`), and time seeking (`h`/`l`).
* **Discord RPC:** Automatically shows which song you are listening to on your Discord profile.
* **Multi-format Support:** Compatible with `.mp3`, `.wav`, `.ogg`, `.flac`, and `.opus`.
* **Efficiency:** Use of `__slots__` to minimize RAM consumption.

---

## Compatibility

This player is designed to be hardware-agnostic and works wherever there is a terminal:

* **TTY:** Works without the need for a graphical environment (X11/Wayland).
* **Steam Deck:** Perfect for "Desktop Mode" or via a terminal in Gaming Mode to save resources while you play.
* **Termux:** Thanks to its text-based interface, it is ideal for Android devices using Termux.
* **Terminals:** Fully compatible with Linux.

## Preview:

In inmutable systems:
<img width="1087" height="679" alt="image" src="https://github.com/user-attachments/assets/e6100d2a-e6b5-4884-abec-e4f74aef80f4" />

In mutable systems:

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e7db1c77-f007-41a7-a046-2442ce150030" />


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

3. **Run the player:**

```bash
python3 pymus.py

```

---

## Controls

### Explorer (Browser)

| Key | Action |
| --- | --- |
| `↑` / `↓` or `k` / `j` | Move cursor |
| `Enter` / `→` / `l` | Open folder or select directory |
| `Backspace` / `←` / `h` | Go back to previous folder |
| `o` | Go to home directory ($HOME) |
| `q` | Cancel / Exit |

### Player

| Key | Action |
| --- | --- |
| `Space` | Pause / Resume |
| `Enter` | Play selected song |
| `n` / `p` | Next / Previous song |
| `←` / `→` or `h` / `l` | Seek backward / forward 5 seconds |
| `+` / `-` | Increase / Decrease volume |
| `o` | Open the file explorer |
| `q` | Exit the program |

---

## Requirements

* **Python 3.7+**
* **Pygame:** Main audio engine.
* **Mutagen (Optional):** For accurate duration metadata reading.
* **Pypresence (Optional):** For Discord integration.

---
