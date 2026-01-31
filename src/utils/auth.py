import hashlib
import hmac
import json
from urllib.parse import parse_qsl, parse_qs
from typing import Dict, Any, Optional
from fastapi import Header, HTTPException, status

from src.core.config import settings
from src.core.logger import app_logger

def validate_init_data(init_data: str, bot_token: str = settings.BOT_TOKEN) -> Optional[Dict[str, Any]]:
    """
    [LEGO BLOCK: SECURITY]
    Validates the `initData` string sent by Telegram Mini App.
    Returns the user data dict if valid, None otherwise.
    
    Ref: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        return None

    if "hash" not in parsed_data:
        return None

    received_hash = parsed_data.pop("hash")
    
    # Sort keys alphabetically
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
    
    # Calculate HMAC-SHA256
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if calculated_hash == received_hash:
        # Data is valid!
        # Parse the 'user' JSON string inside
        if "user" in parsed_data:
            return json.loads(parsed_data["user"])
        return parsed_data
    
    app_logger.warning("Invalid initData hash received!")
    return None

async def get_current_user(x_telegram_init_data: str = Header(None)):
    """
    [SECURITY LAYER] FastAPI Dependency.
    Validates the `X-Telegram-Init-Data` header.
    
    Usage:
        @router.post("/protected")
        def route(user_data = Depends(get_current_user)):
            ...
    
    Returns:
        dict: The parsed user data from initData.
    Raises:
        HTTPException: If validation fails (401).
    """
    if not x_telegram_init_data:
        # For Phase 4 Demo simplicity, if no header is present, we might return None.
        # But in Strict Mode, we raise 401.
        # Uncomment below to ENFORCE:
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Auth Header")
        return None
        
    user_data = validate_init_data(x_telegram_init_data, settings.BOT_TOKEN)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram Signature (Spoofing Detection)"
        )
    
    return user_data
