"""
SIP Handler - Gestione chiamate SIP con WebRTC
Supporta chiamate VoIP tramite account SIP standard
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

import vocode
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig

logger = logging.getLogger(__name__)


class SIPHandler:
    """Gestisce le chiamate SIP con WebRTC"""
    
    def __init__(
        self,
        sip_server: str,
        sip_username: str,
        sip_password: str,
        sip_domain: str,
        sip_port: int = 5060,
        sip_transport: str = "udp",
        stun_server: Optional[str] = None,
        turn_server: Optional[str] = None,
    ):
        self.sip_server = sip_server
        self.sip_username = sip_username
        self.sip_password = sip_password
        self.sip_domain = sip_domain
        self.sip_port = sip_port
        self.sip_transport = sip_transport
        self.stun_server = stun_server or "stun:stun.l.google.com:19302"
        self.turn_server = turn_server
        
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.registered = False
        
        logger.info(f"SIPHandler initialized for {sip_username}@{sip_server}")
    
    async def register(self) -> bool:
        """
        Registra l'account SIP con il server
        """
        try:
            # Simula registrazione SIP
            # In produzione, usare una libreria SIP come pjsua o aiortc
            logger.info(f"Attempting SIP registration: {self.sip_username}@{self.sip_server}")
            
            # TODO: Implementare registrazione SIP reale
            # Per ora, simuliamo successo
            self.registered = True
            logger.info("SIP registration successful")
            return True
            
        except Exception as e:
            logger.error(f"SIP registration failed: {e}", exc_info=True)
            self.registered = False
            return False
    
    async def handle_incoming_call(
        self,
        call_id: str,
        from_uri: str,
        to_uri: str,
        sdp_offer: str,
    ) -> Dict[str, Any]:
        """
        Gestisce una chiamata SIP in entrata
        
        Args:
            call_id: ID univoco della chiamata
            from_uri: SIP URI del chiamante
            to_uri: SIP URI del chiamato
            sdp_offer: SDP offer per negoziazione media
            
        Returns:
            Dict con SDP answer e dettagli chiamata
        """
        try:
            logger.info(f"Handling incoming SIP call {call_id} from {from_uri}")
            
            # Crea info chiamata
            call_info = {
                "call_id": call_id,
                "from_uri": from_uri,
                "to_uri": to_uri,
                "start_time": datetime.utcnow(),
                "status": "active",
            }
            
            self.active_calls[call_id] = call_info
            
            # TODO: Implementare negoziazione WebRTC reale con aiortc
            # Per ora, restituiamo un SDP answer di esempio
            sdp_answer = self._generate_sdp_answer(sdp_offer)
            
            return {
                "status": "success",
                "call_id": call_id,
                "sdp_answer": sdp_answer,
                "message": "Call accepted",
            }
            
        except Exception as e:
            logger.error(f"Error handling SIP call {call_id}: {e}", exc_info=True)
            return {
                "status": "error",
                "call_id": call_id,
                "error": str(e),
            }
    
    def _generate_sdp_answer(self, sdp_offer: str) -> str:
        """
        Genera un SDP answer basato sull'offer ricevuto
        
        In produzione, questo dovrebbe usare aiortc o simili per
        gestire correttamente la negoziazione WebRTC
        """
        # Placeholder SDP answer
        sdp_answer = """v=0
o=- 0 0 IN IP4 0.0.0.0
s=Voice Assistant
c=IN IP4 0.0.0.0
t=0 0
m=audio 9 UDP/TLS/RTP/SAVPF 111 103 104
a=rtpmap:111 opus/48000/2
a=fmtp:111 minptime=10;useinbandfec=1
a=rtcp-fb:111 transport-cc
a=sendrecv
a=ice-ufrag:{}
a=ice-pwd:{}
a=fingerprint:sha-256 {}
a=setup:active
a=mid:0
""".format(
            uuid.uuid4().hex[:8],
            uuid.uuid4().hex,
            ":".join([uuid.uuid4().hex[i:i+2].upper() for i in range(0, 64, 2)])
        )
        return sdp_answer
    
    async def end_call(self, call_id: str) -> bool:
        """
        Termina una chiamata SIP
        """
        if call_id in self.active_calls:
            call_info = self.active_calls[call_id]
            call_info["end_time"] = datetime.utcnow()
            call_info["status"] = "completed"
            
            duration = (call_info["end_time"] - call_info["start_time"]).total_seconds()
            call_info["duration"] = duration
            
            logger.info(f"Ended SIP call {call_id}, duration: {duration}s")
            del self.active_calls[call_id]
            return True
        
        return False
    
    async def get_active_calls(self) -> Dict[str, Dict[str, Any]]:
        """
        Ritorna tutte le chiamate attive
        """
        return self.active_calls


# Global SIP handler instance
_sip_handler: Optional[SIPHandler] = None


def initialize_sip_handler(**kwargs) -> SIPHandler:
    """
    Inizializza il SIP handler globale
    """
    global _sip_handler
    _sip_handler = SIPHandler(**kwargs)
    return _sip_handler


def get_sip_handler() -> Optional[SIPHandler]:
    """
    Ottiene l'istanza del SIP handler
    """
    return _sip_handler
