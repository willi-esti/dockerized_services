Import the databse

````sh
docker cp planka.sql postgres:/tmp; docker exec -it postgres su postgres -c 'psql -c "drop database planka"'; docker exec -it postgres su postgres -c 'psql -c "create database planka"' ; docker exec -it postgres su postgres -c 'psql planka -f /tmp/planka.sql';
docker cp wiki.sql postgres:/tmp; docker exec -it postgres su postgres -c 'psql -c "drop database wiki"'; docker exec -it postgres su postgres -c 'psql -c "create database wiki"' ; docker exec -it postgres su postgres -c 'psql wiki -f /tmp/wiki.sql';
```

Check the update date

```sql
-- Replace `:card_id` with the actual card ID you want to query.

SELECT 
    c.updated_at AS card_updated_at,
    t.updated_at AS task_updated_at
FROM 
    card c
LEFT JOIN 
    task t ON t.card_id = c.id
LEFT JOIN 
    attachment a ON a.card_id = c.id
LEFT JOIN 
    card_membership cm ON cm.card_id = c.id
LEFT JOIN 
    user_account u ON u.id = cm.user_id
LEFT JOIN 
    action ac ON ac.card_id = c.id AND ac.type = 'commentCard'
WHERE 
    c.id = '1520250197530117751' and
    c.updated_at is not null and
    t.updated_at is not null and
    c.updated_at > '2023-10-01 00:00:00' and
    t.updated_at > '2023-10-01 00:00:00';

```

```sql
-- Replace `:card_id` with the actual card ID you want to query.

SELECT 
    c.id AS card_id,
    c.name AS card_name,
    c.description AS card_description,
    c.due_date AS card_due_date,
    c.is_due_date_completed AS card_due_date_completed,
    c.created_at AS card_created_at,
    c.updated_at AS card_updated_at,
    t.id AS task_id,
    t.name AS task_name,
    t.is_completed AS task_completed,
    t.created_at AS task_created_at,
    t.updated_at AS task_updated_at,
    a.id AS attachment_id,
    a.name AS attachment_name,
    a.filename AS attachment_filename,
    a.created_at AS attachment_created_at,
    cm.user_id AS member_user_id,
    u.name AS member_name,
    u.email AS member_email,
    ac.id AS comment_id,
    ac.data->>'text' AS comment_text,
    ac.created_at AS comment_created_at
FROM 
    card c
LEFT JOIN 
    task t ON t.card_id = c.id
LEFT JOIN 
    attachment a ON a.card_id = c.id
LEFT JOIN 
    card_membership cm ON cm.card_id = c.id
LEFT JOIN 
    user_account u ON u.id = cm.user_id
LEFT JOIN 
    action ac ON ac.card_id = c.id AND ac.type = 'commentCard'
WHERE 
    c.id = '1520250197530117751';
```