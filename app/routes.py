import os
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

from travel_ai import TravelAI
from app.schemas import UserQuery
from services.places_service import PlacesService


# Load env
load_dotenv()

# Router
router = APIRouter()

# Services
places_service = PlacesService()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing")

ai = TravelAI(API_KEY)


# -----------------------------
# Schemas
# -----------------------------
class TripRequest(BaseModel):
    city: str
    budget: int
    mood: str


# -----------------------------
# AI Endpoints
# -----------------------------
@router.post("/process")
def process_query(data: UserQuery):
    return ai.process(data.query)


@router.post("/routes")
def routes_api(data: UserQuery):
    # 🎯 شغالة ومستقرة تماماً وبتنادي على الـ process اللي بيروح للـ RouteEngine الجديد
    return ai.process(data.query)


@router.post("/trips")
def trips_api(data: UserQuery):
    return ai.process(data.query)


@router.post("/recommendations")
def recommendation_api(data: UserQuery):
    return ai.process(data.query)


# -----------------------------
# Places APIs
# -----------------------------
@router.get("/places/{city}")
def get_places(city: str):
    return places_service.get_places(
        city=city,
        place_type="tourism",
        limit=20
    )


@router.get("/places/{city}/{place_type}")
def get_places_by_type(city: str, place_type: str):
    return places_service.get_places(
        city=city,
        place_type=place_type,
        limit=20
    )


# -----------------------------
# Trip Planner
# -----------------------------
@router.post("/trip-plan")
def generate_trip(request: TripRequest):
    return ai.trip_planner.create_trip(
        city=request.city,
        budget=request.budget,
        mood=request.mood,
        lat=None,
        lon=None
    )
@router.get("/poster/image")
def get_poster_image():
    file_path = "trip_poster.png"

    if not os.path.exists(file_path):
        return {"error": "poster not found"}

    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename="trip_poster.png"
    )