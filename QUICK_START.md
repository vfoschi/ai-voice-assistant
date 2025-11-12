# 🚀 Quick Start - AI Voice Assistant

## 📦 Cosa hai ricevuto

Repository Git completo e production-ready per deployare un assistente vocale AI su Kubernetes che può rispondere automaticamente alle tue chiamate telefoniche.

## 🎯 Funzionalità Principali

✅ Risponde automaticamente alle chiamate in entrata
✅ Conversazioni naturali in italiano tramite GPT-4
✅ Integrazione con Twilio per telefonia
✅ Speech-to-Text con Deepgram
✅ Text-to-Speech con ElevenLabs
✅ Deploy su Kubernetes con Helm
✅ Monitoring con Prometheus
✅ Scalabile e production-ready

## 📋 Cosa ti serve

### Account e API Keys necessarie:

1. **Twilio** (https://www.twilio.com)
   - Account SID
   - Auth Token
   - Numero di telefono

2. **OpenAI** (https://platform.openai.com)
   - API Key per GPT-4

3. **Deepgram** (https://www.deepgram.com)
   - API Key per Speech-to-Text

4. **ElevenLabs** (https://elevenlabs.io)
   - API Key per Text-to-Speech

5. **Kubernetes cluster**
   - Con Helm installato
   - Nginx Ingress Controller
   - Cert-manager (opzionale, per TLS automatico)

## 🏃 Setup Rapido (5 minuti)

### 1. Upload su GitHub/GitLab

```bash
cd ai-voice-assistant

# Aggiungi remote del tuo repository
git remote add origin https://github.com/TUO-USERNAME/ai-voice-assistant.git

# Push
git push -u origin master
```

### 2. Configura le Secrets

```bash
# Copia il file di esempio
cp kubernetes/secrets/secrets.example.yaml kubernetes/secrets/secrets.yaml

# Edita con le tue API keys (usa il tuo editor preferito)
nano kubernetes/secrets/secrets.yaml
# oppure
vim kubernetes/secrets/secrets.yaml
```

**IMPORTANTE**: NON committare `secrets.yaml` nel repository!

### 3. Aggiorna la Configurazione

Edita `helm/voice-assistant/values.yaml`:
```yaml
# Cambia il tuo dominio
config:
  baseUrl: "https://voice-assistant.tuodominio.com"

ingress:
  hosts:
    - host: voice-assistant.tuodominio.com
```

### 4. Deploy su Kubernetes

```bash
# Metodo 1: Script automatico (consigliato)
./scripts/setup.sh

# Metodo 2: Manuale con kubectl
kubectl create namespace voice-ai
kubectl apply -f kubernetes/secrets/secrets.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml

# Metodo 3: Con Helm (consigliato per production)
helm install voice-assistant ./helm/voice-assistant \
  --namespace voice-ai \
  --create-namespace
```

### 5. Verifica il Deploy

```bash
# Controlla i pods
kubectl get pods -n voice-ai

# Controlla i logs
kubectl logs -f -n voice-ai -l app=voice-assistant

# Verifica l'ingress
kubectl get ingress -n voice-ai
```

### 6. Configura Twilio

1. Vai su https://console.twilio.com/
2. Phone Numbers → Manage → Active numbers
3. Clicca sul tuo numero
4. Nella sezione "Voice & Fax":
   - A CALL COMES IN: Webhook
   - URL: `https://voice-assistant.tuodominio.com/webhooks/twilio/voice`
   - Method: POST
5. Salva

### 7. Testa!

Chiama il tuo numero Twilio e l'assistente AI dovrebbe rispondere! 🎉

## 🔧 Sviluppo Locale

Per testare in locale prima del deploy:

```bash
cd app

# Installa dipendenze
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copia .env
cp .env.example .env
# Edita .env con le tue keys

# Avvia Redis locale
docker run -d -p 6379:6379 redis:7-alpine

# Avvia l'app
python main.py

# In un altro terminale, avvia ngrok
ngrok http 8080

# Usa l'URL di ngrok come webhook in Twilio
```

Vedi `docs/development.md` per dettagli completi.

## 📊 Monitoring

### Logs
```bash
kubectl logs -f -n voice-ai -l app=voice-assistant
```

### Metriche Prometheus
```bash
kubectl port-forward -n voice-ai svc/voice-assistant 8080:80
curl http://localhost:8080/metrics
```

### Status
```bash
# Health check
curl https://voice-assistant.tuodominio.com/health

# Ready check
curl https://voice-assistant.tuodominio.com/ready
```

## 🎨 Personalizzazione

### Cambiare il messaggio iniziale

Edita `kubernetes/configmap.yaml`:
```yaml
INITIAL_MESSAGE: "Il tuo messaggio personalizzato!"
```

Oppure in `helm/voice-assistant/values.yaml`:
```yaml
config:
  initialMessage: "Il tuo messaggio personalizzato!"
```

### Cambiare il comportamento

Edita il system prompt in `config/assistant-config.yaml` o direttamente nel configmap.

### Cambiare la voce

Vedi le voci disponibili su ElevenLabs e cambia `ELEVENLABS_VOICE_ID` nel configmap.

## 📁 Struttura del Repository

```
ai-voice-assistant/
├── app/                    # Applicazione Python
│   ├── Dockerfile
│   ├── main.py            # FastAPI app
│   ├── requirements.txt
│   └── config/
├── kubernetes/            # Manifesti K8s raw
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── helm/                  # Helm chart
│   └── voice-assistant/
├── config/                # Configurazione assistente
├── scripts/               # Script utility
└── docs/                  # Documentazione
```

## 🆘 Troubleshooting

### Il pod non parte
```bash
kubectl describe pod -n voice-ai <pod-name>
kubectl logs -n voice-ai <pod-name>
```

### L'assistente non risponde
- Verifica che il webhook Twilio sia configurato correttamente
- Controlla i logs: `kubectl logs -f -n voice-ai -l app=voice-assistant`
- Verifica che tutte le API keys siano corrette

### Errori di API
- Controlla che le API keys siano valide
- Verifica i limiti di rate delle API
- Controlla i crediti nei vari servizi

## 📚 Documentazione Completa

- **README.md** - Overview generale
- **docs/development.md** - Guida sviluppo
- **config/assistant-config.yaml** - Configurazione assistente
- **helm/voice-assistant/values.yaml** - Configurazione Helm

## 🔐 Sicurezza

⚠️ **IMPORTANTE**:
- NON committare mai `secrets.yaml` nel repository
- Usa secret management (AWS Secrets Manager, Vault, etc) in production
- Abilita TLS/HTTPS per tutti i webhook
- Monitora l'uso delle API per evitare costi inattesi

## 💰 Costi Stimati

Per 100 chiamate al mese (~5 min ciascuna):
- Twilio: ~$25-50/mese (varia per paese)
- OpenAI GPT-4: ~$10-20/mese
- Deepgram: ~$5-10/mese
- ElevenLabs: ~$5-22/mese (dipende dal piano)
- **Totale stimato: $45-100/mese**

## 🚀 Next Steps

1. ✅ Deploy base completato
2. 📱 Testa con chiamate reali
3. 🎨 Personalizza messaggio e comportamento
4. 📊 Setup monitoring (Grafana dashboard)
5. 🔄 Setup CI/CD per deploy automatici
6. 📈 Scala in base al traffico
7. 🎯 Aggiungi funzionalità custom (calendario, CRM, etc)

## 💡 Idee per Estensioni Future

- Integrazione con Google Calendar per appuntamenti
- Connessione a CRM (Salesforce, HubSpot)
- Call recording e trascrizioni automatiche
- Analytics dashboard personalizzata
- Multi-lingua support
- Sentiment analysis
- A/B testing per prompt optimization

## 📞 Supporto

Per domande o problemi:
- Consulta `docs/development.md`
- Apri una issue su GitHub
- Email: infrastructure@technacy.it

---

**Creato con ❤️ per Technacy Milano - Infrastructure Team**

Buon lavoro! 🎉
