# AI Voice Assistant - Kubernetes Deployment

Sistema di assistente vocale AI open source per rispondere automaticamente alle chiamate telefoniche, deployabile su Kubernetes.

## 🎯 Obiettivo

Creare un'infrastruttura cloud-native che permetta all'intelligenza artificiale di rispondere automaticamente alle chiamate telefoniche in entrata, gestendo conversazioni naturali attraverso integrazione con LLM e servizi di telefonia.

## 🏗️ Architettura

```
┌─────────────────┐
│  Twilio/Plivo   │ ◄── Chiamate telefoniche in entrata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ingress/LB    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vocode Service  │ ◄── Orchestrazione conversazione
└────────┬────────┘
         │
    ┌────┴────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼
┌────────┐ ┌─────┐ ┌─────┐ ┌──────┐
│  STT   │ │ LLM │ │ TTS │ │ Redis│
│Deepgram│ │ GPT │ │11Labs│ │Cache │
└────────┘ └─────┘ └─────┘ └──────┘
```

## 📦 Componenti

- **Vocode Core**: Framework open source per voice AI
- **Deepgram**: Speech-to-Text
- **OpenAI GPT**: Large Language Model
- **ElevenLabs**: Text-to-Speech
- **Twilio**: Provider telefonia
- **Redis**: Cache e gestione stato conversazioni
- **PostgreSQL**: Database per logging e analytics

## 🚀 Quick Start

### Prerequisiti

- Kubernetes cluster (v1.24+)
- Helm 3.x
- kubectl configurato
- Account Twilio
- API keys per: OpenAI, Deepgram, ElevenLabs

### Installazione

```bash
# 1. Clone repository
git clone <your-repo-url>
cd ai-voice-assistant

# 2. Configura le secrets
cp kubernetes/secrets/secrets.example.yaml kubernetes/secrets/secrets.yaml
# Edita secrets.yaml con le tue API keys

# 3. Crea namespace
kubectl create namespace voice-ai

# 4. Applica secrets
kubectl apply -f kubernetes/secrets/secrets.yaml

# 5. Deploy con Helm
helm install voice-assistant ./helm/voice-assistant -n voice-ai

# 6. Verifica deployment
kubectl get pods -n voice-ai
```

## 🔧 Configurazione

### 1. Twilio Setup

1. Crea un account su [Twilio](https://www.twilio.com)
2. Acquista un numero di telefono
3. Configura webhook: `https://<your-domain>/webhooks/twilio/voice`

### 2. API Keys

Necessarie le seguenti API keys:
- `OPENAI_API_KEY`: Per LLM
- `DEEPGRAM_API_KEY`: Per STT
- `ELEVENLABS_API_KEY`: Per TTS
- `TWILIO_ACCOUNT_SID`: Account Twilio
- `TWILIO_AUTH_TOKEN`: Auth token Twilio

### 3. Configurazione Assistente

Modifica `config/assistant-config.yaml` per personalizzare:
- Messaggio iniziale
- Prompt del sistema
- Voce da utilizzare
- Lingua
- Comportamento conversazionale

## 📁 Struttura Repository

```
ai-voice-assistant/
├── README.md
├── .gitignore
├── LICENSE
│
├── app/                          # Applicazione Python
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config/
│   └── handlers/
│
├── kubernetes/                   # Manifesti Kubernetes raw
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secrets/
│   │   └── secrets.example.yaml
│   └── monitoring/
│
├── helm/                         # Helm charts
│   └── voice-assistant/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-prod.yaml
│       └── templates/
│
├── config/                       # Configurazioni applicazione
│   ├── assistant-config.yaml
│   └── prompts/
│
├── scripts/                      # Script utility
│   ├── setup.sh
│   ├── test-call.sh
│   └── deploy.sh
│
├── docs/                         # Documentazione
│   ├── architecture.md
│   ├── development.md
│   └── troubleshooting.md
│
└── monitoring/                   # Monitoring e observability
    ├── grafana-dashboard.json
    └── prometheus-rules.yaml
```

## 🔐 Sicurezza

- Tutte le API keys sono gestite tramite Kubernetes Secrets
- TLS/HTTPS obbligatorio per webhook Twilio
- Network policies per isolamento pods
- RBAC configurato con principio least-privilege

## 📊 Monitoring

L'applicazione espone metriche Prometheus su `/metrics`:
- Numero chiamate gestite
- Durata conversazioni
- Latenza componenti (STT, LLM, TTS)
- Errori e retry

Dashboard Grafana inclusa in `monitoring/grafana-dashboard.json`

## 🧪 Testing

```bash
# Test locale con ngrok
./scripts/test-local.sh

# Test chiamata
./scripts/test-call.sh +39XXXXXXXXXX
```

## 🐛 Troubleshooting

Vedi [docs/troubleshooting.md](docs/troubleshooting.md) per problemi comuni e soluzioni.

## 📝 Logging

Logging strutturato JSON inviato a:
- stdout per Kubernetes logs
- Loki (se configurato)
- File locale in development

Livelli log: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🔄 CI/CD

Pipeline GitHub Actions inclusa per:
- Build Docker image
- Security scanning
- Deploy automatico su staging
- Deploy manuale su production

## 🤝 Contribuire

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Apri Pull Request

## 📄 Licenza

MIT License - vedi [LICENSE](LICENSE) per dettagli

## 🙋 Supporto

Per domande o problemi:
- Apri una issue su GitHub
- Consulta la [documentazione](docs/)

## 🗺️ Roadmap

- [x] Setup base Kubernetes
- [x] Integrazione Vocode
- [ ] Multi-lingua support
- [ ] Web dashboard per gestione
- [ ] Analytics avanzate
- [ ] Integrazione calendario
- [ ] Call recording e trascrizioni
- [ ] A/B testing prompts

---

Sviluppato con ❤️ per Technacy Milano - Infrastructure Team
