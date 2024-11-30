# Dockerized Services

## Project Description

This project provides a set of Dockerized services for managing web hosting, including PHP scripts, backup solutions, and Git version control. It includes instructions for setting up Docker, managing SSL certificates with Certbot, and configuring Google Service Accounts for backup uploads.

## Prerequisites

```
apt install -y jq php php-xml php-curl composer cron
```

Make a .env form the .env.example

## Docker

Install docker https://docs.docker.com/engine/install/

Adding user to docker group
```
sudo usermod -aG docker username
```

Apply the change
```
newgrp docker
```
## Certbot

```
sudo certbot -d example.fr -d *.example.fr --manual --preferred-challenges dns certonly
```

To Renew manually (Next date: 2024-12-01)

```
certbot renew --manual
```

## Google Service Accounts

For uploading backups to Google Drive

1.  Create a service account:  Google Cloud Console
    
    -   IAM and administration > Service accounts > Create
    -   Email:  example@test-api-847519.iam.gserviceaccount.com
2.  Then in Keys:
    
    -   Add a key
    -   Download the key and place it in  `/opt/vault/`
    -   Modify  `SERVICE_ACCOUNT_KEY`  in  `/opt/script/get_token.sh`  with the name of the key file
    -   Run  `get_token.sh`
    -   A file  `access_token`  will be created with  `$SERVICE_ACCOUNT_KEY.access_token`
3.  `backup_httpd.sh`  should use this file for uploads with a  `*.access_token`  (Do not create other  `.access_token`  files in vault)

## PHP 

```
cd scripts/planka-api-php
composer install
```
## Cron

Replace path_to :

```
0 7 * * * root /usr/bin/php -f /path_to/httpd/scripts/planka-api-php/planka_api.php
```
## Run

In ~/.bashrc
```
export PATH=$PATH:/path/to/your/https/scripts/
```

```
source ~/.bashrc 
```
Start :
```
run # For the help
```

Example :
```
run web up
```
