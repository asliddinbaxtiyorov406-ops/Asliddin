#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/murojat-bot}"
SERVICE_NAME="${SERVICE_NAME:-murojat-bot}"

cd "$APP_DIR"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

sudo cp deploy/murojat-bot.service.example "/etc/systemd/system/${SERVICE_NAME}.service"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager
