# Use the kylemanna/openvpn image as the base
FROM kylemanna/openvpn

# Copy the ovpn_getclient script from the local filesystem to /usr/local/bin/ovpn_getclient in the image
ADD ovpn_getclient /usr/local/bin/ovpn_getclient

# Set execute permissions for the ovpn_getclient script
RUN chmod +x /usr/local/bin/ovpn_getclient
