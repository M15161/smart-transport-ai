# import os
# from dotenv import load_dotenv
# from fastapi import APIRouter
# from pydantic import BaseModel

# from travel_ai import TravelAI
# from app.schemas import UserQuery
# from services.places_service import PlacesService


# # Load env
# load_dotenv()

# # Router
# router = APIRouter()

# # Services
# places_service = PlacesService()

# API_KEY = os.getenv("GOOGLE_API_KEY")

# if not API_KEY:
#     raise RuntimeError("GOOGLE_API_KEY is missing")

# ai = TravelAI(API_KEY)


# # -----------------------------
# # Schemas
# # -----------------------------
# class TripRequest(BaseModel):
#     city: str
#     budget: int
#     mood: str


# # -----------------------------
# # AI Endpoints
# # -----------------------------
# @router.post("/process")
# def process_query(data: UserQuery):
#     return ai.process(data.query)


# @router.post("/routes")
# def routes_api(data: UserQuery):
#     # 🎯 شغالة ومستقرة تماماً وبتنادي على الـ process اللي بيروح للـ RouteEngine الجديد
#     return ai.process(data.query)


# @router.post("/trips")
# def trips_api(data: UserQuery):
#     return ai.process(data.query)


# @router.post("/recommendations")
# def recommendation_api(data: UserQuery):
#     return ai.process(data.query)


# # -----------------------------
# # Places APIs
# # -----------------------------
# @router.get("/places/{city}")
# def get_places(city: str):
#     return places_service.get_places(
#         city=city,
#         place_type="tourism",
#         limit=20
#     )


# @router.get("/places/{city}/{place_type}")
# def get_places_by_type(city: str, place_type: str):
#     return places_service.get_places(
#         city=city,
#         place_type=place_type,
#         limit=20
#     )


# # -----------------------------
# # Trip Planner
# # -----------------------------
# @router.post("/trip-plan")
# def generate_trip(request: TripRequest):
#     return ai.trip_planner.create_trip(
#         city=request.city,
#         budget=request.budget,
#         mood=request.mood,
#         lat=None,
#         lon=None
#     )

# import os
# import json
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional
# from dotenv import load_dotenv

# from travel_ai import TravelAI
# from app.schemas import UserQuery
# from services.places_service import PlacesService

# # استيراد الـ SDK الجديد الخاص بـ Gemini
# # from google import genai
# # from google.genai import types

# # Load env
# load_dotenv()

# # Router
# router = APIRouter()

# # Services
# places_service = PlacesService()

# API_KEY = os.getenv("GOOGLE_API_KEY")
# GEMINI_KEY = os.getenv("GEMINI_API_KEY") or API_KEY  # استخدام الـ Key المتاح

# if not API_KEY:
#     raise RuntimeError("GOOGLE_API_KEY is missing")

# ai = TravelAI(API_KEY)

# # إعداد عميل Gemini الذكي للشات
# client = genai.Client(api_key=GEMINI_KEY)


# # -----------------------------
# # Schemas
# # -----------------------------
# class TripRequest(BaseModel):
#     city: str
#     budget: int
#     mood: str

# # الـ Models الخاصة بنظام الشات بوت والمحادثة المستمرة
# class ChatMessage(BaseModel):
#     role: str  # إما "user" أو "model"
#     content: str

# class ChatRequest(BaseModel):
#     message: str
#     history: Optional[List[ChatMessage]] = []


# # -----------------------------
# # 🛠️ Tool Definition (الدالة الحقيقية اللي البوت هينادي عليها)
# # -----------------------------
# def bot_generate_trip_tool(city: str, mood: str) -> dict:
#     """
#     تقوم بتوليد واقتراح الأماكن المناسبة في مدينة مصرية معينة بناءً على تفضيلات وموود المستخدم.

#     Args:
#         city: اسم المدينة باللغة العربية (مثل: القاهرة، المنصورة، الإسكندرية، الجيزة، الأقصر، أسوان، دهب، شرم الشيخ، الغردقة، طنطا).
#         mood: نوع الأجواء المطلوبة للرحلة (youth للشبابية، family للعائلية، romantic للرومانسية، adventure للمغامرة، luxury للراقية، tourism للسياحية).
#     """
#     try:
#         # استدعاء الـ Trip Planner الحقيقي اللي شغال عندك في الـ Router تحت
#         # قمنا بتمرير budget افتراضي (مثلاً 5000) لحين طلبه من المستخدم صراحة
#         result = ai.trip_planner.create_trip(
#             city=city,
#             budget=5000, 
#             mood=mood,
#             lat=None,
#             lon=None
#         )
#         return {"status": "success", "data": result}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}


# # -----------------------------
# # 🤖 AI & Chat Endpoints
# # -----------------------------
# @router.post("/chat")
# async def chat_with_ai(payload: ChatRequest):
#     """
#     شات بوت ذكي يرجع الإجابة مقسمة: كلام منسق، يليه جدول الأماكن، 
#     وفي النهاية يرفق مسار بوستر الرحلة trip_poster.png
#     """
#     genai_history = []
#     for msg in payload.history:
#         genai_history.append(
#             types.Content(role=msg.role, parts=[types.Part.from_text(text=msg.content)])
#         )
        
#     # 🎯 تحديث التعليمات بدقة لترتيب الرد وإضافة البوستر
#     system_instruction = """
#     أنت المساعد السياحي الذكي الرسمي لمشروع "Smart Trip".
#     مهمتك مساعدة المستخدمين في تخطيط رحلاتهم بذكاء.
    
