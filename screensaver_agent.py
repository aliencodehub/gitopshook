#!/usr/bin/env python3
"""
Screensaver Agent
=================
Monitors terminal idle time and launches a bouncing smiley-face screensaver
after IDLE_TIMEOUT seconds (default: 60 seconds / 1 minute) of inactivity.

Usage:
    python3 screensaver_agent.py [idle_seconds]

    idle_seconds  Optional override for the idle timeout (default: 60).

Controls:
    - Any key press resets the idle timer while the agent is watching.
    - Any key press during the screensaver returns to the agent.
    - Ctrl+C exits the agent entirely.
"""

import curses
import select
import sys
import termios
import time
import tty

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_IDLE_TIMEOUT = 60  # seconds before screensaver activates
FRAME_DELAY = 0.05          # seconds between screensaver frames (~20 fps)

SMILEY_FRAMES = [
    r" ___  ",
    r"(o o) ",
    r" \-/  ",
]

# ---------------------------------------------------------------------------
# Screensaver
# ---------------------------------------------------------------------------


def _draw_smiley(win, row: int, col: int) -> None:
    """Render the smiley sprite at (row, col), clipping to window bounds."""
    height, width = win.getmaxyx()
    for i, line in enumerate(SMILEY_FRAMES):
        r = row + i
        if 0 <= r < height:
            for j, ch in enumerate(line):
                c = col + j
                if 0 <= c < width - 1:
                    try:
                        win.addch(r, c, ch)
                    except curses.error:
                        pass


def run_screensaver(stdscr) -> None:
    """
    Bouncing smiley screensaver.  Runs until the user presses any key.
    """
    curses.curs_set(0)     # hide cursor
    stdscr.nodelay(True)   # non-blocking getch
    stdscr.clear()

    sprite_h = len(SMILEY_FRAMES)
    sprite_w = max(len(line) for line in SMILEY_FRAMES)

    height, width = stdscr.getmaxyx()

    # Start near the centre
    x = max(0, width // 2 - sprite_w // 2)
    y = max(0, height // 2 - sprite_h // 2)

    # Diagonal direction
    dx = 1
    dy = 1

    while True:
        # Exit screensaver on any key press
        key = stdscr.getch()
        if key != -1:
            break

        # Recalculate bounds in case terminal was resized
        height, width = stdscr.getmaxyx()
        max_x = max(0, width - sprite_w - 1)
        max_y = max(0, height - sprite_h)

        stdscr.erase()
        _draw_smiley(stdscr, y, x)
        stdscr.refresh()

        # Update position
        x += dx
        y += dy

        # Bounce off edges
        if x <= 0:
            x = 0
            dx = 1
        elif x >= max_x:
            x = max_x
            dx = -1

        if y <= 0:
            y = 0
            dy = 1
        elif y >= max_y:
            y = max_y
            dy = -1

        time.sleep(FRAME_DELAY)


# ---------------------------------------------------------------------------
# Idle-monitoring agent
# ---------------------------------------------------------------------------


def monitor(idle_timeout: int) -> None:
    """
    Main agent loop.

    Reads stdin in non-blocking mode.  Any activity resets the idle timer.
    When the timer expires the screensaver is shown; returning from the
    screensaver resets the timer.
    """
    print(f"Screensaver agent running.  Idle timeout: {idle_timeout}s.")
    print("Type anything to reset the idle timer.  Press Ctrl+C to quit.")

    last_activity = time.monotonic()

    # Put the terminal into cbreak mode so we can read individual key-presses
    # without waiting for Enter, and without echoing them.
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setcbreak(sys.stdin.fileno())

        while True:
            # Check for input without blocking (100 ms poll interval)
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                sys.stdin.read(1)
                last_activity = time.monotonic()

            idle = time.monotonic() - last_activity
            remaining = idle_timeout - idle

            if remaining > 0:
                # Show a live countdown so the user knows the agent is active
                print(
                    f"\r  Idle: {idle:5.1f}s  |  Screensaver in: {remaining:5.1f}s  ",
                    end="",
                    flush=True,
                )
            else:
                # Idle threshold reached – launch screensaver
                print("\r  Launching screensaver…                               ")
                curses.wrapper(run_screensaver)
                # After the screensaver exits, reset the timer
                last_activity = time.monotonic()
                print("  Screensaver dismissed.  Watching for idle time again.")

    except KeyboardInterrupt:
        print("\nScreensaver agent stopped.")
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) > 1:
        try:
            idle_timeout = int(sys.argv[1])
            if idle_timeout <= 0:
                raise ValueError
        except ValueError:
            print(f"Error: idle_seconds must be a positive integer.", file=sys.stderr)
            sys.exit(1)
    else:
        idle_timeout = DEFAULT_IDLE_TIMEOUT

    monitor(idle_timeout)


if __name__ == "__main__":
    main()
