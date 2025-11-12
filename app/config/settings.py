"""
Settings and configuration management using Pydantic Settings
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Server configuration
    base_url: str
    port: int = 8080
    
    # Twilio configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: Optional[str] = None
    
    # OpenAI configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Deepgram configuration (Speech-to-Text)
    deepgram_api_key: str
    
    # ElevenLabs configuration (Text-to-Speech)
    elevenlabs_api_key: str
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default: Rachel voice
    
    # Vocode configuration (optional)
    vocode_api_key: Optional[str] = None
    
    # Redis configuration (optional but recommended)
    redis_url: Optional[str] = None
    redis_password: Optional[str] = None
    
    # PostgreSQL configuration (optional)
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_db: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    
    # Assistant behavior
    initial_message: str = "Ciao! Sono il tuo assistente vocale. Come posso aiutarti?"
    system_prompt: str = """Sei un assistente vocale italiano cortese e professionale.
Rispondi in modo conciso e naturale. 
Se non sai rispondere a qualcosa, sii onesto e chiedi se puoi aiutare in altro modo.
Mantieni sempre un tono amichevole ma professionale."""
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    @property
    def postgres_url(self) -> Optional[str]:
        """Build PostgreSQL connection URL"""
        if all([self.postgres_host, self.postgres_db, self.postgres_user, self.postgres_password]):
            return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return None
