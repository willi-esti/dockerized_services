#!/bin/bash

# WireGuard Client Installation Script
# Usage: ./install_wireguard_client.sh <config_filename.conf>
# Example: ./install_wireguard_client.sh wg0.conf

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Check if config file argument is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No configuration file specified${NC}"
    echo "Usage: $0 <config_filename.conf>"
    echo "Example: $0 wg0.conf"
    exit 1
fi

CONFIG_FILE="$1"
INTERFACE_NAME="${CONFIG_FILE%.conf}"

# Validate config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Configuration file '$CONFIG_FILE' not found${NC}"
    exit 1
fi

# Validate config file has .conf extension
if [[ ! "$CONFIG_FILE" == *.conf ]]; then
    echo -e "${RED}Error: Configuration file must have .conf extension${NC}"
    exit 1
fi

echo -e "${GREEN}Starting WireGuard client installation...${NC}"
echo ""

# Update package list
echo -e "${YELLOW}Updating package list...${NC}"
apt-get update

# Install WireGuard
echo -e "${YELLOW}Installing WireGuard...${NC}"
apt-get install -y wireguard wireguard-tools

# Create WireGuard directory if it doesn't exist
mkdir -p /etc/wireguard

# Copy configuration file to /etc/wireguard
echo -e "${YELLOW}Copying configuration file to /etc/wireguard/${INTERFACE_NAME}.conf${NC}"
cp "$CONFIG_FILE" "/etc/wireguard/${INTERFACE_NAME}.conf"

# Set proper permissions
chmod 600 "/etc/wireguard/${INTERFACE_NAME}.conf"

# Test the configuration
echo -e "${YELLOW}Testing WireGuard configuration...${NC}"
if wg-quick up "$INTERFACE_NAME"; then
    echo -e "${GREEN}✓ WireGuard interface brought up successfully${NC}"
    
    # Show interface status
    echo ""
    echo -e "${YELLOW}Current WireGuard status:${NC}"
    wg show
    
    # Bring down the interface for now
    echo ""
    echo -e "${YELLOW}Bringing interface down temporarily...${NC}"
    wg-quick down "$INTERFACE_NAME"
else
    echo -e "${RED}✗ Failed to bring up WireGuard interface${NC}"
    echo "Please check your configuration file"
    exit 1
fi

# Enable systemd service for auto-start at boot
echo ""
echo -e "${YELLOW}Enabling WireGuard service for auto-start at boot...${NC}"

# Create systemd override directory
mkdir -p "/etc/systemd/system/wg-quick@${INTERFACE_NAME}.service.d"

# Create override file to ensure network is ready before starting
cat > "/etc/systemd/system/wg-quick@${INTERFACE_NAME}.service.d/override.conf" << EOF
[Unit]
After=network-online.target
Wants=network-online.target
EOF

# Enable and start the service
systemctl enable "wg-quick@${INTERFACE_NAME}"
systemctl start "wg-quick@${INTERFACE_NAME}"

# Verify service status
echo ""
echo -e "${YELLOW}Verifying service status...${NC}"
if systemctl is-active --quiet "wg-quick@${INTERFACE_NAME}"; then
    echo -e "${GREEN}✓ WireGuard service is active and running${NC}"
else
    echo -e "${RED}✗ WireGuard service failed to start${NC}"
    systemctl status "wg-quick@${INTERFACE_NAME}"
    exit 1
fi

# Display final status
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}WireGuard client installation completed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Interface: $INTERFACE_NAME"
echo "  Config file: /etc/wireguard/${INTERFACE_NAME}.conf"
echo "  Service: wg-quick@${INTERFACE_NAME}"
echo ""
echo -e "${YELLOW}Status:${NC}"
wg show
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  Check status:           wg"
echo "  View routes:            ip route show"
echo "  Service status:         systemctl status wg-quick@${INTERFACE_NAME}"
echo "  Restart service:        systemctl restart wg-quick@${INTERFACE_NAME}"
echo "  Stop service:           systemctl stop wg-quick@${INTERFACE_NAME}"
echo "  Disable auto-start:     systemctl disable wg-quick@${INTERFACE_NAME}"
echo "  View logs:              journalctl -u wg-quick@${INTERFACE_NAME} -f"
echo ""
echo -e "${GREEN}The client will auto-connect on every boot.${NC}"
