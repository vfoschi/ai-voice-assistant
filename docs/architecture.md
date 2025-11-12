# Architettura del Sistema

## Overview

L'AI Voice Assistant è un sistema distribuito cloud-native che gestisce chiamate telefoniche attraverso l'integrazione di diversi servizi AI e piattaforme di comunicazione.

## Diagramma Architettura

```
┌──────────────────────────────────────────────────────────────────┐
│                         INTERNET                                  │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │  Chiamata da   │
        │  Utente Finale │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │     TWILIO     │  ◄── Provider Telefonia
        │  Voice Gateway │      (Gestisce SIP/WebRTC)
        └────────┬───────┘
                 │ HTTP Webhook
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                         │
│                                                                 │
│  ┌──────────────┐                                              │
│  │   Ingress    │  ◄── TLS/HTTPS                              │
│  │  Controller  │      (nginx/cert-manager)                    │
│  └──────┬───────┘                                              │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────┐             │
│  │         Voice Assistant Service              │             │
│  │         (LoadBalancer/ClusterIP)             │             │
│  └──────────────┬───────────────────────────────┘             │
│                 │                                               │
│                 ▼                                               │
│  ┌──────────────────────────────────────────────────┐         │
│  │    Voice Assistant Pods (FastAPI + Vocode)       │         │
│  │                                                   │         │
│  │  ┌────────────────────────────────────────┐     │         │
│  │  │  1. Riceve webhook da Twilio           │     │         │
│  │  │  2. Gestisce WebSocket per audio       │     │         │
│  │  │  3. Coordina flusso conversazione      │     │         │
│  │  └────────────────────────────────────────┘     │         │
│  │                                                   │         │
│  │  Replica 1    Replica 2    Replica N             │         │
│  └───────┬──────────┬──────────────┬────────────────┘         │
│          │          │              │                            │
│          │          └──────┬───────┘                           │
│          │                 │                                    │
│          ▼                 ▼                                    │
│  ┌──────────────┐  ┌─────────────┐                           │
│  │    Redis     │  │  PostgreSQL │  ◄── Storage (opzionale)  │
│  │    Cache     │  │   Database  │                            │
│  └──────────────┘  └─────────────┘                           │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
         │                 │                │
         │ API Calls       │ API Calls      │ API Calls
         ▼                 ▼                ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│  Deepgram   │   │    OpenAI    │   │ ElevenLabs  │
│    (STT)    │   │    (LLM)     │   │    (TTS)    │
│             │   │              │   │             │
│ Speech-to-  │   │    GPT-4     │   │  Text-to-   │
│    Text     │   │ Conversation │   │   Speech    │
└─────────────┘   └──────────────┘   └─────────────┘
```

## Flusso della Chiamata

### 1. Inizio Chiamata
```
Utente chiama → Twilio → Webhook a K8s Ingress → Voice Assistant Pod
```

### 2. Conversazione
```
┌──────────────────────────────────────────────────────────┐
│                  Ciclo Conversazione                      │
│                                                           │
│  Audio Utente (Twilio) → WebSocket → Vocode             │
│         ↓                                                 │
│  Deepgram STT → Testo                                    │
│         ↓                                                 │
│  OpenAI GPT-4 → Risposta intelligente                   │
│         ↓                                                 │
│  ElevenLabs TTS → Audio                                  │
│         ↓                                                 │
│  WebSocket → Twilio → Audio a Utente                    │
│                                                           │
│  [Ripete fino a fine chiamata]                          │
└──────────────────────────────────────────────────────────┘
```

### 3. Fine Chiamata
```
Utente termina → Twilio notifica → Cleanup sessione → Salva logs/metriche
```

## Componenti Dettagliati

### 1. FastAPI Application

**Responsabilità:**
- Gestione webhook Twilio
- Coordinamento componenti Vocode
- Health checks e monitoring
- Logging e metrics

**Endpoints principali:**
- `POST /webhooks/twilio/voice` - Riceve chiamate
- `POST /webhooks/twilio/status` - Status updates
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /metrics` - Prometheus metrics

### 2. Vocode Core

**Componenti:**
- **TelephonyServer**: Gestisce integrazione Twilio
- **StreamingConversation**: Coordina flusso audio/conversazione
- **TranscriberConfig**: Configurazione STT
- **AgentConfig**: Configurazione LLM
- **SynthesizerConfig**: Configurazione TTS

### 3. Servizi Esterni

#### Twilio
- **Ruolo**: Gateway telefonia
- **Funzioni**: 
  - Gestione chiamate PSTN/VoIP
  - WebSocket per streaming audio
  - Callback per status

#### Deepgram
- **Ruolo**: Speech-to-Text
- **Modello**: Nova-2
- **Latenza**: ~300-500ms
- **Supporto**: Italiano nativo

#### OpenAI
- **Ruolo**: Language Model
- **Modello**: GPT-4
- **Funzioni**:
  - Comprensione intent
  - Generazione risposte
  - Gestione contesto

#### ElevenLabs
- **Ruolo**: Text-to-Speech
- **Voci**: Multilingual v2
- **Qualità**: Near-human
- **Latenza**: ~200-400ms

### 4. Storage Layer

#### Redis (Opzionale)
- **Ruolo**: Cache e sessioni
- **Uso**:
  - Cache risposte LLM
  - Gestione stato conversazioni
  - Rate limiting

#### PostgreSQL (Opzionale)
- **Ruolo**: Database persistente
- **Uso**:
  - Logging chiamate
  - Analytics
  - Audit trail

## Scalabilità

### Scalabilità Orizzontale

```
Traffic basso:  [Pod 1] [Pod 2]
                    ↓
