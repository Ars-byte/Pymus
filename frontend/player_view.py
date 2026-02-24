import os
from frontend.colors import (W, CLEAR, HIDE, RESET, BOLD, DIM,
                              CYAN, GREEN, YELLOW, MAGENTA, WHITE,
                              BG_SEL, hline, fmt_time)


def _prog_bar(player, cols: int) -> str:
    elapsed  = player.elapsed()
    duration = player.song_duration
    bar_w    = max(4, cols - 20)

    if duration > 0:
        filled = int(min(1.0, elapsed / duration) * bar_w)
        bar = (f'{GREEN}{"━" * filled}{CYAN}●'
               f'{DIM}{"─" * (bar_w - filled)}{RESET}')
        return f' {CYAN}{fmt_time(elapsed)}{RESET} {bar} {CYAN}{fmt_time(duration)}{RESET}'

    spin = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    return (f' {CYAN}{fmt_time(elapsed)}{RESET} '
            f'{DIM}{"─" * bar_w}{RESET} '
            f'{YELLOW}{spin[int(elapsed) % len(spin)]}{RESET}')


def draw_player(player) -> None:
    cols, rows = os.get_terminal_size()
    max_vis = max(1, rows - 7)
    total   = len(player.songs)
    start   = max(0, player.row - max_vis // 2)
    end     = min(total, start + max_vis)
    if end == total:
        start = max(0, total - max_vis)

    out = [CLEAR, HIDE,
           MAGENTA, BOLD, 'PY-MUS'.center(cols), RESET, '\n',
           DIM, hline(cols), RESET, '\n']

    for i in range(start, end):
        song = player.songs[i]
        if i == player.row:
            out += [BG_SEL, CYAN, BOLD, f' → {song}', RESET, '\n']
        elif song == player.playing_now:
            out += [GREEN, BOLD, f' ▶ {song}', RESET, '\n']
        else:
            out += [DIM, f'   {song}', RESET, '\n']

    st    = f'{YELLOW}⏸{RESET}' if player.is_paused else f'{GREEN}▶{RESET}'
    v_n   = int(player.volume * 10)
    v_bar = f'{GREEN}{"█" * v_n}{DIM}{"░" * (10 - v_n)}{RESET}'
    now   = player.playing_now or 'Stopped'

    shuf_label = f'{GREEN}SHUFFLE{RESET}' if player.shuffle else f'{DIM}shuffle{RESET}'
    loop_label = f'{GREEN}LOOP{RESET}'    if player.loop    else f'{DIM}loop{RESET}'

    out += [DIM, hline(cols), RESET, '\n',
            _prog_bar(player, cols), '\n',
            f' {st} {WHITE}{now[:cols - 22]}{RESET}  {v_bar}  '
            f'{DIM}{player.row + 1}/{total}{RESET}\n',
            DIM,
            '↑↓ nav  Enter play  n/p skip  Space pause  '
            '←/h  →/l seek±5s  +/- vol  o browser  q quit  ',
            RESET,
            's:', shuf_label, '  r:', loop_label]
    W(*out)
