#!/bin/bash

# wil, rob, vinc, sandrine, quen
users=('1219444903042352548' '1219448688074556850' '1219495018868245956' '1244929240911054651')
# Récuperation du SI, définition des variable 
if [[ "$1" == "majdc" ]];then
    id_task=1251467723498587145
    id_action=1251486618200572944
    id_card=1250744779034068946
    id_notification=8
elif [[ "$1" == "1ed" ]];then
    id_task=1252130262226044008
    id_action=1252130024450950246
    id_card=1252103317388002400
    id_notification=9
else
    echo "majdc ou 1ed en argument";
    exit;
fi


# Vérifie si la tache à été cocher
echo -e "Vérification de la tâche sur Ergo ...\n"
is_completed=$(docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"select is_completed from task WHERE id='$id_task';\"" | grep " t" | wc -l)
# Si oui, valider les nouvelles versions et décocher
if [[ "$is_completed" == "1" ]]; then
    cp /opt/scripts/tmp/$1.txt /var/www/html/collections/versions/$1.txt
    docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"update task set is_completed='f' WHERE id= '$id_task';\""
fi

# Téléchargement de la météo
echo -e "Téléchargement de la météo ..."
wget -O "/opt/scripts/tmp/meteo-ruche.html" https://portail-hebergement.intradef.gouv.fr/meteo-ruche/meteo-ruche.html --no-check-certificate 2>/dev/null

# Filtrage du logiciel et de sa version
nb_lines=$(cat /opt/scripts/tmp/meteo-ruche.html | wc -l)
table1=$(cat /opt/scripts/tmp/meteo-ruche.html  |grep -n table | head -n 1 | awk -F':' '{print $1}')
table2=$(cat /opt/scripts/tmp/meteo-ruche.html  |grep -n table | tail -n 1 | awk -F':' '{print $1}')
cat /opt/scripts/tmp/meteo-ruche.html | tail -n $(($nb_lines-$table1)) > /tmp/content.tmp
nb_lines=$(cat /tmp/content.tmp | wc -l)
cat /tmp/content.tmp | head -n $(($nb_lines-$table2)) > /opt/scripts/tmp/meteo-ruche.html
cat /opt/scripts/tmp/meteo-ruche.html | grep 'td' | awk '{print $2}' | egrep '^(_|[A-Z]*|[a-z]*|([0-9]|\.)*)$|(_)' | egrep '^([0-9].*|\.)$'  -B 1 | grep -v '-' > /opt/scripts/tmp/content.html

# Nettoyage et création du fichier temporaire de nouvelles versions
rm -f /opt/scripts/tmp/$1.txt
touch /opt/scripts/tmp/$1.txt
mkdir -p /opt/scripts/collection
is_new_versions=0
for l in $(cat /var/www/html/collections/versions/$1.txt); do
    name=$(echo $l | awk -F';' '{print $1}')
    new_v=$(cat /opt/scripts/tmp/content.html | grep -i $name -A 1 | tail -n 1;)
    old_v=$(echo $l | awk -F';' '{print $2}')
    echo "$name;$new_v">> /opt/scripts/tmp/$1.txt
    if [[ "$new_v" != "$old_v" ]];
    then
        is_new_versions=1
        echo "    $name : $old_v -> $new_v"
        wget -O  "/opt/scripts/collection/minarm-$name-$new_v.tar.gz" "https://drrcembdxla600c.dr-cpt.intradef.gouv.fr/api/galaxy/v3/artifacts/collections/published/minarm-$name-$new_v.tar.gz" --no-check-certificate 2>/dev/null
    fi;
done

