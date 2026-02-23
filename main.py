import sys

from backend.player import Player
from frontend.colors import W, CLEAR, SHOW
from frontend.input import read_key
from frontend.browser import browse
from frontend.player_view import draw_player


def run():
    player = Player()
    fd     = sys.stdin.fileno()

    W(CLEAR)
    selected = browse(fd)
    if selected is None:
        W(SHOW)
        return

    player.load_directory(selected)
    draw_player(player)

    while True:
        if not player.songs:
            W(CLEAR, SHOW)
            selected = browse(fd)
            if selected:
                player.load_directory(selected)
            else:
                break
            draw_player(player)
            continue

        if player.playing_now and not player.is_paused and player.is_ended():
            player.next_song()
            draw_player(player)

        key = read_key(fd, timeout=0.25)

        if key is None:
            if player.playing_now and not player.is_paused:
                draw_player(player)
            continue

        redraw = True

        if   key in ('\x1b[A', 'k'):   player.row = (player.row - 1) % len(player.songs)
        elif key in ('\x1b[B', 'j'):   player.row = (player.row + 1) % len(player.songs)
        elif key == '\r':              player.play_current()
        elif key.lower() == 'n':       player.next_song()
        elif key.lower() == 'p':       player.prev_song()
        elif key == ' ':               player.toggle_pause()
        elif key in ('\x1b[D', 'h'):   player.seek(-5)
        elif key in ('\x1b[C', 'l'):   player.seek(+5)
        elif key in ('+', '='):        player.change_volume(+0.05)
        elif key in ('-', '_'):        player.change_volume(-0.05)
        elif key.lower() == 'o':
            W(CLEAR, SHOW)
            sel = browse(fd)
            if sel:
                player.load_directory(sel)
        elif key.lower() == 'q':
            break
        else:
            redraw = False

        if redraw:
            draw_player(player)

    player.stop()
    W(CLEAR, SHOW)


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        W(CLEAR, SHOW)