from pydantic import BaseModel
from typing import Optional


class UserQuery(BaseModel):
    query: str

class TripRequest(BaseModel):

    city: Optional[str] = None

    budget: Optional[int] = None

    mood: Optional[str] = None

    lat: Optional[float] = None

    lon: Optional[float] = None