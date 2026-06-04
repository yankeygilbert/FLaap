#!/bin/zsh
set -e
set -u

local qdrantStatus="http://127.0.0.1:6333"
local ollamaStatus="http://127.0.0.1:11434"

if curl --silent --fail --max-time 4 "$qdrantStatus" &> /dev/null; then
    echo "Qdrant server Up and Running "
else
    local killQ=$(lsof -t -i :6333)

    if [[ "$killQ" == "" ]]; then
        open -a Docker
        sleep 4
        docker run -d -p 6333:6333 -p 6334:6334 \
            -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
            qdrant/qdrant 
        
        echo "Qdrant Up"
    else
        kill -9 "$killQ"
        docker run -d -p 6333:6333 -p 6334:6334 \
            -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
            qdrant/qdrant
        
        echo "Qdrant Up"
    fi
fi

if curl --silent --fail --max-time 4 "$ollamaStatus" &> /dev/null; then
    echo "Ollama Server Up and Running"

else
    local killO= $(lsof -t -i :11434)

    if [[ "$killO" == "" ]]; then
        ollama serve

        echo "ollama Up"
    else
        kill -9 "$killO"

        ollama serve

        echo "ollama Up"
    fi
fi


    
