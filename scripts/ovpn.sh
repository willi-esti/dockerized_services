SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(cat "$SCRIPT_DIR/../.env" | grep -v '#' | awk '/=/ {print $1}')
else
    echo "The .env file does not exist."
    exit 1
fi

# Check if the action and client name are provided as arguments
if [ -z "$1" ]; then
    echo "Usage: $0 {init|add|rm|list|show} [CLIENTNAME]"
    exit 1
fi

ACTION=$1
CLIENTNAME=$2

# Run these before starting the docker
OVPN_DATA=ovpn-data
#docker volume create --name $OVPN_DATA
#docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u udp://$SERVER_DOMAIN
#docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn ovpn_initpki

if [ "$ACTION" = "init" ]; then
    if [ ! "$(docker volume ls -q -f name=$OVPN_DATA)" ]; then
        docker volume create --name $OVPN_DATA
        docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u udp://$SERVER_DOMAIN
        docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn ovpn_initpki
    else
        echo "The volume $OVPN_DATA already exists."
        echo "If you want to reinitialize it, remove the volume with the following command:"
        echo "docker volume rm $OVPN_DATA"
    fi
elif [ "$ACTION" = "add" ]; then
    # Make a new client
    docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn:v2 easyrsa build-client-full $CLIENTNAME nopass
    docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn:v2 ovpn_getclient $CLIENTNAME > $OPENVPN_PATH/$CLIENTNAME.ovpn
elif [ "$ACTION" = "rm" ]; then
    # Revoke the client
    docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn:v2 easyrsa revoke $CLIENTNAME
    docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn:v2 easyrsa gen-crl
    rm -f $OPENVPN_PATH/$CLIENTNAME.ovpn
elif [ "$ACTION" = "list" ]; then
    # List all clients
    docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn:v2 ovpn_listclients
elif [ "$ACTION" = "show" ]; then
    # Show IP addresses of connected clients
    docker exec -it openvpn bash -c 'apk update;apk add nmap; nmap -sP 192.168.255.0/24' | grep '192.168.255' | cut -d ' ' -f5
else
    echo "Invalid action: $ACTION"
    echo "Usage: $cd0 {init|add|rm|list|show} [CLIENTNAME]"
    exit 1
fi

