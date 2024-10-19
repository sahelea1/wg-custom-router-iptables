#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root."
    exit 1
fi

# Define paths
SCRIPT_PATH="/usr/local/bin/apply_wg_routes.py"
SERVICE_PATH="/etc/systemd/system/apply_wg_routes.service"

# Stop the service if it's running
echo "Stopping apply_wg_routes.service if running..."
systemctl stop apply_wg_routes.service

# Disable the systemd service
echo "Disabling apply_wg_routes.service..."
systemctl disable apply_wg_routes.service

# Remove the systemd service file
if [ -f "$SERVICE_PATH" ]; then
    echo "Removing $SERVICE_PATH..."
    rm "$SERVICE_PATH"
else
    echo "$SERVICE_PATH does not exist."
fi

# Remove the Python script
if [ -f "$SCRIPT_PATH" ]; then
    echo "Removing $SCRIPT_PATH..."
    rm "$SCRIPT_PATH"
else
    echo "$SCRIPT_PATH does not exist."
fi

# Reload systemd daemon to reflect the removal of the service
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Optionally flush iptables rules and routes created by the service (safe only if you're sure no other rules are using these)
read -p "Do you want to flush iptables rules and routes created by the service? [y/N]: " flush
if [[ "$flush" == "y" || "$flush" == "Y" ]]; then
    echo "Flushing iptables rules and routes..."

    # Flush mangle and nat table rules created by the script
    iptables -t mangle -F
    iptables -t nat -F

    # Flush routing table 100
    ip route flush table 100

    # Flush fwmark rules
    ip rule flush
else
    echo "Skipping iptables and route flush."
fi

echo "Uninstallation complete."
