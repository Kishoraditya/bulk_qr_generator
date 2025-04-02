# Gunicorn configuration file
import multiprocessing
import os
# Bind to 0.0.0.0:$PORT
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")

# Worker Options
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging Options
loglevel = 'info'
accesslog = '-'
errorlog = '-'
