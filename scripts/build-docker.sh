#!/bin/bash

# Build Script per AI Voice Assistant Docker Image
# Questo script costruisce l'immagine Docker con tutte le dipendenze

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 AI Voice Assistant - Docker Build${NC}"
echo "======================================"
echo ""

# Check if Docker is running
if ! /usr/local/bin/docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker non è in esecuzione!${NC}"
    echo "Apri Docker Desktop e riprova."
    exit 1
fi

echo -e "${GREEN}✅ Docker è in esecuzione${NC}"
echo ""

# Set variables
IMAGE_NAME="ai-voice-assistant"
IMAGE_TAG=${1:-latest}
REGISTRY=${DOCKER_REGISTRY:-""}

if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
else
    FULL_IMAGE="$IMAGE_NAME:$IMAGE_TAG"
fi

echo "📦 Building image: $FULL_IMAGE"
echo "📁 Build context: $(pwd)"
echo ""

# Build the image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
/usr/local/bin/docker build \
    --platform linux/amd64 \
    -t "$FULL_IMAGE" \
    -f Dockerfile \
    . \
    --progress=plain

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Build completato con successo!${NC}"
    echo ""
    echo "📊 Informazioni immagine:"
    /usr/local/bin/docker images "$IMAGE_NAME" | head -2
    echo ""
    echo "🚀 Per testare l'immagine:"
    echo "   docker run -p 8080:8080 --env-file .env $FULL_IMAGE"
    echo ""
    
    if [ -n "$REGISTRY" ]; then
        echo "📤 Per pushare l'immagine:"
        echo "   docker push $FULL_IMAGE"
    fi
else
    echo ""
    echo -e "${RED}❌ Build fallito!${NC}"
    exit 1
fi
