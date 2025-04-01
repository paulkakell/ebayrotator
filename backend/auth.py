from fastapi import Header, HTTPException, Depends
from app.config import get_settings

def verify_api_key(x_api_key: str = Header(...)):
    settings = get_settings()
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
