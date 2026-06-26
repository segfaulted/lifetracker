#!/bin/bash
# Wrapper script to execute the TaskTracker Client from system shortcut
APP_DIR="$(dirname "$(realpath "$0")")"
exec "${APP_DIR}/.venv/bin/python" "${APP_DIR}/run.py" "$@"
