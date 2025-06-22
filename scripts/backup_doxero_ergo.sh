#/opt/scripts/backup_doxero_ergo.sh daily
#/opt/scripts/backup_doxero_ergo.sh 30min


if [[ $1 != "daily" ]] &&  [[ $1 != "30min" ]];
then
    echo "Specifier l'argument daily ou 30min";
    exit;
fi;

today=$(date +%d%m%Y%H%M%S)

planka_data=planka_data.tgz;
tar czf /tmp/$planka_data -C  /var/lib/docker/volumes/ planka_data

postgres_data=postgres_data.tgz;
tar czf /tmp/$postgres_data -C /var/lib/docker/volumes/ postgres_data
docker exec postgres su postgres -c 'pg_dump -U postgres planka > /tmp/planka.sql'
docker cp postgres_data:/tmp/planka.sql /tmp/
tar czf /tmp/planka.sql.tgz -C /tmp/ planka.sql
rm -f  /tmp/planka.sql

docker exec wikijs-db-1 su postgres -c 'pg_dump -U wikijs wiki > /tmp/wiki.sql'
docker cp wikijs-db-1:/tmp/wiki.sql /tmp/
tar czf /tmp/wiki.sql.tgz -C /tmp/ wiki.sql
rm -f  /tmp/wiki.sql

wiki_data=wiki_data.tgz;
tar czf /tmp/$wiki_data -C /var/lib/docker/volumes/ wiki_data

pgadmin_data=pgadmin_data.tgz;
tar czf /tmp/$pgadmin_data -C /var/lib/docker/volumes/ pgadmin_data


tar czf /opt/backup/$1/backup_$today.tgz -C /tmp/ $planka_data $postgres_data $wiki_data $pgadmin_data planka.sql.tgz wiki.sql.tgz
rm -f /tmp/$planka_data /tmp/$postgres_data /tmp/$wiki_data /tmp/$pgadmin_data /tmp/planka.sql.tgz /tmp/wiki.sql.tgz


days=30
if [[ $1 == "daily" ]];
then
    days=48
fi;

count=1;
for i in $(ls -r  /opt/backup/$1/);
do
	#echo $i $count;
	count=$(($count+1));

	if [[ $count -gt $days ]];
	then
		rm -f  /opt/backup/$1/$i;
	fi;
done







