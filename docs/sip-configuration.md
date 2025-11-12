# Guida Configurazione SIP

Questa guida spiega come configurare l'AI Voice Assistant con un account SIP al posto di Twilio.

## 🎯 Vantaggi dell'uso di SIP

- **Flessibilità**: Usa qualsiasi provider VoIP
- **Costi**: Spesso più economico di Twilio
- **Integrazione**: Connetti con PBX aziendale esistente
- **Portabilità**: Porta il tuo numero esistente
- **Privacy**: Mantieni tutto on-premise se necessario

## 📋 Prerequisiti

### 1. Account SIP
Hai bisogno di un account SIP con:
- Server SIP address (es: `sip.provider.com`)
- Username
- Password
- Domain/Realm
- Extension (opzionale)

### 2. Connettività
- Porta 5060 (UDP) o 5061 (TLS) aperta
- STUN server per NAT traversal
- Opzionale: TURN server per relay

### 3. WebRTC Support
Il tuo server SIP deve supportare WebRTC:
- Codec: Opus, G.711
- Transport: WSS (WebSocket Secure)
- ICE, STUN, TURN

## 🔧 Setup Passo-Passo

### Passo 1: Ottieni Credenziali SIP

#### Opzione A: Provider Cloud (es. Twilio SIP)
```bash
# Twilio supporta anche SIP!
SIP_SERVER=sip.twilio.com
SIP_USERNAME=<your-twilio-sip-username>
SIP_PASSWORD=<your-twilio-sip-password>
SIP_DOMAIN=sip.twilio.com
```

#### Opzione B: 3CX
```bash
SIP_SERVER=your-3cx-server.com
SIP_PORT=5060
SIP_USERNAME=extension_number
SIP_PASSWORD=extension_password
SIP_DOMAIN=your-3cx-server.com
SIP_EXTENSION=100
```

#### Opzione C: FreePBX / Asterisk
```bash
SIP_SERVER=your-asterisk-server.com
SIP_PORT=5060
SIP_USERNAME=asterisk_user
SIP_PASSWORD=asterisk_pass
SIP_DOMAIN=your-asterisk-server.com
```

### Passo 2: Configurazione Secrets

Edita `kubernetes/secrets/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: voice-assistant-secrets
  namespace: voice-ai
type: Opaque
stringData:
  # Telephony Provider
  TELEPHONY_PROVIDER: "sip"
  
  # SIP Configuration
  SIP_SERVER: "sip.yourdomain.com"
  SIP_PORT: "5060"
  SIP_USERNAME: "your_username"
  SIP_PASSWORD: "your_password"
  SIP_DOMAIN: "yourdomain.com"
  SIP_EXTENSION: "1000"  # opzionale
  SIP_TRANSPORT: "udp"  # o tcp, tls
  
  # STUN/TURN (per NAT traversal)
  SIP_STUN_SERVER: "stun:stun.l.google.com:19302"
  # SIP_TURN_SERVER: "turn:turn.example.com:3478"
  
  # API Keys (sempre necessarie)
  OPENAI_API_KEY: "sk-xxx"
  DEEPGRAM_API_KEY: "xxx"
  ELEVENLABS_API_KEY: "xxx"
```

### Passo 3: Configurazione Server SIP

#### Per 3CX

1. Vai su **Extensions**
2. Crea nuova extension per l'AI assistant
3. Abilita **WebRTC** nell'extension
4. Configura **Outbound rules** se necessario
5. Nota le credenziali

#### Per FreePBX

1. Vai su **Applications** → **Extensions**
2. Crea **PJSIP Extension**
3. Imposta:
   - Extension Number
   - Display Name: "AI Voice Assistant"
   - Secret/Password
4. In **Advanced**:
   - WebRTC: Yes
   - Encryption: Enabled
5. Apply Config

#### Per Asterisk (manuale)

Edita `/etc/asterisk/pjsip.conf`:

```ini
[voice-assistant]
type=endpoint
context=from-internal
disallow=all
allow=opus
allow=ulaw
webrtc=yes
transport=transport-wss
auth=voice-assistant
aors=voice-assistant

[voice-assistant]
type=auth
auth_type=userpass
password=your_secure_password
username=voice-assistant

[voice-assistant]
type=aor
max_contacts=5
```

### Passo 4: Test Connettività

Test registrazione SIP:

```bash
# Deploy l'applicazione
kubectl apply -f kubernetes/

# Verifica logs
kubectl logs -f -n voice-ai -l app=voice-assistant

# Dovresti vedere:
# "SIP registration successful"

# Check status via API
curl https://your-domain.com/sip/status
```

Output atteso:
```json
{
  "status": "connected",
  "sip_server": "sip.yourdomain.com",
  "sip_username": "voice-assistant",
  "active_calls": 0,
  "calls": []
}
```

### Passo 5: Configurazione Routing Chiamate

#### Su 3CX

1. Vai su **Call Routing**
2. Crea **Inbound Rule**:
   - DID/Extension: Il tuo numero
   - Destination: Extension "AI Voice Assistant"
3. Salva

#### Su FreePBX

1. Vai su **Connectivity** → **Inbound Routes**
2. Crea nuova route:
   - DID Number: Il tuo numero
   - Set Destination: Extension → AI Voice Assistant
3. Submit

#### Su Asterisk

Edita `/etc/asterisk/extensions.conf`:

