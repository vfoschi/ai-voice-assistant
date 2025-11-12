# Cheat Sheet - Comandi Utili

Raccolta di comandi frequentemente utilizzati per gestire l'AI Voice Assistant.

## 🚀 Deploy & Setup

### Deploy Completo
```bash
# Setup automatico (consigliato)
./scripts/setup.sh

# Deploy con Helm
helm install voice-assistant ./helm/voice-assistant \
  --namespace voice-ai \
  --create-namespace \
  --values helm/voice-assistant/values-prod.yaml

# Upgrade deployment esistente
helm upgrade voice-assistant ./helm/voice-assistant \
  --namespace voice-ai \
  --reuse-values
```

### Deploy con kubectl (Raw Manifests)
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets/secrets.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml
```

## 📊 Monitoring

### Logs
```bash
# Tutti i pods
kubectl logs -f -n voice-ai -l app=voice-assistant

# Pod specifico
kubectl logs -f -n voice-ai <pod-name>

# Ultimi 100 righe
kubectl logs -n voice-ai -l app=voice-assistant --tail=100

# Logs con timestamp
kubectl logs -n voice-ai -l app=voice-assistant --timestamps=true

# Logs di tutti i container in un pod
kubectl logs -n voice-ai <pod-name> --all-containers=true
```

### Status & Health
```bash
# Status pods
kubectl get pods -n voice-ai

# Descrizione dettagliata
kubectl describe pod -n voice-ai <pod-name>

# Status deployment
kubectl get deployment -n voice-ai

# Status service
kubectl get svc -n voice-ai

# Status ingress
kubectl get ingress -n voice-ai

# Events
kubectl get events -n voice-ai --sort-by='.lastTimestamp'
```

### Metrics
```bash
# Port forward per accedere alle metriche
kubectl port-forward -n voice-ai svc/voice-assistant 8080:80

# In un altro terminale
curl http://localhost:8080/metrics

# Health check
curl http://localhost:8080/health

# Readiness check
curl http://localhost:8080/ready
```

## 🔧 Troubleshooting

### Debug Pods
```bash
# Shell interattiva in un pod
kubectl exec -it -n voice-ai <pod-name> -- /bin/sh

# Esegui comando in un pod
kubectl exec -n voice-ai <pod-name> -- env

# Copia file da pod
kubectl cp voice-ai/<pod-name>:/path/to/file ./local-file

# Copia file a pod
kubectl cp ./local-file voice-ai/<pod-name>:/path/to/file
```

### Network Debugging
```bash
# Test connettività al service
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -n voice-ai

# DNS lookup
kubectl run -it --rm debug --image=tutum/dnsutils --restart=Never -n voice-ai -- nslookup voice-assistant

# Port forward per test locale
kubectl port-forward -n voice-ai svc/voice-assistant 8080:80
```

### Restart & Rollback
```bash
# Restart deployment (rollout)
kubectl rollout restart deployment/voice-assistant -n voice-ai

# Rollout history
kubectl rollout history deployment/voice-assistant -n voice-ai

# Rollback a versione precedente
kubectl rollout undo deployment/voice-assistant -n voice-ai

# Rollback a versione specifica
kubectl rollout undo deployment/voice-assistant -n voice-ai --to-revision=2

# Status rollout
kubectl rollout status deployment/voice-assistant -n voice-ai
```

## 🔐 Secrets Management

### View Secrets
```bash
# Lista secrets
kubectl get secrets -n voice-ai

# Descrizione secret
kubectl describe secret voice-assistant-secrets -n voice-ai

# Decode secret (esempio)
kubectl get secret voice-assistant-secrets -n voice-ai -o jsonpath='{.data.OPENAI_API_KEY}' | base64 --decode
```

### Update Secrets
```bash
# Edita secret
kubectl edit secret voice-assistant-secrets -n voice-ai

# Ricrea secret da file
kubectl delete secret voice-assistant-secrets -n voice-ai
kubectl apply -f kubernetes/secrets/secrets.yaml

# Patch secret
kubectl patch secret voice-assistant-secrets -n voice-ai \
  -p='{"stringData":{"OPENAI_API_KEY":"nuovo-valore"}}'
