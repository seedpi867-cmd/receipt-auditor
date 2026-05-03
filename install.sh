#!/bin/bash
# Quick install — creates a systemd service so the agent runs on boot
#
# policy_owner: local operator
# log_path: systemd journal for the installed service
# approval_mode: manual sudo execution
# recovery_path: systemctl disable --now SERVICE_NAME; remove service file
# verification_command: systemctl status SERVICE_NAME
set -e

SERVICE_NAME="${1:-brain-agent}"
AGENT_DIR="$(cd "$(dirname "$0")" && pwd)"
USER="$(whoami)"

cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=Brain Loop Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$AGENT_DIR
ExecStart=/bin/bash $AGENT_DIR/brain-loop.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/${SERVICE_NAME}.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo "Installed as $SERVICE_NAME"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    journalctl -u $SERVICE_NAME -f"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
