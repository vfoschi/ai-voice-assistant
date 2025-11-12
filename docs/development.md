# Development Guide

Questa guida spiega come sviluppare e testare l'AI Voice Assistant localmente.

## Setup Ambiente di Sviluppo

### Prerequisiti

- Python 3.11+
- Docker & Docker Compose
- kubectl e Helm (per testing su Kubernetes)
- ngrok (per testare webhook Twilio in locale)
- Account e API keys per: Twilio, OpenAI, Deepgram, ElevenLabs

### Installazione Locale

1. **Clone repository**
   ```bash
   git clone <your-repo-url>
   cd ai-voice-assistant
   ```

2. **Setup Python environment**
   ```bash
   cd app
   python -m venv venv
   source venv/bin/activate  # su Linux/Mac
   # oppure
   venv\Scripts\activate  # su Windows
   
   pip install -r requirements.txt
   ```

3. **Configura environment variables**
   ```bash
   cp .env.example .env
   # Edita .env con le tue API keys
   ```

4. **Avvia Redis in locale (opzionale ma consigliato)**
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

## Testing Locale

### Test Basico

```bash
cd app
python main.py
```

L'applicazione parte su `http://localhost:8080`

Testa gli endpoint:
- `curl http://localhost:8080/`
- `curl http://localhost:8080/health`
- `curl http://localhost:8080/ready`

### Test con ngrok

Per testare le chiamate Twilio in locale:

1. **Avvia ngrok**
   ```bash
   ngrok http 8080
   ```

2. **Copia l'URL https di ngrok** (es. `https://abc123.ngrok.io`)

3. **Aggiorna .env**
   ```bash
   BASE_URL=https://abc123.ngrok.io
   ```

4. **Configura Twilio webhook**
   - Vai su Twilio Console → Phone Numbers
   - Seleziona il tuo numero
   - Voice & Fax → A CALL COMES IN
   - Imposta: `https://abc123.ngrok.io/webhooks/twilio/voice`

5. **Chiama il tuo numero Twilio** per testare!

## Build Docker Image

```bash
cd app
docker build -t voice-assistant:dev .
```

### Test con Docker

```bash
docker run -p 8080:8080 \
  --env-file .env \
  voice-assistant:dev
```

## Testing su Kubernetes Locale

### Setup Minikube/Kind

```bash
# Con minikube
minikube start
eval $(minikube docker-env)

# Build image
docker build -t voice-assistant:dev app/

# Deploy
kubectl create namespace voice-ai
kubectl apply -f kubernetes/secrets/secrets.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### Port forwarding per test

```bash
kubectl port-forward -n voice-ai svc/voice-assistant 8080:80
```

## Debugging

### Logs

```bash
# Locale
tail -f logs/app.log

# Kubernetes
kubectl logs -f -n voice-ai -l app=voice-assistant

# Segui logs di un pod specifico
kubectl logs -f -n voice-ai <pod-name>
```

### Debug con pdb

Aggiungi nel codice:
```python
import pdb; pdb.set_trace()
```

### Metrics

Controlla metriche Prometheus:
```bash
curl http://localhost:8080/metrics
```

## Struttura Codice

```
app/
├── main.py              # FastAPI app e endpoints
├── config/
│   └── settings.py      # Configurazione
├── handlers/
│   └── call_handler.py  # Logica gestione chiamate
└── requirements.txt     # Dipendenze Python
```

## Best Practices

### Coding Style

- Segui PEP 8
- Type hints per parametri e return values
- Docstrings per funzioni pubbliche
- Usa `async`/`await` dove possibile

### Git Workflow

1. Crea feature branch da `main`
   ```bash
   git checkout -b feature/my-feature
   ```

2. Commit atomici con messaggi chiari
   ```bash
   git commit -m "feat: add call recording feature"
   ```

3. Push e apri PR
   ```bash
   git push origin feature/my-feature
   ```

### Testing

```bash
# Run tests
pytest

# Con coverage
pytest --cov=app tests/

# Solo test specifici
pytest tests/test_call_handler.py -k test_start_call
```

## Configurazione IDE

### VS Code

File `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

### PyCharm

1. Imposta interprete Python al venv
2. Abilita type checking
3. Configura pytest come test runner

## Troubleshooting

### Problema: "Module not found"

```bash
pip install -r requirements.txt
```

### Problema: Twilio webhook non riceve chiamate

- Verifica che ngrok sia attivo
- Controlla che l'URL webhook sia corretto in Twilio
- Verifica i logs

### Problema: Errore API keys

- Controlla che tutte le keys siano nel file `.env`
- Verifica che non ci siano spazi extra nelle keys
- Testa le keys manualmente

## Risorse Utili

- [Vocode Documentation](https://docs.vocode.dev)
- [Twilio Voice API](https://www.twilio.com/docs/voice)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Deepgram API](https://developers.deepgram.com)
- [ElevenLabs API](https://docs.elevenlabs.io)

## Contatti

Per domande sullo sviluppo:
- Team Infrastructure: infrastructure@technacy.it
- GitHub Issues: [link-to-issues]