Traffic medio:  [Pod 1] [Pod 2] [Pod 3] [Pod 4]
                    ↓
Traffic alto:   [Pod 1...Pod 10]
```

**HorizontalPodAutoscaler:**
- Min replicas: 2
- Max replicas: 10
- Target CPU: 80%
- Target Memory: 80%

### Scalabilità dei Provider

| Provider | Chiamate Simultanee | Latenza | Rate Limits |
|----------|-------------------|---------|-------------|
| Twilio | 1000+ | ~50ms | Per account |
| Deepgram | 1000+ | ~300ms | Per minuto |
| OpenAI | 3000+ | ~1-2s | Per minuto |
| ElevenLabs | 50-500 | ~400ms | Per piano |

## High Availability

### Pod Replica
- Minimo 2 repliche sempre attive
- Anti-affinity per distribuzione su nodi diversi
- Rolling updates senza downtime

### Health Checks
```yaml
livenessProbe:
  httpGet:
    path: /health
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
  initialDelaySeconds: 10
  periodSeconds: 5
```

### Session Affinity
- ClientIP session affinity per WebSocket
- Timeout: 3 ore (per chiamate lunghe)

## Sicurezza

### Network Security
```
Internet → TLS/HTTPS → Ingress → mTLS → Services
```

### Secrets Management
- Kubernetes Secrets per API keys
- External secrets (AWS/GCP/Azure) consigliato per production
- No secrets in code o ConfigMaps

### Pod Security
- Non-root user (UID 1000)
- Read-only root filesystem
- Capability dropping
- Security Context constraints

## Monitoring & Observability

### Metriche Prometheus

```python
# Esempio metriche esposte
voice_assistant_calls_total{status="success"}
voice_assistant_calls_total{status="failed"}
voice_assistant_call_duration_seconds_bucket
voice_assistant_errors_total{error_type="twilio"}
voice_assistant_errors_total{error_type="openai"}
```

### Logging

Formato JSON strutturato:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "call_sid": "CAxxxx",
  "from": "+39xxxxxxx",
  "event": "call_started",
  "duration": null
}
```

### Tracing (Futuro)

Possibile integrazione con:
- Jaeger
- Zipkin
- OpenTelemetry

## Performance

### Latenze Target

| Componente | Target | Tipico |
|------------|--------|--------|
| Webhook response | <500ms | ~200ms |
| STT (Deepgram) | <500ms | ~300ms |
| LLM (GPT-4) | <2s | ~1.5s |
| TTS (ElevenLabs) | <500ms | ~400ms |
| **Totale round-trip** | **<3.5s** | **~2.5s** |

### Ottimizzazioni

1. **Streaming**: Audio streaming per ridurre latenza percepita
2. **Caching**: Redis per risposte comuni
3. **Parallel Processing**: STT e preparazione LLM in parallelo
4. **Connection Pooling**: Riuso connessioni HTTP

## Disaster Recovery

### Backup
- Secrets backup in secret manager esterno
- ConfigMaps versionati in Git
- Database backup (se usato) ogni 24h

### Recovery
- Infrastructure as Code (tutto in Git)
- Re-deploy automatico da CI/CD
- RTO (Recovery Time Objective): <5 minuti
- RPO (Recovery Point Objective): <1 ora

## Costi Operativi

### Kubernetes
- 2 pods × 0.5 CPU × $0.04/h = **$1.4/giorno**
- 2 pods × 512MB RAM × $0.005/h = **$0.24/giorno**

### Servizi Esterni (per 1000 chiamate/mese @ 5min)
- Twilio: **~$250/mese**
- OpenAI: **~$100/mese**
- Deepgram: **~$50/mese**
- ElevenLabs: **~$99/mese**

**Totale stimato: ~$550/mese** per 1000 chiamate

## Limiti e Considerazioni

### Limiti Tecnici
- Max durata chiamata: 10 minuti (configurabile)
- Max chiamate simultanee: Limitato da ElevenLabs tier
- Latenza totale: 2-3 secondi per risposta

### Considerazioni GDPR
- Registrazione chiamate: OFF di default
- Trascrizioni: Salvate se abilitato
- Retention: 90 giorni default
- Diritto cancellazione: Implementare API per GDPR requests

## Roadmap Tecnica

### Q1 2025
- [x] MVP con Vocode
- [ ] Monitoring dashboard Grafana
- [ ] Call recording opzionale

### Q2 2025
- [ ] Multi-tenant support
- [ ] Advanced analytics
- [ ] A/B testing framework

### Q3 2025
- [ ] Custom voice training
- [ ] Multi-language auto-detection
- [ ] Calendar integration

### Q4 2025
- [ ] CRM integrations
- [ ] Real-time sentiment analysis
- [ ] Automated quality scoring
