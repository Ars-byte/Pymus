#!/usr/bin/env python3
import os, sys, time, select, termios, tty
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

CLEAR   = '\033[H\033[2J'
HIDE    = '\033[?25l'
SHOW    = '\033[?25h'
RESET   = '\033[0m'
BOLD    = '\033[1m'
DIM     = '\033[2m'
CYAN    = '\033[96m'
GREEN   = '\033[92m'
YELLOW  = '\033[93m'
MAGENTA = '\033[95m'
WHITE   = '\033[97m'
BG_SEL  = '\033[48;2;45;45;45m'
BG_DARK = '\033[48;2;20;20;20m'

SONG_EXTS = ('.mp3', '.wav', '.ogg', '.flac', '.opus')
CLIENT_ID  = '1468317452969709570'

def W(*a): sys.stdout.write(''.join(a)); sys.stdout.flush()
def hline(n): return '─' * n
def fmt_time(s): s = max(0, int(s)); return f'{s // 60}:{s % 60:02d}'


def read_key(fd, timeout=None):
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if not r: return None
        ch = os.read(fd, 1).decode('latin-1')
        if ch == '\x1b':
            seq = ch
            for _ in range(5):
                r2, _, _ = select.select([sys.stdin], [], [], 0.1)
                if not r2: break
                b = os.read(fd, 1).decode('latin-1')
                seq += b
                if b.isalpha() or b == '~': break
            return seq
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def get_duration(filepath):
    # mutagen reads only the audio header, avoiding loading the full file
    try:
        from mutagen import File as MFile
        f = MFile(filepath)
        if f is not None and f.info.length:
            return f.info.length
    except Exception:
        pass
    try:
        snd = pygame.mixer.Sound(filepath)
        d = snd.get_length()
        del snd
        return d if d > 0 else 0.0
    except Exception:
        return 0.0


