#!/bin/bash

echo "[*] Starting initial setup..."

# Step 1: Install required packages
echo "[*] Installing packages from packages.txt..."
sudo apt update
xargs -a packages.txt sudo apt install -y

# Step 2: Setup VLAN-capable macvlan interface
echo "[*] Configuring macvlan for OpenWRT..."
ip link add macvlan0 link eth0 type macvlan mode bridge
ip addr add 192.168.100.2/24 dev macvlan0
ip link set macvlan0 up

# Step 3: Start Docker stack
echo "[*] Starting Docker stack..."
docker-compose up -d

echo "[*] Setup complete."
