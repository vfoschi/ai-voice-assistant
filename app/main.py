#!/usr/bin/env python3
"""
AI Voice Assistant - Main Application
Gestisce chiamate telefoniche in entrata tramite Twilio o SIP con Vocode
"""

import os
import logging
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from twilio.twiml.voice_response import VoiceResponse

import vocode
from vocode.streaming.telephony.server.base import TelephonyServer
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig

from config.settings import Settings
from handlers.call_handler import CallHandler
from handlers.sip_handler import initialize_sip_handler, get_sip_handler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
CALLS_TOTAL = Counter('voice_assistant_calls_total', 'Total number of calls handled')
CALLS_DURATION = Histogram('voice_assistant_call_duration_seconds', 'Call duration in seconds')
ERRORS_TOTAL = Counter('voice_assistant_errors_total', 'Total number of errors', ['error_type'])

# Load settings
settings = Settings()

# Configure Vocode with API keys
vocode.api_key = settings.vocode_api_key if hasattr(settings, 'vocode_api_key') else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    logger.info("Starting AI Voice Assistant...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Telephony Provider: {settings.telephony_provider}")
    
    # Initialize Redis config manager if Redis is configured
    if settings.redis_url:
        app.state.config_manager = RedisConfigManager(redis_url=settings.redis_url)
        logger.info("Redis config manager initialized")
    
    # Initialize telephony based on provider selection
    if settings.telephony_provider == "twilio":
        # Initialize Twilio telephony server
        app.state.telephony_server = TelephonyServer(
            base_url=settings.base_url,
            config_manager=app.state.config_manager if hasattr(app.state, 'config_manager') else None,
            twilio_config=TwilioConfig(
                account_sid=settings.twilio_account_sid,
                auth_token=settings.twilio_auth_token,
            ),
            agent_config=ChatGPTAgentConfig(
                openai_api_key=settings.openai_api_key,
                initial_message=BaseMessage(text=settings.initial_message),
                prompt_preamble=settings.system_prompt,
                model_name=settings.openai_model,
            ),
            transcriber_config=DeepgramTranscriberConfig(
                api_key=settings.deepgram_api_key,
                language="it",  # Italiano
                model="nova-2",
            ),
            synthesizer_config=ElevenLabsSynthesizerConfig(
                api_key=settings.elevenlabs_api_key,
                voice_id=settings.elevenlabs_voice_id,
                model_id="eleven_multilingual_v2",
            ),
        )
        logger.info("Twilio telephony server initialized")
        logger.info(f"Twilio Webhook URL: {settings.base_url}/webhooks/twilio/voice")
        
    elif settings.telephony_provider == "sip":
        # Initialize SIP handler
        app.state.sip_handler = initialize_sip_handler(
            sip_server=settings.sip_server,
            sip_username=settings.sip_username,
            sip_password=settings.sip_password,
            sip_domain=settings.sip_domain,
            sip_port=settings.sip_port,
            sip_transport=settings.sip_transport,
            stun_server=settings.sip_stun_server,
            turn_server=settings.sip_turn_server,
        )
        
        # Register with SIP server
        if await app.state.sip_handler.register():
            logger.info("SIP handler initialized and registered")
            logger.info(f"SIP Server: {settings.sip_server}:{settings.sip_port}")
            logger.info(f"SIP WebRTC endpoint: {settings.base_url}/webhooks/sip/webrtc")
        else:
            logger.error("Failed to register with SIP server")
    else:
        logger.error(f"Unknown telephony provider: {settings.telephony_provider}")
        raise ValueError(f"Invalid telephony_provider: {settings.telephony_provider}")
    
    
    yield
    
    logger.info("Shutting down AI Voice Assistant...")


