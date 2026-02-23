
import os
from backend.player import SONG_EXTS
from frontend.colors import (W, CLEAR, HIDE, SHOW, RESET, BOLD, DIM,
                              CYAN, GREEN, BG_SEL, BG_DARK, hline)
from frontend.input import read_key


def _entries(path):
    try:
        ls = os.listdir(path)
    except PermissionError:
        return [], []
    d = sorted((x for x in ls if os.path.isdir(os.path.join(path, x))), key=str.lower)
    s = sorted((x for x in ls if x.lower().endswith(SONG_EXTS)), key=str.lower)
    return d, s


def _song_count(path):
    try:
        return sum(1 for f in os.listdir(path) if f.lower().endswith(SONG_EXTS))
    except OSError:
        return 0


def _draw(path, dirs, songs, cur, scr):
    cols, rows = os.get_terminal_size()
    max_vis = max(1, rows - 7)
    total   = len(dirs) + len(songs)
    hint    = f'{GREEN}♪ {len(songs)} tracks{RESET}' if songs else f'{DIM}no tracks{RESET}'

    out = [CLEAR, HIDE,
           BG_DARK, CYAN, BOLD, ' PY-MUS  ·  Browser'.center(cols), RESET, '\n',
           CYAN, BOLD, f' {path}', RESET, '\n',
           ' ', hint, '\n',
           DIM, hline(cols), RESET, '\n']

    end = min(total, scr + max_vis)
    for i in range(scr, end):
        sel = (i == cur)
        if i < len(dirs):
            nm  = dirs[i]
            sc  = _song_count(os.path.join(path, nm))
            sc_s = f' {GREEN}♪{sc}{RESET}' if sc else ''
            if sel: out += [BG_SEL, CYAN, BOLD, f' → 📁 {nm}', RESET, sc_s, '\n']
            else:   out += [f'   {CYAN}📁{RESET} {nm}', sc_s, '\n']
        else:
            nm = songs[i - len(dirs)]
            if sel: out += [BG_SEL, GREEN, BOLD, f' → ♪  {nm}', RESET, '\n']
            else:   out += [DIM, f'   ♪  {nm}', RESET, '\n']

    if total == 0:
        out += [DIM, '   (empty)', RESET, '\n']
    if total > max_vis:
        out += [DIM, f'   {scr+1}-{end} of {total}', RESET, '\n']

    out += [DIM, hline(cols), RESET, '\n',
            CYAN, '↑↓', RESET, ' move  ',
            CYAN, '→/l/Enter', RESET, ' open/select  ',
            CYAN, '←/h/Bksp', RESET, ' up  ',
            CYAN, 'o', RESET, ' home  ',
            CYAN, 'q', RESET, ' cancel']
    W(*out)


def browse(fd, start=None) -> str | None:

    cur_path = os.path.realpath(start or os.path.expanduser('~'))
    cursor = scroll = 0

    dirs, songs = _entries(cur_path)
    _draw(cur_path, dirs, songs, cursor, scroll)

    while True:
        _, rows  = os.get_terminal_size()
        max_vis  = max(1, rows - 7)
        total    = len(dirs) + len(songs)
        key      = read_key(fd, timeout=None)
        if key is None:
            continue
        redraw = True

        if key in ('\x1b[A', 'k'):
            if total: cursor = (cursor - 1) % total

        elif key in ('\x1b[B', 'j'):
            if total: cursor = (cursor + 1) % total

        elif key in ('\x1b[C', '\r', 'l', 'L'):
            if total == 0:
                redraw = False
            elif cursor < len(dirs):
                cur_path = os.path.realpath(os.path.join(cur_path, dirs[cursor]))
                dirs, songs = _entries(cur_path)
                cursor = scroll = 0
                if not dirs and songs:
                    W(CLEAR, SHOW)
                    return cur_path
            else:
                W(CLEAR, SHOW)
                return cur_path

        elif key in ('\x1b[D', '\x7f', 'h', 'H'):
            parent = os.path.dirname(cur_path)
            if parent != cur_path:
                prev     = os.path.basename(cur_path)
                cur_path = parent
                dirs, songs = _entries(cur_path)
                cursor = dirs.index(prev) if prev in dirs else 0
                scroll = 0

        elif key in ('o', 'O'):
            cur_path    = os.path.expanduser('~')
            dirs, songs = _entries(cur_path)
            cursor = scroll = 0

        elif key in ('q', 'Q', '\x03'):
            W(CLEAR, SHOW)
            return None

        else:
            redraw = False

        if redraw:
            total = len(dirs) + len(songs)
            if cursor < scroll:
                scroll = cursor
            elif cursor >= scroll + max_vis:
                scroll = cursor - max_vis + 1
            _draw(cur_path, dirs, songs, cursor, scroll)