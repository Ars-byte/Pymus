import os, sys, time, shutil, subprocess
from threading import Thread


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
        self._proc         = None
        self._vol          = 0.5
        self._start        = 0.0
        self._offset       = 0.0
        self._paused       = False
        self._pause_t      = 0.0
        self._paused_accum = 0.0
        self._path         = None
        self._ended        = False

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
        self._proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
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
        if self._paused: return
        if self._proc and self._proc.poll() is None:
            self._offset = self.get_pos()
            self.play()

    def get_volume(self): return self._vol

    def get_pos(self):
        if self._paused:    return self._offset
        if not self._proc:  return self._offset
        return self._offset + (time.monotonic() - self._start)

    def set_pos(self, seconds):
        was_paused   = self._paused
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
        return VLCBackend(), 'vlc'
    except Exception:
        pass
    try:
        return FFPlayBackend(), 'ffplay'
    except Exception:
        pass
    sys.exit('Error: neither python-vlc nor ffplay found.\n'
             'Install one:  pip install python-vlc   OR   apt install ffmpeg')