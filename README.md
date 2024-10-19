# WireGuard Custom Routing with Automated iptables Setup

This repository provides a way to automatically configure custom routing and iptables rules for specific peers in your WireGuard configuration. The setup allows you to define routing and masquerading rules directly in your WireGuard configuration files, which will be applied dynamically whenever WireGuard is started.

## Features
- **Custom Routing per Peer**: Specify next-hop routes and interfaces for individual peers.
- **Automatic iptables Setup**: iptables rules for marking and masquerading traffic are automatically configured based on the WireGuard config.
- **Systemd Integration**: The routes and iptables rules are applied automatically when WireGuard starts.
- **Config Cleanup**: The script ensures that stale routes and iptables rules are cleaned up if removed from the WireGuard config.

## Installation

To install the script and systemd service on your server, run the following one-liner:

```bash
bash <(curl -s https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME/main/install.sh)
```

This command will:
1. Clone the repository.
2. Run the `install.sh` script to install the Python script and systemd service.

> **Note**: Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY_NAME` with your actual GitHub repository information.

### Manual Installation Steps
Alternatively, you can install the script and service manually:

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
   cd YOUR_REPOSITORY_NAME
   ```

2. Run the install script:
   ```bash
   sudo ./install.sh
   ```

## Adding Custom Routes to WireGuard Config

To specify custom routing for a peer, add the following comment to your WireGuard configuration file under the `[Peer]` section:

```ini
# WireGuard config example (e.g., /etc/wireguard/wg0.conf)

[Interface]
PrivateKey = ...
Address = 10.11.12.1/24
ListenPort = 51820

[Peer]
PublicKey = ...
AllowedIPs = 10.11.12.33/32
#!!172.15.15.3|wg0  # Custom route for this peer, via peer 172.15.15.3 on wg0

[Peer]
PublicKey = ...
AllowedIPs = 10.11.12.34/32
#!!172.15.15.4|wg0  # Custom route for this peer, via peer 172.15.15.4 on wg0

[Peer]
PublicKey = ...
AllowedIPs = 10.11.12.35/32
#!!172.15.15.5|wg1  # Custom route for this peer, via peer 172.15.15.5 on wg1
```

### Format of the Custom Route Comment

```text
#!!<via_peer_ip>|<interface>
```

- **via_peer_ip**: The IP address of the peer that will act as the next hop.
- **interface**: The WireGuard interface that the traffic will be routed through (e.g., `wg0`).

The Python script will read these comments, apply the necessary `iptables` and routing rules, and ensure proper traffic flow through the specified peer.

## Systemd Integration

A systemd service is created that will automatically apply routes and iptables rules every time WireGuard is started. You don't need to manually trigger the route setup after rebooting or restarting WireGuard.

To check the status of the custom route service:

```bash
sudo systemctl status apply_wg_routes.service
```

To start/stop the service manually:

```bash
sudo systemctl start apply_wg_routes.service
sudo systemctl stop apply_wg_routes.service
```

## Uninstallation

To remove the Python script and systemd service, run the following command:

```bash
sudo ./uninstall.sh
```

You will be prompted to decide whether to flush the iptables rules and routes set by the service.

## Example Workflow

### 1. Add a Custom Route to a WireGuard Peer

Edit your WireGuard configuration file (`/etc/wireguard/wg0.conf`) and add the following under a specific peer:

```ini
[Peer]
PublicKey = ...
AllowedIPs = 10.11.12.33/32
#!!172.15.15.3|wg0
```

### 2. Restart WireGuard

After editing the config, restart WireGuard to apply the changes:

```bash
sudo systemctl restart wg-quick@wg0
```

### 3. Verify Routes and iptables

Check the routing and `iptables` rules that were applied:

```bash
ip route show table 100
iptables -t mangle -S
iptables -t nat -S
```

## License

This project is open source and available under the [MIT License](LICENSE).