```

## ⚙️ Configuration Updates

### Update ConfigMap
```bash
# Edita configmap
kubectl edit configmap voice-assistant-config -n voice-ai

# Apply nuovo configmap
kubectl apply -f kubernetes/configmap.yaml

# Restart pods per applicare cambiamenti
kubectl rollout restart deployment/voice-assistant -n voice-ai
```

### Helm Values Update
```bash
# Update con nuovo values file
helm upgrade voice-assistant ./helm/voice-assistant \
  --namespace voice-ai \
  --values helm/voice-assistant/values-prod.yaml

# Override singolo valore
helm upgrade voice-assistant ./helm/voice-assistant \
  --namespace voice-ai \
  --set replicaCount=3

# Dry-run per vedere cambiamenti
helm upgrade voice-assistant ./helm/voice-assistant \
  --namespace voice-ai \
  --values helm/voice-assistant/values-prod.yaml \
  --dry-run --debug
```

## 📈 Scaling

### Manual Scaling
```bash
# Scala a N repliche
kubectl scale deployment voice-assistant -n voice-ai --replicas=5

# Scale down a 1 replica
kubectl scale deployment voice-assistant -n voice-ai --replicas=1
```

### Auto-scaling
```bash
# Abilita HPA
kubectl autoscale deployment voice-assistant -n voice-ai \
  --min=2 --max=10 --cpu-percent=80

# Status HPA
kubectl get hpa -n voice-ai

# Descrizione HPA
kubectl describe hpa voice-assistant -n voice-ai

# Delete HPA
kubectl delete hpa voice-assistant -n voice-ai
```

## 🧹 Cleanup

### Delete Resources
```bash
# Delete con Helm
helm uninstall voice-assistant -n voice-ai

# Delete namespace (ATTENZIONE: cancella tutto)
kubectl delete namespace voice-ai

# Delete singoli resources
kubectl delete deployment voice-assistant -n voice-ai
kubectl delete service voice-assistant -n voice-ai
kubectl delete ingress voice-assistant -n voice-ai
kubectl delete configmap voice-assistant-config -n voice-ai
kubectl delete secret voice-assistant-secrets -n voice-ai
```

## 🐳 Docker

### Build
```bash
# Build image
cd app
docker build -t voice-assistant:latest .

# Build con tag specifico
docker build -t your-registry/voice-assistant:v1.0.0 .

# Build multi-platform
docker buildx build --platform linux/amd64,linux/arm64 \
  -t your-registry/voice-assistant:latest .
```

### Push to Registry
```bash
# Login a registry
docker login your-registry.com

# Tag image
docker tag voice-assistant:latest your-registry/voice-assistant:v1.0.0

# Push
docker push your-registry/voice-assistant:v1.0.0

# Push latest
docker push your-registry/voice-assistant:latest
```

### Local Testing
```bash
# Run container
docker run -p 8080:8080 \
  --env-file app/.env \
  voice-assistant:latest

# Run con logs
docker run -p 8080:8080 \
  --env-file app/.env \
  -v $(pwd)/logs:/app/logs \
  voice-assistant:latest

# Run interattivo
docker run -it --rm \
  --env-file app/.env \
  voice-assistant:latest /bin/sh
```

## 📝 Logging

### Aggregazione Logs
```bash
# Logs da tutti i pods
kubectl logs -n voice-ai -l app=voice-assistant --all-containers=true

# Salva logs su file
kubectl logs -n voice-ai -l app=voice-assistant > logs.txt

# Stream logs con grep
kubectl logs -f -n voice-ai -l app=voice-assistant | grep ERROR

# Logs con jq per parsing JSON
kubectl logs -n voice-ai -l app=voice-assistant | jq '.'
```

## 🔍 Inspection

### Resource Usage
```bash
# CPU e Memory usage dei pods
kubectl top pods -n voice-ai

# Usage di tutti i nodes
kubectl top nodes

# Describe deployment
kubectl describe deployment voice-assistant -n voice-ai

# Get YAML del deployment
kubectl get deployment voice-assistant -n voice-ai -o yaml

