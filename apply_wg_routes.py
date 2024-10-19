
import os
import subprocess
import re
import sys

# Directory where WireGuard config files are located
WG_CONFIG_DIR = '/etc/wireguard'

# Regex pattern to match the custom route comment in WireGuard config files
route_pattern = re.compile(r'#!!([\d\.]+)\|(\w+)')

# Function to run a shell command and handle errors
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e.stderr.decode('utf-8')}")
        return None

# Function to apply routes and iptables rules from WireGuard config files
def apply_routes():
    # Collect existing rules for cleanup later
    applied_peer_ips = set()

    # Process each WireGuard configuration file in /etc/wireguard
    for config_file in os.listdir(WG_CONFIG_DIR):
        if config_file.endswith('.conf'):
            config_path = os.path.join(WG_CONFIG_DIR, config_file)
            print(f"Processing {config_path}...")

            with open(config_path, 'r') as wg_config:
                peer_ip = None
                for line in wg_config:
                    # Check if the line contains an AllowedIPs entry
                    if line.startswith('AllowedIPs'):
                        peer_ip = line.split('=')[1].strip().split('/')[0]  # Extract the peer IP (e.g., 10.11.12.33)

                    # Check if the line contains the custom route comment
                    match = route_pattern.search(line)
                    if match and peer_ip:
                        via_peer_ip = match.group(1)   # Extract next-hop peer IP
                        interface = match.group(2)     # Extract interface
                        applied_peer_ips.add(peer_ip)  # Keep track of the peer for cleanup

                        print(f"Applying route for peer {peer_ip} via {via_peer_ip} on {interface}...")

                        # Mark traffic from this peer
                        mark_command = f"iptables -t mangle -A PREROUTING -s {peer_ip} -j MARK --set-mark 0x1"
                        run_command(mark_command)

                        # Add the route for this peer via the specified next-hop peer
                        routing_command = f"ip route add default via {via_peer_ip} table 100"
                        run_command(routing_command)

                        # Add fwmark rule for the marked traffic
                        fwmark_rule_command = "ip rule add fwmark 0x1 table 100"
                        run_command(fwmark_rule_command)

                        # Apply masquerading for the outgoing traffic on the specified interface
                        nat_command = f"iptables -t nat -A POSTROUTING -m mark --mark 0x1 -o {interface} -j MASQUERADE"
                        run_command(nat_command)

                        # Reset the peer_ip variable after the route is applied
                        peer_ip = None

    return applied_peer_ips

# Function to clean up old routes and iptables rules
def cleanup_routes(applied_peer_ips):
    print("Cleaning up old routes and rules...")

    # Get existing marked rules to find old ones
    existing_rules = run_command("iptables -t mangle -S PREROUTING").splitlines()
    for rule in existing_rules:
        if "-s" in rule:  # Find peer-specific rules
            peer_ip = rule.split("-s ")[1].split(" ")[0]
            if peer_ip not in applied_peer_ips:
                # Remove old iptables rule for this peer
                delete_command = f"iptables -t mangle -D PREROUTING -s {peer_ip} -j MARK --set-mark 0x1"
                run_command(delete_command)

    # Remove old routes and ip rules associated with fwmark if no longer needed
    run_command("ip rule flush")
    run_command("ip route flush table 100")

    # Re-apply the default NAT rule
    run_command("iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")

def main():
    # Ensure script is being run as root
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)

    print("Applying WireGuard routes and iptables rules...")

    # Apply routes and iptables rules based on WireGuard configs
    applied_peer_ips = apply_routes()

    # Clean up old routes and rules
    cleanup_routes(applied_peer_ips)

    print("Route and rule application completed.")

if __name__ == "__main__":
    main()
