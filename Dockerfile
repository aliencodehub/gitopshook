# Use a slim Python image so curses and the standard library are available
FROM python:3.12-slim

WORKDIR /app

COPY screensaver_agent.py .

# Run the screensaver agent with the default idle timeout of 60 seconds.
# Override the timeout by passing a different value, e.g.:
#   docker run -it gitopshook 30
ENTRYPOINT ["python3", "screensaver_agent.py"]
