from pydantic import BaseModel
from typing import Optional


class UserRequest(BaseModel):
    intent: str = "unknown"

    source: Optional[str] = None
    destination: Optional[str] = None

    city: Optional[str] = None

    budget: Optional[int] = None

    days: Optional[int] = None

    mood: Optional[str] = None

    preference: Optional[str] = None