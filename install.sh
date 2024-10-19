#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root."
    exit 1
fi

# Define paths
SCRIPT_PATH="/usr/local/bin/apply_wg_routes.py"
SERVICE_PATH="/etc/systemd/system/apply_wg_routes.service"

# Copy the Python script to /usr/local/bin
echo "Installing apply_wg_routes.py to /usr/local/bin..."
cp apply_wg_routes.py $SCRIPT_PATH
chmod +x $SCRIPT_PATH

# Copy the systemd service file to /etc/systemd/system
echo "Installing apply_wg_routes.service to /etc/systemd/system..."
cp apply_wg_routes.service $SERVICE_PATH

# Reload systemd daemon to recognize the new service
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the systemd service so it runs after WireGuard starts
echo "Enabling apply_wg_routes.service..."
systemctl enable apply_wg_routes.service

# Optionally start the service immediately
echo "Starting apply_wg_routes.service..."
systemctl start apply_wg_routes.service

echo "Installation complete. The WireGuard route and iptables rules will be applied automatically."
