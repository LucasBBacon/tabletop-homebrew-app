# app/schemas/auth.py

from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    sub: Optional[str] = None
    
class TokenRefreshRequest(BaseModel):
    refresh_token: str
    
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'