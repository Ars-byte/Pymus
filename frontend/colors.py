import sys

CLEAR   = '\033[H\033[2J'
HIDE    = '\033[?25l'
SHOW    = '\033[?25h'
RESET   = '\033[0m'
BOLD    = '\033[1m'
DIM     = '\033[2m'

CYAN    = '\033[38;2;200;200;190m'
GREEN   = '\033[38;2;255;255;255m'
YELLOW  = '\033[38;2;230;225;210m'
MAGENTA = '\033[38;2;180;175;165m'
WHITE   = '\033[38;2;220;220;210m'

BG_SEL  = '\033[48;2;60;60;55m\033[38;2;255;255;250m'
BG_DARK = '\033[48;2;240;240;230m\033[38;2;40;40;40m'

def W(*a):
    sys.stdout.write(''.join(a))
    sys.stdout.flush()


def hline(n: int) -> str:
    return '─' * n


def fmt_time(s: float) -> str:
    s = max(0, int(s))
    return f'{s // 60}:{s % 60:02d}'
