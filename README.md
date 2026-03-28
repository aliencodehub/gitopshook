# Screensaver Agent

A lightweight agent that watches for idle time and launches a **bouncing smiley-face screensaver** in the terminal after **1 minute** of inactivity.

## How it works

The agent polls stdin every 100 ms.  Any key-press resets the idle counter.
Once the counter reaches the configured idle timeout the screensaver takes
over the terminal.  Pressing any key dismisses the screensaver and returns to
the idle-watching loop.  `Ctrl+C` exits the agent entirely.

## Running locally (requires Python 3.6+)

```bash
python3 screensaver_agent.py            # default: 60-second idle timeout
python3 screensaver_agent.py 30         # custom: 30-second idle timeout
```

## Running with Docker

```bash
# Build the image
docker build -t gitopshook .

# Run with the default 60-second timeout (terminal must be allocated with -it)
docker run -it gitopshook

# Run with a custom 30-second timeout
docker run -it gitopshook 30
```

## Screensaver preview

```
 ___
(o o)
 \-/
```

The smiley bounces diagonally around the terminal window until any key is pressed.
