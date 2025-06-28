#!/bin/bash

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 1
done

echo "✅ Ollama is ready!"

# Check if we already have models
MODELS=$(curl -s http://localhost:11434/api/tags | jq '.models | length')

if [ "$MODELS" = "0" ]; then
    echo "📥 No models found. Pulling default model: llama3.2"
    ollama pull llama3.2
    echo "✅ Default model installed!"
else
    echo "✅ Models already available"
fi

echo "🚀 Ollama setup complete!"
