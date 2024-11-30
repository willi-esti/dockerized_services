#!/bin/bash

if [ $EUID -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(cat "$SCRIPT_DIR/../.env" | grep -v '#' | awk '/=/ {print $1}')
else
    echo "The .env file does not exist."
    exit 1
fi

# Base64 decode
base64 -d $VAULT_PATH/gaia/backup_only_needed.s.d.txt > /tmp/backup_only_needed.s.tgz
# Decrypt the backup file
#openssl enc -d -aes-256-cbc -in /tmp/backup_only_needed.s.tgz -out /tmp/backup_only_needed.tgz
gpg --output /tmp/backup_only_needed.tgz --decrypt /tmp/backup_only_needed.s.tgz
# if the decryption fails, exit
if [ $? -ne 0 ]; then
    exit 1
fi
rm -f /tmp/backup_only_needed.s.tgz

# Extract the contents of the decrypted backup file
tar xzf /tmp/backup_only_needed.tgz -C /tmp/
rm -f /tmp/backup_only_needed.tgz

# Extract the individual backup files
tar xzf /tmp/planka_attachments.tgz -C /tmp/
rm -rf /var/lib/docker/volumes/gaia-planka-attachments/_data/*
mv /tmp/planka_attachments/_data /var/lib/docker/volumes/gaia-planka-attachments



tar xzf /tmp/planka.sql.tgz -C /tmp/
tar xzf /tmp/wiki.sql.tgz -C /tmp/
rm -f /tmp/planka_attachments.tgz /tmp/planka.sql.tgz /tmp/wiki.sql.tgz

# Restore the Planka database
# if the docker is running, use it
if docker inspect httpd-gaia-postgres-1 > /dev/null 2>&1; then
    docker cp /tmp/planka.sql httpd-gaia-postgres-1:/tmp/
    docker exec -it httpd-gaia-postgres-1 su postgres -c 'psql -U postgres -c "create database planka"'
    docker exec -it httpd-gaia-postgres-1 su postgres -c 'psql -U postgres -d planka -f /tmp/planka.sql'
    rm -f /tmp/planka.sql
else
    echo 'Import database planka failed.'
fi

# Restore the Wiki.js database
# if the docker is running, use it
if docker inspect httpd-gaia-postgres-1 > /dev/null 2>&1; then
    docker cp /tmp/wiki.sql httpd-gaia-postgres-1:/tmp/
    docker exec -it httpd-gaia-postgres-1 su postgres -c 'psql -U postgres -c "create database wikijs"'
    docker exec -it httpd-gaia-postgres-1 su postgres -c 'psql -U postgres -c "CREATE USER wikijs WITH PASSWORD '\''wikijs'\'';"'
    docker exec -it httpd-gaia-postgres-1 su postgres -c 'psql -U postgres -d wikijs -f /tmp/wiki.sql'
    rm -f /tmp/wiki.sql
else
    echo 'Import database wikijs failed.'
fi
