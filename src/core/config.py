from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application Configuration.
    Loads variables from .env file or environment.
    """
    # [Start] Telegram Config
    BOT_TOKEN: str # The Telegram Bot API Token
    
    # [Start] Database Config
    DATABASE_URL: str = "sqlite+aiosqlite:///./database.db" # Connection string
    ADMIN_IDS: list[int] = [] # List of hardcoded system admins
    
    # [Start] TON Blockchain Config
    TON_WALLET_ADDRESS: Optional[str] = None # Hot Wallet for receiving payments
    WALLET_MNEMONIC: Optional[str] = None # 24-word mnemonic for signing payout transactions
    
    # [Start] Lifecycle Config
    WEBHOOK_URL: Optional[str] = None # For production deployment
    WEBHOOK_PATH: str = "/webhook"
    
    # [Start] Debug
    DEBUG: bool = True # [DEBUG MODE] Set to True to see all logs
    
    # [SECURITY]: Admin key for destructive endpoints
    ADMIN_KEY: str = "change-me-in-env"
    
    # [Start] Ngrok
    NGROK_AUTHTOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
