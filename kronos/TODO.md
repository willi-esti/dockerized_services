Run test env : 

docker exec -it python_vsb bash
cd /app/
python embedder.py





Run the test env manually :

```sh
docker build -t python-app -f ./docker/python/Dockerfile .
docker run -it --name app python-app bash
```

```sh
docker compose down && docker volume rm vsb_db_data; docker compose up -d && docker compose logs -f
```



SELECT ki.*, c.embedding
FROM chunks c
JOIN knowledge_items ki ON c.knowledge_item_id = ki.id
JOIN knowledge_item_tags kit ON kit.knowledge_item_id = ki.id
JOIN tags t ON kit.tag_id = t.id
WHERE t.name = 'nutrition'
ORDER BY c.embedding <=> '[your_query_vector]'
LIMIT 10;
