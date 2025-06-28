#!/bin/bash

# Script to manage Ollama models in Docker container

CONTAINER_NAME="ollama"

echo "🤖 Ollama Model Manager"
echo "======================="

# Check if Ollama container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo "❌ Ollama container is not running. Please start it first:"
    echo "   docker-compose up ollama -d"
    exit 1
fi

echo "✅ Ollama container is running"
echo ""

# Function to pull a model
pull_model() {
    local model=$1
    echo "📥 Pulling model: $model"
    docker exec $CONTAINER_NAME ollama pull $model
    echo ""
}

# Function to list models
list_models() {
    echo "📋 Available models:"
    docker exec $CONTAINER_NAME ollama list
    echo ""
}

# Function to test a model
test_model() {
    local model=$1
    echo "🧪 Testing model: $model"
    echo "Sending test message..."
    docker exec $CONTAINER_NAME ollama run $model "Hello, can you respond with a short greeting?"
    echo ""
}

# Menu
case "${1:-menu}" in
    "pull")
        if [ -z "$2" ]; then
            echo "Usage: $0 pull <model-name>"
            echo "Example: $0 pull llama3.2"
            exit 1
        fi
        pull_model $2
        ;;
    "list")
        list_models
        ;;
    "test")
        if [ -z "$2" ]; then
            echo "Usage: $0 test <model-name>"
            echo "Example: $0 test llama3.2"
            exit 1
        fi
        test_model $2
        ;;
    "setup")
        echo "🚀 Setting up recommended models..."
        echo ""
        
        # Pull recommended models
        pull_model "llama3.2"
        pull_model "codellama"
        
        echo "✅ Setup complete!"
        echo ""
        list_models
        ;;
    "menu"|*)
        echo "Available commands:"
        echo "  $0 setup              - Pull recommended models (llama3.2, codellama)"
        echo "  $0 pull <model>       - Pull a specific model"
        echo "  $0 list               - List available models"
        echo "  $0 test <model>       - Test a model"
        echo ""
        echo "Recommended models:"
        echo "  - llama3.2           - General purpose chat (smaller, faster)"
        echo "  - llama3.2:70b       - More capable but larger"
        echo "  - codellama          - Specialized for code"
        echo "  - mistral            - Fast and efficient"
        echo "  - phi3               - Very small and fast"
        echo ""
        ;;
esac
