import os, time
from backend.audio import make_backend

SONG_EXTS = ('.mp3', '.wav', '.ogg', '.flac', '.opus')
CLIENT_ID  = '1468317452969709570'


def get_duration(filepath):
    try:
        from mutagen import File as MFile
        f = MFile(filepath)
        if f is not None and f.info is not None and f.info.length:
            return float(f.info.length)
    except Exception:
        pass
    return 0.0


class Player:

    __slots__ = ('playing_now', '_paused_flag', 'volume', 'row', 'path',
                 'songs', 'rpc', 'rpc_ok', 'song_duration',
                 'backend', '_backend_name')

    def __init__(self):
        self.playing_now   = None
        self._paused_flag  = False
        self.volume        = 0.5
        self.row           = 0
        self.path          = ''
        self.songs         = []
        self.rpc_ok        = False
        self.rpc           = None
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

    def elapsed(self):
        if not self.playing_now:
            return 0.0
        return self.backend.get_pos()

    def play_current(self):
        if not self.songs:
            return
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

    def toggle_pause(self):
        if not self.playing_now:
            return
        if self._paused_flag:
            if hasattr(self.backend, 'resume'):
                self.backend.resume()
            else:
                self.backend.pause()
            self._paused_flag = False
        else:
            self.backend.pause()
            self._paused_flag = True

    def seek(self, delta):
        if not self.playing_now or self.song_duration <= 0:
            return
        pos = max(0.0, min(self.elapsed() + delta, self.song_duration - 0.5))
        try:
            self.backend.set_pos(pos)
        except Exception:
            pass

    def change_volume(self, delta):
        self.volume = max(0.0, min(1.0, self.volume + delta))
        self.backend.set_volume(self.volume)

    def next_song(self):
        self.row = (self.row + 1) % len(self.songs)
        self.play_current()

    def prev_song(self):
        self.row = (self.row - 1) % len(self.songs)
        self.play_current()

    def stop(self):
        self.backend.stop()

    def is_ended(self):
        return self.backend.is_ended()


    def scan(self, path):
        p = os.path.expanduser(path)
        if not os.path.isdir(p):
            return []
        try:
            return sorted(f for f in os.listdir(p) if f.lower().endswith(SONG_EXTS))
        except OSError:
            return []

    def load_directory(self, path):
        self.path  = path
        self.songs = self.scan(path)
        self.row   = 0