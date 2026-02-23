
import sys

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


def W(*a):
    sys.stdout.write(''.join(a))
    sys.stdout.flush()


def hline(n: int) -> str:
    return '─' * n


def fmt_time(s: float) -> str:
    s = max(0, int(s))
    return f'{s // 60}:{s % 60:02d}'