if [[ "$is_new_versions" == 1 ]]; then
    echo -e "\nTarrage des collections ...\n"
    # tar czf /tmp/wiki_$today.sql.tgz -C /tmp/ wiki.sql
    tar czf /var/www/html/collections/collection_$1_$(date +%Y-%m-%d).tgz -C /opt/scripts/ collection/ 
    rm -rf /opt/scripts/collection/
    echo "Création des notifications sur Ergo ..."
    docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"update task set name='Cocher pour valider l''envoi aux devs : https://221.10.11.149:445/collections/collection_$1_$(date +%Y-%m-%d).tgz' WHERE id='$id_task'\""
    #docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"update notification set is_read='f' WHERE id= '1251486618276070417';\""
    
    count=10
    for user_id in "${users[@]}"
    do
        count=$(($count+1))
        docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"delete from notification where id='1317278488638127$id_notification$count';\""
        docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"insert into notification (id, user_id, action_id, card_id, is_read, created_at, updated_at) values (1317278488638127$id_notification$count, $user_id, $id_action, $id_card, 'f', NOW(), NULL);\""
        #echo "Welcome $user_id times"
    done
    
    #docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"update notification set is_read='f' WHERE id= '1252050382662665262';\""
    docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"update action set data='{\\\"text\\\":\\\"Nouvelle(s) Collection(s) : https://221.10.11.149:445/collections/collection_$1_$(date +%Y-%m-%d).tgz\\\"}' WHERE id='$id_action'\""
    docker exec -it planka-postgres-1 su postgres -c "psql -d planka -c \"update card set description='**Nouvelle(s) Collection(s) :**
*https://221.10.11.149:445/collections/collection_$1_$(date +%Y-%m-%d).tgz*

**Versions actuelles :**
*https://221.10.11.149:445/collections/versions/$1.txt*' WHERE id='$id_card'\""
fi

#/opt/scripts/check_meteo.sh majdc
# willi 1219444903042352548
# robin 1219448688074556850
# action 1251486618200572944
# card 1250744779034068946

#insert into notification (id, user_id, action_id, card_id, is_read, created_at, updated_at) values (1217278488638127845, 1219444903042352548, 1251486618200572944, 1250744779034068946, 'f', NOW(), NULL);
#insert into notification (id, user_id, action_id, card_id, is_read, created_at, updated_at) values (1217278488638127847, 1219448688074556850, 1251486618200572944, 1250744779034068946, 'f', NOW(), NULL);


#INSERT INTO action (id, card_id, user_id, type, data, created_at, updated_at) VALUES ('1217255965812851777', '1250744779034068946', '1250746749190932437', 'commentCard', '{"text": "rreff"}', NOW(), NULL);

#insert into notification (id, user_id, action_id, card_id, is_read, created_at, updated_at) values (1217278488638127845, 1219444903042352548, 1217255965812851777, 1250744779034068946, 'f', NOW(), NULL);
#insert into notification (id, user_id, action_id, card_id, is_read, created_at, updated_at) values (1217278488638127847, 1219448688074556850, 1217255965812851777, 1250744779034068946, 'f', NOW(), NULL);


#delete from action where id='1217255965812851777';
#delete from notification where id='1217278488638127845';
#delete from notification where id='1217278488638127847';


#\"update task set name='Cocher pour valider l\\'\\'envoi aux devs : https://221.10.11.149:445/collections/collection$(date +%Y-%m-%d).tgz' WHERE id='1251467723498587145'\"
#update task set name='Cocher pour valider l''envoi aux devs : https://221.10.11.149:445/collections/collection$(date +%Y-%m-%d).tgz' WHERE id='1251467723498587145'
#update task set is_read='f' WHERE id= '1251467723498587145';

#echo https://221.10.11.149:445/collections/collection$(date +%Y-%m-%d).tgz
# UPDATE 1251467723498587145
#UPDATE task SET name = 'Collections : ' WHERE id=1251467723498587145

#INSERT INTO action (id, card_id, user_id, type, data, created_at, updated_at) VALUES ('1217255965812851777', '1250744779034068946', '1250746749190932437', 'commentCard', '{"text": "rreff"}', '2024-04-05 06:50:18.884', NULL);


#INSERT INTO notification (id, user_id, action_id, card_id, is_read) VALUES ('1217255965812851743', '1250746749190932437', '1251481912946459658', '1250744779034068946', '{"text": "rreff"}', '2024-04-05 06:50:18.884', NULL);







