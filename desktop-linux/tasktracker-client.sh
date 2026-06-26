#!/bin/bash
# Wrapper script to execute the TaskTracker Client from system shortcut
APP_DIR="/home/bgarcia/p/tasktracker_server/desktop-linux"
exec "${APP_DIR}/.venv/bin/python" "${APP_DIR}/run.py" "$@"
