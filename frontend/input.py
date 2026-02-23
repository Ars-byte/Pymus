
import os, sys, select, termios, tty


def read_key(fd, timeout=None):

    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if not r:
            return None
        ch = os.read(fd, 1).decode('latin-1')
        if ch == '\x1b':
            seq = ch
            for _ in range(5):
                r2, _, _ = select.select([sys.stdin], [], [], 0.1)
                if not r2:
                    break
                b = os.read(fd, 1).decode('latin-1')
                seq += b
                if b.isalpha() or b == '~':
                    break
            return seq
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)