```ini
[from-trunk]
exten => YOUR_DID,1,NoOp(Incoming call for AI Assistant)
same => n,Answer()
same => n,Wait(1)
same => n,Dial(PJSIP/voice-assistant)
same => n,Hangup()
```

## 🧪 Testing

### Test 1: Registrazione SIP

```bash
# Check SIP registration
kubectl exec -it -n voice-ai <pod-name> -- curl localhost:8080/sip/status
```

### Test 2: Chiamata di Test

1. Da un telefono, chiama l'extension/DID configurato
2. L'AI assistant dovrebbe rispondere
3. Verifica logs:

```bash
kubectl logs -f -n voice-ai -l app=voice-assistant | grep SIP
```

### Test 3: Qualità Audio

Fai una chiamata e verifica:
- [ ] Audio chiaro in entrambe le direzioni
- [ ] Latenza accettabile (< 500ms)
- [ ] Nessun echo o feedback
- [ ] Riconoscimento vocale accurato

## 🔧 Troubleshooting

### Problema: Registrazione SIP Fallisce

**Sintomi**: Logs mostrano "SIP registration failed"

**Soluzioni**:
1. Verifica username/password corretti
2. Check porta 5060 aperta nel firewall
3. Verifica che il server SIP sia raggiungibile:
   ```bash
   nslookup sip.yourdomain.com
   telnet sip.yourdomain.com 5060
   ```

### Problema: Audio Non Funziona

**Sintomi**: Chiamata connessa ma nessun audio

**Soluzioni**:
1. Verifica codec supportati (Opus preferito)
2. Check STUN server configurato correttamente
3. Verifica porte RTP aperte (tipicamente 10000-20000)
4. Prova con TURN server se dietro NAT complesso

### Problema: Echo o Feedback

**Sintomi**: Senti la tua voce ripetuta

**Soluzioni**:
1. Abilita echo cancellation sul server SIP
2. Riduci livelli audio
3. Verifica configurazione codec

### Problema: Alta Latenza

**Sintomi**: Ritardo > 1 secondo nelle risposte

**Soluzioni**:
1. Usa server SIP geograficamente vicino
2. Verifica rete Kubernetes non congestiona
3. Check latenza componenti AI (GPT-4, Deepgram, ElevenLabs)
4. Considera usare Redis per caching

## 📊 Monitoraggio

### Metriche Prometheus

```promql
# Chiamate SIP totali
voice_assistant_calls_total{provider="sip"}

# Durata chiamate SIP
voice_assistant_call_duration_seconds{provider="sip"}

# Errori SIP
voice_assistant_errors_total{error_type="sip_handler"}
```

### Grafana Dashboard

Query utili:
```promql
# Success rate chiamate SIP
sum(rate(voice_assistant_calls_total{provider="sip",status="success"}[5m])) 
/ 
sum(rate(voice_assistant_calls_total{provider="sip"}[5m]))

# Latenza media risposta
rate(voice_assistant_call_duration_seconds_sum[5m]) 
/ 
rate(voice_assistant_call_duration_seconds_count[5m])
```

## 🔒 Sicurezza

### Best Practices

1. **Usa TLS Transport**
   ```yaml
   SIP_TRANSPORT: "tls"
   ```

2. **Password Forti**
   - Minimo 16 caratteri
   - Lettere, numeri, simboli

3. **Firewall Rules**
   ```bash
   # Permetti solo IP server SIP
   iptables -A INPUT -p udp --dport 5060 -s SIP_SERVER_IP -j ACCEPT
   iptables -A INPUT -p udp --dport 5060 -j DROP
   ```

4. **SRTP per Media Encryption**
   ```yaml
   # Nel server SIP
   encryption=yes
   media_encryption=sdes
   ```

5. **Monitoring e Alerting**
   - Alert su fallimenti registrazione
   - Monitoring chiamate anomale
   - Rate limiting

## 💡 Suggerimenti Avanzati

### 1. Load Balancing

Per alta disponibilità, usa più instance:

```yaml
# In helm values
replicaCount: 3

sip:
  registration_retry: 5
  heartbeat_interval: 30
```

### 2. Failover Automatico

Configura fallback a Twilio se SIP non disponibile:

```yaml
TELEPHONY_PROVIDER: "sip"
TELEPHONY_FALLBACK: "twilio"
TWILIO_ACCOUNT_SID: "ACxxx"  # per fallback
```

### 3. Call Recording

Abilita recording per compliance:

```yaml
SIP_RECORD_CALLS: "true"
SIP_RECORDING_PATH: "/var/spool/recordings"
```

### 4. Multi-Tenant

Supporta più account SIP:

```yaml
SIP_ACCOUNTS: |
  - username: tenant1
    password: pass1
    extension: 100
  - username: tenant2
    password: pass2
    extension: 200
```

## 📚 Risorse

- **SIP RFC**: https://www.rfc-editor.org/rfc/rfc3261
- **WebRTC**: https://webrtc.org/
- **PJSIP**: https://www.pjsip.org/
- **Asterisk**: https://www.asterisk.org/
- **3CX**: https://www.3cx.com/

## 🆘 Supporto

Per problemi specifici SIP:
- Apri issue: https://github.com/vfoschi/ai-voice-assistant/issues
- Email: vittorio.foschi@technacy.it
- Tag: `sip-configuration`

---

**Nota**: Il supporto SIP richiede configurazione più complessa di Twilio ma offre maggiore flessibilità e controllo.