# Create FastAPI app
app = FastAPI(
    title="AI Voice Assistant",
    description="Assistente vocale AI per gestione chiamate telefoniche",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Voice Assistant",
        "version": "1.0.0",
        "status": "running",
        "webhook": f"{settings.base_url}/webhooks/twilio/voice"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes"""
    # Check if critical services are available
    checks = {
        "openai": bool(settings.openai_api_key),
        "deepgram": bool(settings.deepgram_api_key),
        "elevenlabs": bool(settings.elevenlabs_api_key),
        "twilio": bool(settings.twilio_account_sid and settings.twilio_auth_token),
    }
    
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/webhooks/twilio/voice")
async def handle_twilio_voice(request: Request):
    """
    Webhook handler for Twilio voice calls
    Questo endpoint viene chiamato da Twilio quando arriva una chiamata
    """
    try:
        CALLS_TOTAL.inc()
        logger.info("Received incoming call from Twilio")
        
        # Get form data from Twilio
        form_data = await request.form()
        from_number = form_data.get("From", "Unknown")
        to_number = form_data.get("To", "Unknown")
        call_sid = form_data.get("CallSid", "Unknown")
        
        logger.info(f"Call details - From: {from_number}, To: {to_number}, SID: {call_sid}")
        
        # Use Vocode's telephony server to handle the call
        if hasattr(app.state, 'telephony_server'):
            # The telephony server will handle the WebSocket connection
            # and manage the conversation flow
            response = await app.state.telephony_server.handle_inbound_call(request)
            return response
        else:
            # Fallback if telephony server not initialized
            logger.error("Telephony server not initialized")
            response = VoiceResponse()
            response.say(
                "Mi dispiace, il servizio non è al momento disponibile. Riprova più tardi.",
                language="it-IT"
            )
            return PlainTextResponse(str(response), media_type="text/xml")
            
    except Exception as e:
        logger.error(f"Error handling Twilio call: {e}", exc_info=True)
        ERRORS_TOTAL.labels(error_type="twilio_handler").inc()
        
        # Return error response to Twilio
        response = VoiceResponse()
        response.say(
            "Si è verificato un errore. Per favore riprova più tardi.",
            language="it-IT"
        )
        return PlainTextResponse(str(response), media_type="text/xml")


@app.post("/webhooks/twilio/status")
async def handle_twilio_status(request: Request):
    """
    Webhook handler for Twilio call status updates
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "Unknown")
        call_status = form_data.get("CallStatus", "Unknown")
        
        logger.info(f"Call status update - SID: {call_sid}, Status: {call_status}")
        
        if call_status in ["completed", "failed", "busy", "no-answer"]:
            duration = form_data.get("CallDuration", "0")
            logger.info(f"Call {call_sid} ended with status {call_status}, duration: {duration}s")
            
            if duration and duration.isdigit():
                CALLS_DURATION.observe(float(duration))
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error handling status callback: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@app.get("/config")
async def get_config():
    """
    Get current configuration (sanitized - no secrets)
    """
    return {
        "environment": settings.environment,
        "telephony_provider": settings.telephony_provider,
        "base_url": settings.base_url,
        "initial_message": settings.initial_message,
        "openai_model": settings.openai_model,
        "elevenlabs_voice": settings.elevenlabs_voice_id,
    }


@app.post("/webhooks/sip/webrtc")
async def handle_sip_webrtc(request: Request):
    """
    WebRTC signaling endpoint for SIP calls
    Handles SIP INVITE and media negotiation
    """
    if settings.telephony_provider != "sip":
        raise HTTPException(status_code=400, detail="SIP provider not configured")
    
    try:
        CALLS_TOTAL.inc()
        data = await request.json()
        
        call_id = data.get("call_id")
        from_uri = data.get("from")
        to_uri = data.get("to")
        sdp_offer = data.get("sdp")
        
        logger.info(f"SIP WebRTC call - ID: {call_id}, From: {from_uri}, To: {to_uri}")
        
        sip_handler = get_sip_handler()
        if not sip_handler:
            raise HTTPException(status_code=500, detail="SIP handler not initialized")
        
        # Handle the call
        result = await sip_handler.handle_incoming_call(
            call_id=call_id,
            from_uri=from_uri,
            to_uri=to_uri,
            sdp_offer=sdp_offer,
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error handling SIP WebRTC call: {e}", exc_info=True)
        ERRORS_TOTAL.labels(error_type="sip_handler").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sip/status")
async def get_sip_status():
    """
    Get SIP connection status and active calls
    """
    if settings.telephony_provider != "sip":
        return {"provider": settings.telephony_provider, "sip_enabled": False}
    
    sip_handler = get_sip_handler()
    if not sip_handler:
        return {"status": "not_initialized"}
    
    active_calls = await sip_handler.get_active_calls()
    
    return {
        "status": "connected",
        "sip_server": settings.sip_server,
        "sip_username": settings.sip_username,
        "active_calls": len(active_calls),
        "calls": list(active_calls.keys()),
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        log_level="info",
        access_log=True,
    )
