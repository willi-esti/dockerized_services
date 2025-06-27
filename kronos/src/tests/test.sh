
curl "http://localhost:8000/" -H "accept: application/json"
curl -X POST "http://localhost:8000/chat" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"message\":\"Hello, how are you?\"}"



