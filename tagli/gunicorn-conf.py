import os

def numCPUs():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

bind = "0.0.0.0:8000"
workers = numCPUs() * 2 + 1
pidfile = '/var/log/tagli.pid'
proc_name = 'gunicorn/tagli'
daemon = True
debug = True
logfile="/var/log/tagli.log"
accesslog="/var/log/tagli.log"
errorlog="/var/log/tagli.err"
loglevel = "debug"