# Get JSON del deployment
kubectl get deployment voice-assistant -n voice-ai -o json
```

### Network & Ingress
```bash
# Test ingress
curl -v https://voice-assistant.tuodominio.com

# Test webhook endpoint
curl -X POST https://voice-assistant.tuodominio.com/webhooks/twilio/voice \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=%2B1234567890&To=%2B0987654321"

# DNS lookup
nslookup voice-assistant.tuodominio.com

# Certificate check
echo | openssl s_client -servername voice-assistant.tuodominio.com \
  -connect voice-assistant.tuodominio.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

## 🔄 CI/CD

### GitHub Actions (esempio)
```bash
# Trigger manual workflow
gh workflow run deploy.yml

# Lista workflows
gh workflow list

# View workflow run
gh run list --workflow=deploy.yml

# Watch workflow run
gh run watch
```

### Manual Deploy Pipeline
```bash
# 1. Build
docker build -t your-registry/voice-assistant:$VERSION app/

# 2. Test
docker run --rm your-registry/voice-assistant:$VERSION pytest

# 3. Push
docker push your-registry/voice-assistant:$VERSION

# 4. Deploy
helm upgrade voice-assistant ./helm/voice-assistant \
  --namespace voice-ai \
  --set image.tag=$VERSION
```

## 🧪 Testing

### Local Testing
```bash
# Unit tests
cd app
pytest

# Con coverage
pytest --cov=app tests/

# Solo test specifici
pytest tests/test_call_handler.py

# Verbose
pytest -v
```

### Integration Testing
```bash
# Health check
curl http://localhost:8080/health

# Readiness check
curl http://localhost:8080/ready

# Metrics
curl http://localhost:8080/metrics

# Test chiamata (con ngrok)
# Chiama il numero Twilio e monitora logs
kubectl logs -f -n voice-ai -l app=voice-assistant
```

## 📊 Monitoring con Prometheus

### Query Prometheus
```bash
# Port forward Prometheus (se installato)
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Esempi query (da eseguire in Prometheus UI)
# Numero totale chiamate
sum(voice_assistant_calls_total)

# Durata media chiamate
rate(voice_assistant_call_duration_seconds_sum[5m]) / 
rate(voice_assistant_call_duration_seconds_count[5m])

# Errori per tipo
sum by (error_type) (voice_assistant_errors_total)
```

## 🔔 Alerts

### Check Alertmanager
```bash
# Port forward Alertmanager
kubectl port-forward -n monitoring svc/alertmanager 9093:9093

# Silence alert
amtool silence add alertname=VoiceAssistantDown --duration=1h
```

## 💡 Tips & Tricks

### Quick Pod Access
```bash
# Alias utili (aggiungi a ~/.bashrc o ~/.zshrc)
alias k='kubectl'
alias kva='kubectl -n voice-ai'
alias kvapods='kubectl get pods -n voice-ai'
alias kvalogs='kubectl logs -f -n voice-ai -l app=voice-assistant'
```

### Watch Commands
```bash
# Watch pods status
watch kubectl get pods -n voice-ai

# Watch con evidenziazione differenze
watch -d kubectl get pods -n voice-ai

# Auto-refresh logs
while true; do kubectl logs -n voice-ai -l app=voice-assistant --tail=20; sleep 2; done
```

### One-liners Utili
```bash
# Restart tutti i pods
kubectl delete pods -n voice-ai -l app=voice-assistant

# Get IP di tutti i pods
kubectl get pods -n voice-ai -o wide

# Numero di pods in running
kubectl get pods -n voice-ai -l app=voice-assistant --field-selector=status.phase=Running --no-headers | wc -l

# Pod con più errori
kubectl get pods -n voice-ai -o json | jq '.items[] | select(.status.containerStatuses[].restartCount > 0) | .metadata.name'
```

## 📚 Documentation Links

- Kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Helm Commands: https://helm.sh/docs/helm/
- Docker CLI: https://docs.docker.com/engine/reference/commandline/cli/
- Vocode Docs: https://docs.vocode.dev

---

**Pro Tip**: Salva questo file e tienilo a portata di mano! 🎯
