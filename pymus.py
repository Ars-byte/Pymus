#!/usr/bin/env python3
import os, sys, time, select, termios, tty, subprocess, shutil
from threading import Thread

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
    try:
        from mutagen import File as MFile
        f = MFile(filepath)
        if f is not None and f.info is not None and f.info.length:
            return float(f.info.length)
    except Exception:
        pass
    return 0.0



class VLCBackend:
    def __init__(self):
        import vlc
        self._vlc  = vlc
        self._inst = vlc.Instance('--no-video', '--quiet')
        self._mp   = self._inst.media_player_new()
        self._vol  = 50

    def load(self, path):
        media = self._inst.media_new(path)
        self._mp.set_media(media)

    def play(self):
        self._mp.play()
        self._mp.audio_set_volume(self._vol)

    def pause(self): self._mp.pause()
    def stop(self):  self._mp.stop()

    def set_volume(self, v01):
        self._vol = int(v01 * 100)
        self._mp.audio_set_volume(self._vol)

    def get_volume(self): return self._vol / 100.0

    def get_pos(self):
        t = self._mp.get_time()
        return t / 1000.0 if t >= 0 else 0.0

    def set_pos(self, seconds):
        self._mp.set_time(int(seconds * 1000))

    def is_playing(self):
        return self._mp.is_playing()

    def is_paused(self):
        state = self._mp.get_state()
        return state == self._vlc.State.Paused

    def is_ended(self):
        state = self._mp.get_state()
        return state in (self._vlc.State.Ended, self._vlc.State.Stopped,
                         self._vlc.State.Error, self._vlc.State.NothingSpecial)


class FFPlayBackend:

    def __init__(self):
        if not shutil.which('ffplay'):
            raise RuntimeError('ffplay not found')
        self._proc    = None
        self._vol     = 0.5
        self._start   = 0.0
        self._offset  = 0.0
        self._paused  = False
        self._pause_t = 0.0
        self._paused_accum = 0.0
        self._path    = None
        self._ended   = False

    def _kill(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try: self._proc.wait(timeout=1)
            except Exception: self._proc.kill()
        self._proc = None

    def load(self, path):
        self._kill()
        self._path   = path
        self._offset = 0.0
        self._ended  = False

    def play(self):
        self._kill()
        vol_ffplay = int(self._vol * 100)
        cmd = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet',
               '-ss', str(self._offset),
               '-volume', str(vol_ffplay),
               self._path]
        self._proc  = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
        self._start        = time.monotonic()
        self._paused       = False
        self._paused_accum = 0.0
        self._ended        = False
        Thread(target=self._watch, daemon=True).start()

    def _watch(self):
        if self._proc: self._proc.wait()
        self._ended = True

    def pause(self):
        if self._paused or not self._proc: return
        self._offset = self.get_pos()
        self._kill()
        self._paused  = True
        self._pause_t = time.monotonic()

    def resume(self):
        if not self._paused: return
        self._paused = False
        self.play()

    def stop(self):
        self._kill()
        self._ended = True

    def set_volume(self, v01):
        self._vol = max(0.0, min(1.0, v01))
        
        if self._paused:
            return
        if self._proc and self._proc.poll() is None:
            self._offset = self.get_pos()
            self.play()
    def get_volume(self): return self._vol

    def get_pos(self):
        if self._paused: return self._offset
        if not self._proc:  return self._offset
        return self._offset + (time.monotonic() - self._start)

    def set_pos(self, seconds):
        was_paused = self._paused
        self._offset = max(0.0, seconds)
        self._kill()
        self._paused = False
        if not was_paused:
            self.play()

    def is_playing(self): return bool(self._proc and self._proc.poll() is None)
    def is_paused(self):  return self._paused
    def is_ended(self):   return self._ended and not self._paused


def make_backend():
    try:
        b = VLCBackend()
        return b, 'vlc'
    except Exception:
        pass
    try:
        b = FFPlayBackend()
        return b, 'ffplay'
    except Exception:
        pass
    sys.exit('Error: neither python-vlc nor ffplay found.\n'
             'Install one:  pip install python-vlc   OR   apt install ffmpeg')



class CyMus:
    __slots__ = ('playing_now', '_paused_flag', 'volume', 'row', 'path', 'songs',
                 'rpc', 'rpc_ok', 'fd', 'song_duration', 'backend', '_backend_name')

    def __init__(self):
        self.playing_now  = None
        self._paused_flag = False
        self.volume       = 0.5
        self.row          = 0
        self.path         = ''
        self.songs        = []
        self.fd           = sys.stdin.fileno()
        self.rpc_ok       = False
        self.rpc          = None
        self.song_duration = 0.0
        self.backend, self._backend_name = make_backend()
        self.backend.set_volume(self.volume)
        try:
            from pypresence import Presence
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.rpc_ok = True
        except Exception:
            pass

    @property
    def is_paused(self):
        return self._paused_flag

    def _elapsed(self):
        if not self.playing_now: return 0.0
        return self.backend.get_pos()

    def _seek(self, delta):
        if not self.playing_now or self.song_duration <= 0: return
        pos = max(0.0, min(self._elapsed() + delta, self.song_duration - 0.5))
        try:
            self.backend.set_pos(pos)
            if self._paused_flag:
                pass
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
        self.playing_now   = self.songs[self.row]
        fp = os.path.join(os.path.expanduser(self.path), self.playing_now)
        self.song_duration = get_duration(fp)
        self.backend.load(fp)
        self.backend.play()
        self._paused_flag  = False
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
               BG_DARK, MAGENTA, BOLD, f'PY-MUS'.center(cols), RESET, '\n',
               DIM, hline(cols), RESET, '\n']

        for i in range(start, end):
            song = self.songs[i]
            if i == self.row:              out += [BG_SEL, CYAN, BOLD, f' → {song}', RESET, '\n']
            elif song == self.playing_now: out += [GREEN, BOLD, f' ▶ {song}', RESET, '\n']
            else:                          out += [DIM, f'   {song}', RESET, '\n']

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

            if self.playing_now and not self.is_paused and self.backend.is_ended():
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
                    if self._paused_flag:
                        if hasattr(self.backend, 'resume'):
                            self.backend.resume()
                        else:
                            self.backend.pause()
                        self._paused_flag = False
                    else:
                        self.backend.pause()
                        self._paused_flag = True
            elif key in ('\x1b[D', 'h'):   self._seek(-5)
            elif key in ('\x1b[C', 'l'):   self._seek(+5)
            elif key.lower() == 'o':
                W(CLEAR, SHOW)
                sel = self.browse()
                if sel: self.path = sel; self.songs = self._scan(self.path); self.row = 0
            elif key in ('+', '='):
                self.volume = min(1.0, self.volume + 0.05)
                self.backend.set_volume(self.volume)
            elif key in ('-', '_'):
                self.volume = max(0.0, self.volume - 0.05)
                self.backend.set_volume(self.volume)
            elif key.lower() == 'q':       break
            else:                          redraw = False

            if redraw: self._draw_player()

        self.backend.stop()
        W(CLEAR, SHOW)


if __name__ == '__main__':
    try:
        CyMus().run()
    except KeyboardInterrupt:
        W(CLEAR, SHOW)
