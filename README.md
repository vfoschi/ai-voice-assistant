# AI Voice Assistant - Kubernetes Deployment

Sistema di assistente vocale AI open source per rispondere automaticamente alle chiamate telefoniche, deployabile su Kubernetes.

**Supporta sia Twilio che account SIP standard!**

## 🎯 Obiettivo

Creare un'infrastruttura cloud-native che permetta all'intelligenza artificiale di rispondere automaticamente alle chiamate telefoniche in entrata, gestendo conversazioni naturali attraverso integrazione con LLM e servizi di telefonia.

## 📞 Opzioni Telefonia

Il sistema supporta due modalità di connessione telefonica:

### 1. **Twilio** (Consigliato per semplicità)
- Setup rapido e semplice
- Numeri telefonici in 60+ paesi
- Webhook HTTP per gestione chiamate
- Costi: ~$1/mese per numero + $0.013/minuto

### 2. **Account SIP** (Consigliato per flessibilità)
- Usa qualsiasi provider SIP/VoIP
- Porta il tuo numero esistente
- Integrazione con PBX aziendale
- Costi variabili in base al provider
- Supporto WebRTC per chiamate via browser

## 🏗️ Architettura

```
┌─────────────────┐
│  Twilio / SIP   │ ◄── Chiamate telefoniche in entrata
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
- **Twilio / SIP**: Provider telefonia (configurabile)
- **Redis**: Cache e gestione stato conversazioni
- **PostgreSQL**: Database per logging e analytics

## 🚀 Quick Start

### Prerequisiti

- Kubernetes cluster (v1.24+)
- Helm 3.x
- kubectl configurato
- **Opzione A**: Account Twilio  
  **O**  
  **Opzione B**: Account SIP (username, password, server)
- API keys per: OpenAI, Deepgram, ElevenLabs

### Installazione

```bash
# 1. Clone repository
git clone https://github.com/vfoschi/ai-voice-assistant.git
cd ai-voice-assistant

# 2. Configura le secrets
cp kubernetes/secrets/secrets.example.yaml kubernetes/secrets/secrets.yaml
# Edita secrets.yaml con le tue API keys

# 3. Scegli il provider telefonia
# Edita kubernetes/configmap.yaml e imposta:
# TELEPHONY_PROVIDER: "twilio"  # oppure "sip"

# 4. Crea namespace
kubectl create namespace voice-ai

# 5. Applica secrets
kubectl apply -f kubernetes/secrets/secrets.yaml

# 6. Deploy con Helm
helm install voice-assistant ./helm/voice-assistant -n voice-ai

# 7. Verifica deployment
kubectl get pods -n voice-ai
```

## 🔧 Configurazione

### Opzione A: Setup Twilio

1. Crea un account su [Twilio](https://www.twilio.com)
2. Acquista un numero di telefono
3. Configura webhook: `https://<your-domain>/webhooks/twilio/voice`

**Variabili richieste** in `secrets.yaml`:
```yaml
TELEPHONY_PROVIDER: "twilio"
TWILIO_ACCOUNT_SID: "ACxxxxx..."
TWILIO_AUTH_TOKEN: "your_token"
TWILIO_PHONE_NUMBER: "+1234567890"
```

### Opzione B: Setup Account SIP

1. Ottieni credenziali dal tuo provider SIP (es: 3CX, FreePBX, Asterisk)
2. Configura il server SIP per accettare connessioni WebRTC
3. Nota server, username, password, domain

**Variabili richieste** in `secrets.yaml`:
```yaml
TELEPHONY_PROVIDER: "sip"
SIP_SERVER: "sip.yourdomain.com"
SIP_PORT: "5060"
SIP_USERNAME: "your_username"
SIP_PASSWORD: "your_password"
SIP_DOMAIN: "yourdomain.com"
SIP_TRANSPORT: "udp"  # o "tcp", "tls"
```

**Endpoint WebRTC**: `https://<your-domain>/webhooks/sip/webrtc`

### API Keys (Sempre Necessarie)

Necessarie le seguenti API keys:
- `OPENAI_API_KEY`: Per LLM (GPT-4)
- `DEEPGRAM_API_KEY`: Per Speech-to-Text
- `ELEVENLABS_API_KEY`: Per Text-to-Speech

