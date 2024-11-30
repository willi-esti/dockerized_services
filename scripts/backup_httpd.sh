#!/bin/bash

# Usage: /scripts/backup_docker_apps.sh daily
# Usage: /scripts/backup_docker_apps.sh 30min
# Usage: /scripts/backup_docker_apps.sh daily --no-upload
# Usage: /scripts/backup_docker_apps.sh daily -n

NO_UPLOAD=false

if [[ -z $1 ]] || [[ $1 == "--help" ]] || [[ $1 == "-h" ]]; then
    echo "Usage: $0 {daily|30min} [--no-upload|-n]"
    exit 0
fi

if [[ $2 == "--no-upload" ]] || [[ $2 == "-n" ]]; then
    NO_UPLOAD=true
fi

# Ensure the script is run as root
if [[ $EUID -ne 0 ]]; then
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

today=$(date +%d%m%Y%H%M%S)

backup_dir="$BACKUP_PATH/$1"
tmp_dir="/tmp"

echo "1/14 Creating backup directory if it doesn't exist..."
mkdir -p $backup_dir

# Backup paths and filenames
declare -A backups
backups["mysql"]="$tmp_dir/mysql_$today.tgz"
backups["ovpn"]="$tmp_dir/ovpn_$today.tgz"
backups["planka_attachments"]="$tmp_dir/planka_attachments_$today.tgz"
#backups["planka_data"]="$tmp_dir/planka_data_$today.tgz"
backups["planka_project_background_images"]="$tmp_dir/planka_project_background_images_$today.tgz"
backups["planka_user_avatars"]="$tmp_dir/planka_user_avatars_$today.tgz"
#backups["wiki_data"]="$tmp_dir/wiki_data_$today.tgz"
backups["postgres_data"]="$tmp_dir/postgres_data_$today.tgz"
backups["gitea"]="$tmp_dir/gitea_$today.tgz"
backups["vault"]="$tmp_dir/vault_$today.tgz"
backups["root"]="$tmp_dir/root_$today.tgz"

echo "2/14 Creating backup tarballs for MySQL volume..."
tar czf "${backups["mysql"]}" -C /var/lib/docker/volumes/mysql-data .

echo "3/14 Creating backup tarballs for OVPN volume..."
tar czf "${backups["ovpn"]}" -C /var/lib/docker/volumes/ovpn-data .

echo "4/14 Creating backup tarballs for Planka volumes..."
tar czf "${backups["planka_attachments"]}" -C /var/lib/docker/volumes/planka-attachments .
#tar czf "${backups["planka_data"]}" -C /var/lib/docker/volumes/planka-data .
tar czf "${backups["planka_project_background_images"]}" -C /var/lib/docker/volumes/planka-project-background-images .
tar czf "${backups["planka_user_avatars"]}" -C /var/lib/docker/volumes/planka-user-avatars .

echo "5/14 Creating backup tarball for Planka database..."
docker exec -it httpd-postgres-1 su postgres -c 'pg_dump -U postgres planka > /tmp/planka.sql'
docker cp httpd-postgres-1:/tmp/planka.sql $tmp_dir
tar czf "$tmp_dir/planka_$today.sql.tgz" -C $tmp_dir planka.sql
rm -f $tmp_dir/planka.sql

echo "6/14 Creating backup tarballs for Wiki.js volumes..."
#tar czf "${backups["wiki_data"]}" -C /var/lib/docker/volumes/wiki-data .
tar czf "${backups["postgres_data"]}" -C /var/lib/docker/volumes/postgres_data .

echo "7/14 Creating backup tarball for Wiki.js database..."
docker exec -it httpd-postgres-1 su postgres -c 'pg_dump -U postgres wiki > /tmp/wiki.sql'
docker cp httpd-postgres-1:/tmp/wiki.sql $tmp_dir
tar czf "$tmp_dir/wiki_$today.sql.tgz" -C $tmp_dir wiki.sql
rm -f $tmp_dir/wiki.sql

echo "8/14 Creating backup tarballs for Gitea volume..."
tar czf "${backups["gitea"]}" -C /var/lib/docker/volumes/gitea-data .

echo "9/14 Creating backup tarball for Gitea database..."
docker exec -it httpd-postgres-1 su postgres -c 'pg_dump -U postgres gitea > /tmp/gitea.sql'
docker cp httpd-postgres-1:/tmp/gitea.sql $tmp_dir
tar czf "$tmp_dir/gitea_$today.sql.tgz" -C $tmp_dir gitea.sql
rm -f $tmp_dir/gitea.sql

echo "10/14 Creating backup tarball for Vault directory..."
tar czf "${backups["vault"]}" -C $VAULT_PATH .

echo "11/14 Creating backup tarball for Root directory..."
tar czf "${backups["root"]}" -C $ROOT_PATH .

echo "12/14 Creating a final backup tarball..."
tar czf "$backup_dir/backup_$today.tgz" -C $tmp_dir ${backups[@]} "$tmp_dir/planka_$today.sql.tgz" "$tmp_dir/wiki_$today.sql.tgz" "$tmp_dir/gitea_$today.sql.tgz"

echo "13/14 Cleaning up temporary files..."
rm -f ${backups["mysql"]} ${backups["ovpn"]} ${backups["planka_attachments"]} ${backups["planka_data"]} ${backups["planka_project_background_images"]} ${backups["planka_user_avatars"]} ${backups["planka_db"]} "$tmp_dir/planka_$today.sql.tgz" ${backups["wiki_data"]} ${backups["postgres_data"]} "$tmp_dir/wiki_$today.sql.tgz" ${backups["gitea"]} "$tmp_dir/gitea_$today.sql.tgz" ${backups["vault"]} ${backups["root"]}

echo "14/14 Managing backup retention..."
days=30
if [[ $1 == "daily" ]]; then
    days=48
fi

count=1
for i in $(ls -t $backup_dir/); do
    count=$(($count + 1))
    if [[ $count -gt $days ]]; then
        rm -f "$backup_dir/$i"
    fi
done

if [[ $NO_UPLOAD == false ]]; then
    # Upload to drive
    ACCESS_TOKEN=$(cat $ACCESS_TOKEN_FILE | head -n 1)
    FILE_PATH="$backup_dir/backup_$today.tgz"

    curl -X POST -L \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -F "metadata={name : '$(basename "$FILE_PATH")', parents : ['$FOLDER_ID']};type=application/json;charset=UTF-8" \
        -F "file=@$FILE_PATH;type=$(file --mime-type -b "$FILE_PATH")" \
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
fi


