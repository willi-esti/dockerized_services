<?php

if (posix_getuid() != 0) {
    echo "Script is running as root. Exiting...";
    exit;
}

require __DIR__ . '/vendor/autoload.php';

use Planka\Bridge\PlankaClient;
use Planka\Bridge\TransportClients\Client;
use Planka\Bridge\Config;
use Dotenv\Dotenv;

// Add a check to ensure the .env file exists and load environment variables accordingly
$dotenvPath = realpath(__DIR__ . '/../../.env');
if (file_exists($dotenvPath)) {
    $dotenv = Dotenv::createImmutable(dirname($dotenvPath));
    $dotenv->load();
} else {
    echo "The .env file does not exist.";
    exit(1);
}

$root_path = $_ENV['ROOT_PATH'];

$config = new Config(
    user: $_ENV['PLANKA_USER'],
    password: $_ENV['PLANKA_PWD'],
    baseUri: $_ENV['PLANKA_HOST'],
    port: 443
);

$planka = new PlankaClient($config);

$planka->authenticate();

$today = date("Y-m-d H:i:s");
$projectId = '1268932553713124751';
$initialListId = '1268933917876946323';
$destinationListId = '1268939791127283093';
$errorListId = '1268940194023736726';
$card = $planka->card->create($initialListId, "$today", 1);
$output = shell_exec("/bin/bash $root_path/scripts/get_token.sh");
$output = shell_exec("/bin/bash $root_path/scripts/backup_httpd.sh daily; echo $?");
echo $output;
$planka->cardMembership->add($card->id, '1259231137159447555');

$card->description = $output;
$planka->card->update($card);

$card->listId = $destinationListId;
$planka->card->moveCard($card);

#CardDto $card = $planka->card->get($initialListId);
#$planka->projectViewAction($projectId);
//$planka->card->moveCard();
//$planka->cardMembership->remove($initialListId, '1259231137159447555');
$planka->logout();