### Configurazione Assistente

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
├── QUICK_START.md
├── .gitignore
├── LICENSE
│
├── app/                          # Applicazione Python
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                   # FastAPI app (Twilio + SIP)
│   ├── config/
│   │   └── settings.py           # Config con supporto SIP
│   └── handlers/
│       ├── call_handler.py       # Gestione chiamate
│       └── sip_handler.py        # Handler SIP/WebRTC
│
├── kubernetes/                   # Manifesti Kubernetes
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secrets/
│
├── helm/                         # Helm charts
│   └── voice-assistant/
│
├── config/                       # Configurazioni
│   └── assistant-config.yaml
│
├── scripts/                      # Script utility
│   └── setup.sh
│
└── docs/                         # Documentazione
    ├── architecture.md
    ├── development.md
    ├── sip-configuration.md      # Guida setup SIP
    └── troubleshooting.md
```

## 🔐 Sicurezza

- Tutte le API keys gestite tramite Kubernetes Secrets
- TLS/HTTPS obbligatorio per webhook
- Per SIP: supporto TLS transport e SRTP per media encryption
- Network policies per isolamento pods
- RBAC configurato

## 📊 Monitoring

L'applicazione espone metriche Prometheus su `/metrics`:
- Numero chiamate gestite (Twilio + SIP)
- Durata conversazioni
- Latenza componenti
- Errori per provider

Endpoint aggiuntivi:
- `GET /sip/status` - Status connessione SIP e chiamate attive

## 🔄 Switching tra Twilio e SIP

Puoi switchare tra provider semplicemente cambiando la variabile:

```bash
# Update ConfigMap
kubectl edit configmap voice-assistant-config -n voice-ai
# Cambia: TELEPHONY_PROVIDER da "twilio" a "sip" (o viceversa)

# Restart pods
kubectl rollout restart deployment/voice-assistant -n voice-ai
```

## 🌐 Provider SIP Compatibili

Testato con:
- ✅ 3CX
- ✅ FreePBX / Asterisk
- ✅ Twilio SIP (sì, supporta anche SIP oltre che API!)
- ✅ Kamailio
- ✅ OpenSIPS
- ⚙️ Qualsiasi server SIP standard

## 🧪 Testing

### Test con Twilio
Chiama il numero Twilio configurato

### Test con SIP
1. Configura un softphone SIP (es: Zoiper, Linphone)
2. Chiama l'extension configurata
3. L'assistente risponderà automaticamente

## 📚 Documentazione Aggiuntiva

- **[QUICK_START.md](QUICK_START.md)** - Setup rapido
- **[docs/architecture.md](docs/architecture.md)** - Architettura dettagliata
- **[docs/sip-configuration.md](docs/sip-configuration.md)** - Guida setup SIP
- **[docs/development.md](docs/development.md)** - Sviluppo locale
- **[docs/cheat-sheet.md](docs/cheat-sheet.md)** - Comandi utili

## 🐛 Troubleshooting

### Twilio
- Verifica webhook URL in Twilio console
- Controlla logs: `kubectl logs -n voice-ai -l app=voice-assistant`

### SIP
- Verifica registrazione: `curl https://your-domain/sip/status`
- Controlla firewall per porta SIP (default 5060)
- Verifica STUN/TURN server per NAT traversal

## 💰 Costi Stimati

### Con Twilio
- Numero: $1/mese
- Chiamate: $0.013/minuto
- **Totale per 100 chiamate (500 min)**: ~$7/mese

### Con SIP
- Dipende dal provider
- Spesso incluso in abbonamento VoIP aziendale
- **Range tipico**: $0-50/mese

### API (uguali per entrambi)
- OpenAI GPT-4: ~$10-20/mese
- Deepgram: ~$5-10/mese  
- ElevenLabs: ~$5-22/mese

## 🤝 Contribuire

1. Fork del repository
2. Crea feature branch
3. Commit changes
4. Push e apri Pull Request

## 📄 Licenza

MIT License - vedi [LICENSE](LICENSE)

## 🙋 Supporto

- Issues: https://github.com/vfoschi/ai-voice-assistant/issues
- Email: vittorio.foschi@technacy.it

---

Sviluppato con ❤️ per Technacy Milano - Infrastructure Team
