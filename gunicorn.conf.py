import os

# Gunicorn configuration file

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', 3))
