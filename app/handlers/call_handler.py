"""
Call Handler - Logica di gestione delle chiamate
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CallHandler:
    """Gestisce la logica delle chiamate telefoniche"""
    
    def __init__(self):
        self.active_calls: Dict[str, Dict[str, Any]] = {}
    
    async def start_call(self, call_sid: str, from_number: str, to_number: str) -> Dict[str, Any]:
        """
        Inizia una nuova chiamata
        
        Args:
            call_sid: Twilio Call SID
            from_number: Numero chiamante
            to_number: Numero chiamato
            
        Returns:
            Dict con informazioni della chiamata
        """
        call_info = {
            "call_sid": call_sid,
            "from_number": from_number,
            "to_number": to_number,
            "start_time": datetime.utcnow(),
            "status": "active",
        }
        
        self.active_calls[call_sid] = call_info
        logger.info(f"Started call {call_sid} from {from_number}")
        
        return call_info
    
    async def end_call(self, call_sid: str, status: str = "completed") -> Optional[Dict[str, Any]]:
        """
        Termina una chiamata
        
        Args:
            call_sid: Twilio Call SID
            status: Stato finale della chiamata
            
        Returns:
            Dict con informazioni della chiamata completata
        """
        if call_sid in self.active_calls:
            call_info = self.active_calls[call_sid]
            call_info["end_time"] = datetime.utcnow()
            call_info["status"] = status
            
            # Calculate duration
            duration = (call_info["end_time"] - call_info["start_time"]).total_seconds()
            call_info["duration"] = duration
            
            logger.info(f"Ended call {call_sid} with status {status}, duration: {duration}s")
            
            # Remove from active calls
            del self.active_calls[call_sid]
            
            return call_info
        
        return None
    
    async def get_call_info(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """
        Ottiene informazioni su una chiamata attiva
        
        Args:
            call_sid: Twilio Call SID
            
        Returns:
            Dict con informazioni della chiamata o None
        """
        return self.active_calls.get(call_sid)
    
    def get_active_calls_count(self) -> int:
        """Ritorna il numero di chiamate attive"""
        return len(self.active_calls)


# Singleton instance
call_handler = CallHandler()