#     📌 ترتيب تنسيق الرد (هام جداً):
#     عندما تستخدم أداة `bot_generate_trip_tool` وترجع لك البيانات، صغ الرد بالترتيب التالي حرفياً:
#     1. مقدمة ترحيبية لطيفة وكلام منسق تحت بعضه يشرح أجواء الرحلة باختصار.
#     2. جدول Markdown منظم يحتوي على الأماكن المقترحة وأعمدته: (اسم المكان | نوع المكان | الفئة السعرية).
#     3. في السطر الأخير تماماً، اكتب هذه الجملة ليعرض التطبيق البوستر: "وادي بوستر الرحلة الخاص بيك يا فنان جاهز للتحميل: ![بوستر الرحلة](/static/trip_poster.png)"
    
#     تحدث دائماً بلهجة مصرية ودودة وجذابة.
#     """
    
#     config = types.GenerateContentConfig(
#         system_instruction=system_instruction,
#         temperature=0.3, 
#         tools=[bot_generate_trip_tool]
#     )
    
#     try:
#         response = client.models.generate_content(
#             model='gemini-2.5-flash',
#             contents=payload.message,
#             config=config
#         )
        
#         if response.function_calls:
#             function_call = response.function_calls[0]
            
#             if function_call.name == "bot_generate_trip_tool":
#                 args = function_call.args
#                 tool_output = bot_generate_trip_tool(city=args.get("city"), mood=args.get("mood"))
                
#                 follow_up = client.models.generate_content(
#                     model='gemini-2.5-flash',
#                     contents=[
#                         types.Content(role="user", parts=[types.Part.from_text(text=payload.message)]),
#                         response.candidates[0].content,
#                         types.Content(
#                             role="tool",
#                             parts=[types.Part.from_function_response(name="bot_generate_trip_tool", response={"result": tool_output})]
#                         )
#                     ],
#                     config=config
#                 )
                
#                 # نرجع الرد النصي المحتوي على التنسيق والجدول ورابط الصورة
#                 return {"reply": follow_up.text, "poster_url": "/static/trip_poster.png"}
                
#         return {"reply": response.text, "poster_url": None}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Chat Error: {str(e)}")

# @router.post("/process")
# def process_query(data: UserQuery):
#     return ai.process(data.query)


# @router.post("/routes")
# def routes_api(data: UserQuery):
#     return ai.process(data.query)


# @router.post("/trips")
# def trips_api(data: UserQuery):
#     return ai.process(data.query)


# @router.post("/recommendations")
# def recommendation_api(data: UserQuery):
#     return ai.process(data.query)


# # -----------------------------
# # Places APIs
# # -----------------------------
# @router.get("/places/{city}")
# def get_places(city: str):
#     return places_service.get_places(city=city, place_type="tourism", limit=20)


# @router.get("/places/{city}/{place_type}")
# def get_places_by_type(city: str, place_type: str):
#     return places_service.get_places(city=city, place_type=place_type, limit=20)


# # -----------------------------
# # Trip Planner
# # -----------------------------
# @router.post("/trip-plan")
# def generate_trip(request: TripRequest):
#     return ai.trip_planner.create_trip(
#         city=request.city,
#         budget=request.budget,
#         mood=request.mood,
#         lat=None,
#         lon=None
#     )


import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

from travel_ai import TravelAI
from app.schemas import UserQuery
from services.places_service import PlacesService

# استيراد الـ SDK الجديد الخاص بـ Gemini
import google.generativeai as genai

# Load env
load_dotenv()

# Router
router = APIRouter()

# Services
places_service = PlacesService()

API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or API_KEY  # استخدام الـ Key المتاح

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

# الـ Models الخاصة بنظام الشات بوت والمحادثة المستمرة
class ChatMessage(BaseModel):
    role: str  # إما "user" أو "model"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


# -----------------------------
# 🛠️ Tool Definition (الدالة الحقيقية اللي البوت هينادي عليها)
# -----------------------------
genai.configure(api_key=API_KEY)

chat_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
أنت Smart Transport AI.

ساعد المستخدم في:
- تخطيط الرحلات.
- ترشيح الأماكن.
- الرد باللهجة المصرية.
- إذا طلب المستخدم رحلة كاملة، اقترح استخدام Trip Planner.
"""
)

chat_sessions = {}

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

@router.post("/chat")
def chat(request: ChatRequest):

    try:

        session = request.session_id or "default"

        history = chat_sessions.get(session, [])

        chat = chat_model.start_chat(history=history)

        response = chat.send_message(request.message)

        history.append({
            "role": "user",
            "parts": [request.message]
        })

        history.append({
            "role": "model",
            "parts": [response.text]
        })

        chat_sessions[session] = history[-20:]

        return {
            "success": True,
            "reply": response.text,
            "session_id": session,
            "poster_url": "/static/trip_poster.png"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )    

@router.post("/process")
def process_query(data: UserQuery):
    return ai.process(data.query)


@router.post("/routes")
def routes_api(data: UserQuery):
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
    return places_service.get_places(city=city, place_type="tourism", limit=20)


@router.get("/places/{city}/{place_type}")
def get_places_by_type(city: str, place_type: str):
    return places_service.get_places(city=city, place_type=place_type, limit=20)


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