class CyMus:
    __slots__ = ('playing_now', 'is_paused', 'volume', 'row', 'path', 'songs',
                 'rpc', 'rpc_ok', 'fd',
                 'song_duration', 'song_start', 'pause_start', 'paused_accum')

    def __init__(self):
        self.playing_now  = None
        self.is_paused    = False
        self.volume       = 0.5
        self.row          = 0
        self.path         = ''
        self.songs        = []
        self.fd           = sys.stdin.fileno()
        self.rpc_ok       = False
        self.rpc          = None
        self.song_duration  = 0.0
        self.song_start     = 0.0
        self.pause_start    = 0.0
        self.paused_accum   = 0.0
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        try:
            from pypresence import Presence
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.rpc_ok = True
        except Exception:
            pass

    def _elapsed(self):
        if not self.playing_now: return 0.0
        if self.is_paused:
            return self.pause_start - self.song_start - self.paused_accum
        return time.monotonic() - self.song_start - self.paused_accum

    def _seek(self, delta):
        if not self.playing_now or self.song_duration <= 0: return
        pos = max(0.0, min(self._elapsed() + delta, self.song_duration - 0.5))
        try:
            pygame.mixer.music.set_pos(pos)
            self.song_start   = time.monotonic() - pos
            self.paused_accum = 0.0
        except Exception:
            pass

    def _scan(self, path):
        p = os.path.expanduser(path)
        if not os.path.isdir(p): return []
        try:
            return sorted(f for f in os.listdir(p) if f.lower().endswith(SONG_EXTS))
        except OSError:
            return []

    def _play(self):
        if not self.songs: return
        self.playing_now  = self.songs[self.row]
        fp = os.path.join(os.path.expanduser(self.path), self.playing_now)
        pygame.mixer.music.load(fp)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()
        self.is_paused    = False
        self.song_start   = time.monotonic()
        self.paused_accum = 0.0
        self.song_duration = get_duration(fp)
        if self.rpc_ok:
            try:
                self.rpc.update(details=self.playing_now[:50],
                                start=int(time.time()), large_image='icon')
            except Exception:
                self.rpc_ok = False

    def _prog_bar(self, cols):
        elapsed  = self._elapsed()
        duration = self.song_duration
        bar_w    = max(4, cols - 20)
        if duration > 0:
            filled = int(min(1.0, elapsed / duration) * bar_w)
            bar    = f'{GREEN}{"━" * filled}{CYAN}●{DIM}{"─" * (bar_w - filled)}{RESET}'
            return f' {CYAN}{fmt_time(elapsed)}{RESET} {bar} {CYAN}{fmt_time(duration)}{RESET}'
        spin = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
        return f' {CYAN}{fmt_time(elapsed)}{RESET} {DIM}{"─" * bar_w}{RESET} {YELLOW}{spin[int(elapsed) % len(spin)]}{RESET}'

    def browse(self, start=None):
        cur_path = os.path.realpath(start or os.path.expanduser('~'))
        cursor = scroll = 0

        def entries(path):
            try: ls = os.listdir(path)
            except PermissionError: return [], []
            d = sorted((x for x in ls if os.path.isdir(os.path.join(path, x))), key=str.lower)
            s = sorted((x for x in ls if x.lower().endswith(SONG_EXTS)), key=str.lower)
            return d, s

        def song_count(path):
            try: return sum(1 for f in os.listdir(path) if f.lower().endswith(SONG_EXTS))
            except OSError: return 0

        def draw(path, dirs, songs, cur, scr):
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
                    nm = dirs[i]; sc = song_count(os.path.join(path, nm))
                    sc_s = f' {GREEN}♪{sc}{RESET}' if sc else ''
                    if sel: out += [BG_SEL, CYAN, BOLD, f' → 📁 {nm}', RESET, sc_s, '\n']
                    else:   out += [f'   {CYAN}📁{RESET} {nm}', sc_s, '\n']
                else:
                    nm = songs[i - len(dirs)]
                    if sel: out += [BG_SEL, GREEN, BOLD, f' → ♪  {nm}', RESET, '\n']
                    else:   out += [DIM, f'   ♪  {nm}', RESET, '\n']
            if total == 0: out += [DIM, '   (empty)', RESET, '\n']
            if total > max_vis: out += [DIM, f'   {scr+1}-{end} of {total}', RESET, '\n']
            out += [DIM, hline(cols), RESET, '\n',
                    CYAN, '↑↓', RESET, ' move  ',
                    CYAN, '→/l/Enter', RESET, ' open/select  ',
                    CYAN, '←/h/Bksp', RESET, ' up  ',
                    CYAN, 'o', RESET, ' home  ',
                    CYAN, 'q', RESET, ' cancel']
            W(*out)

        dirs, songs = entries(cur_path)
        draw(cur_path, dirs, songs, cursor, scroll)

        while True:
            _, rows = os.get_terminal_size()
            max_vis = max(1, rows - 7)
            total   = len(dirs) + len(songs)
            key     = read_key(self.fd, timeout=None)
            if key is None: continue
            redraw = True

            if key in ('\x1b[A', 'k'):
                if total: cursor = (cursor - 1) % total
            elif key in ('\x1b[B', 'j'):
                if total: cursor = (cursor + 1) % total
            elif key in ('\x1b[C', '\r', 'l', 'L'):
                if total == 0: redraw = False
                elif cursor < len(dirs):
                    cur_path = os.path.realpath(os.path.join(cur_path, dirs[cursor]))
                    dirs, songs = entries(cur_path); cursor = scroll = 0
                    if not dirs and songs:
                        W(CLEAR, SHOW); return cur_path
                else:
                    W(CLEAR, SHOW); return cur_path
            elif key in ('\x1b[D', '\x7f', 'h', 'H'):
                parent = os.path.dirname(cur_path)
                if parent != cur_path:
                    prev = os.path.basename(cur_path); cur_path = parent
                    dirs, songs = entries(cur_path)
                    cursor = dirs.index(prev) if prev in dirs else 0; scroll = 0
            elif key in ('o', 'O'):
                cur_path = os.path.expanduser('~'); dirs, songs = entries(cur_path); cursor = scroll = 0
            elif key in ('q', 'Q', '\x03'):
                W(CLEAR, SHOW); return None
            else: redraw = False

            if redraw:
                total = len(dirs) + len(songs)
                if cursor < scroll: scroll = cursor
                elif cursor >= scroll + max_vis: scroll = cursor - max_vis + 1
                draw(cur_path, dirs, songs, cursor, scroll)

    def _draw_player(self):
        cols, rows = os.get_terminal_size()
        max_vis = max(1, rows - 7)
        total   = len(self.songs)
        start   = max(0, self.row - max_vis // 2)
        end     = min(total, start + max_vis)
        if end == total: start = max(0, total - max_vis)

        out = [CLEAR, HIDE,
               BG_DARK, MAGENTA, BOLD, ' PY-MUS'.center(cols), RESET, '\n',
               DIM, hline(cols), RESET, '\n']

        for i in range(start, end):
            song = self.songs[i]
            if i == self.row:          out += [BG_SEL, CYAN, BOLD, f' → {song}', RESET, '\n']
            elif song == self.playing_now: out += [GREEN, BOLD, f' ▶ {song}', RESET, '\n']
            else:                      out += [DIM, f'   {song}', RESET, '\n']

        st    = f'{YELLOW}⏸{RESET}' if self.is_paused else f'{GREEN}▶{RESET}'
        v_n   = int(self.volume * 10)
        v_bar = f'{GREEN}{"█" * v_n}{DIM}{"░" * (10 - v_n)}{RESET}'
        now   = self.playing_now or 'Stopped'

        out += [DIM, hline(cols), RESET, '\n',
                self._prog_bar(cols), '\n',
                f' {st} {WHITE}{now[:cols - 22]}{RESET}  {v_bar}  {DIM}{self.row+1}/{total}{RESET}\n',
                DIM, '↑↓ nav  Enter play  n/p skip  Space pause  ←/h  →/l seek±5s  +/- vol  o browser  q quit', RESET]
        W(*out)

    def run(self):
        W(CLEAR)
        selected = self.browse()
        if selected is None: W(SHOW); return
        self.path  = selected
        self.songs = self._scan(self.path)
        self._draw_player()

        while True:
            if not self.songs:
                W(CLEAR, SHOW)
                selected = self.browse()
                if selected:
                    self.path = selected; self.songs = self._scan(self.path); self.row = 0
                else: break
                self._draw_player(); continue

            if self.playing_now and not self.is_paused and not pygame.mixer.music.get_busy():
                self.row = (self.row + 1) % len(self.songs)
                self._play(); self._draw_player()

            key = read_key(self.fd, timeout=0.25)

            if key is None:
                if self.playing_now and not self.is_paused: self._draw_player()
                continue

            redraw = True
            if key in ('\x1b[A', 'k'):     self.row = (self.row - 1) % len(self.songs)
            elif key in ('\x1b[B', 'j'):   self.row = (self.row + 1) % len(self.songs)
            elif key == '\r':              self._play()
            elif key.lower() == 'n':       self.row = (self.row + 1) % len(self.songs); self._play()
            elif key.lower() == 'p':       self.row = (self.row - 1) % len(self.songs); self._play()
            elif key == ' ':
                if self.playing_now:
                    if self.is_paused:
                        pygame.mixer.music.unpause()
                        self.paused_accum += time.monotonic() - self.pause_start
                    else:
                        pygame.mixer.music.pause()
                        self.pause_start = time.monotonic()
                    self.is_paused = not self.is_paused
            elif key in ('\x1b[D', 'h'):    self._seek(-5)
            elif key in ('\x1b[C', 'l'):    self._seek(+5)
            elif key.lower() == 'o':
                W(CLEAR, SHOW)
                sel = self.browse()
                if sel: self.path = sel; self.songs = self._scan(self.path); self.row = 0
            elif key in ('+', '='):        self.volume = min(1.0, self.volume + 0.05); pygame.mixer.music.set_volume(self.volume)
            elif key in ('-', '_'):        self.volume = max(0.0, self.volume - 0.05); pygame.mixer.music.set_volume(self.volume)
            elif key.lower() == 'q':       break
            else:                          redraw = False

            if redraw: self._draw_player()

        W(CLEAR, SHOW)


if __name__ == '__main__':
    try:
        CyMus().run()
    except KeyboardInterrupt:
        W(CLEAR, SHOW)
