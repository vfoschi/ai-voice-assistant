#!/bin/bash

# AI Voice Assistant - Setup Script
# Questo script aiuta nella configurazione iniziale del sistema

set -e

echo "🚀 AI Voice Assistant - Setup"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}❌ kubectl is required but not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}❌ helm is required but not installed${NC}"; exit 1; }

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Check if namespace exists
NAMESPACE="voice-ai"
if kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}⚠️  Namespace $NAMESPACE already exists${NC}"
else
    echo "📦 Creating namespace $NAMESPACE..."
    kubectl create namespace $NAMESPACE
    echo -e "${GREEN}✅ Namespace created${NC}"
fi
echo ""

# Check if secrets file exists
SECRETS_FILE="kubernetes/secrets/secrets.yaml"
if [ ! -f "$SECRETS_FILE" ]; then
    echo -e "${YELLOW}⚠️  Secrets file not found${NC}"
    echo "📝 Please copy secrets.example.yaml to secrets.yaml and fill in your API keys"
    echo "   cp kubernetes/secrets/secrets.example.yaml kubernetes/secrets/secrets.yaml"
    echo ""
    read -p "Have you configured the secrets file? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Setup cancelled. Please configure secrets first.${NC}"
        exit 1
    fi
fi

# Apply secrets
if [ -f "$SECRETS_FILE" ]; then
    echo "🔐 Applying secrets..."
    kubectl apply -f $SECRETS_FILE -n $NAMESPACE
    echo -e "${GREEN}✅ Secrets applied${NC}"
fi
echo ""

# Deploy with Helm
echo "📦 Deploying with Helm..."
echo "   Release name: voice-assistant"
echo "   Namespace: $NAMESPACE"
echo ""

read -p "Do you want to proceed with Helm installation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    helm upgrade --install voice-assistant ./helm/voice-assistant \
        --namespace $NAMESPACE \
        --create-namespace \
        --wait \
        --timeout 5m
    
    echo -e "${GREEN}✅ Deployment completed${NC}"
else
    echo "Deployment cancelled"
    exit 0
fi
echo ""

# Check deployment status
echo "🔍 Checking deployment status..."
kubectl get pods -n $NAMESPACE
echo ""

# Get service info
echo "📡 Service information:"
kubectl get svc -n $NAMESPACE
echo ""

# Get ingress info
echo "🌐 Ingress information:"
kubectl get ingress -n $NAMESPACE
echo ""

echo -e "${GREEN}✨ Setup completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Configure your Twilio webhook to point to your ingress URL"
echo "2. Test the service with a phone call"
echo "3. Monitor logs: kubectl logs -f -n $NAMESPACE -l app=voice-assistant"
echo ""
