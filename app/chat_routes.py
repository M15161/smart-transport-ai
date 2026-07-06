# import os
# import google.generativeai as genai

# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from dotenv import load_dotenv

# load_dotenv()

# router = APIRouter()

# API_KEY = os.getenv("GOOGLE_API_KEY")

# if not API_KEY:
#     raise RuntimeError("GOOGLE_API_KEY not found")

# genai.configure(api_key=API_KEY)

# model = genai.GenerativeModel(
#     model_name="gemini-2.5-flash",
#     system_instruction="""
# أنت Smart Transport AI.

# - تحدث باللهجة المصرية.
# - ساعد المستخدم في السفر.
# - اقترح أماكن.
# - اقترح مطاعم.
# - اقترح فنادق.
# - جاوب على أي سؤال عام.
# - لو المستخدم طلب تخطيط رحلة اقترح عليه استخدام Trip Planner.
# - لا تكتب Markdown معقد.
# - رد بطريقة مرتبة ولطيفة.
# """
# )

# # حفظ المحادثات
# chats = {}


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# @router.post("/chat")
# def chat(req: ChatRequest):

#     try:

#         if req.session_id not in chats:
#             chats[req.session_id] = model.start_chat(history=[])

#         response = chats[req.session_id].send_message(req.message)

#         return {
#             "reply": response.text
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )

# import os
# import google.generativeai as genai

# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from dotenv import load_dotenv

# from travel_ai import TravelAI

# import json

# load_dotenv()

# router = APIRouter()

# API_KEY = os.getenv("GOOGLE_API_KEY")

# if not API_KEY:
#     raise RuntimeError("GOOGLE_API_KEY is missing")

# genai.configure(api_key=API_KEY)

# model = genai.GenerativeModel(
#     model_name="gemini-2.5-flash",
#     system_instruction="""
# أنت Smart Transport AI Assistant.

# قواعد مهمة:

# - تحدث باللهجة المصرية.
# - رد بطريقة لطيفة ومنظمة.
# - لو المستخدم بيسأل سؤال عادي جاوبه.
# - لو طلب ترشيحات أماكن أو رحلة أو Route استخدم النظام الداخلي.
# - لا تخترع أماكن.
# """
# )

# travel_ai = TravelAI(API_KEY)

# sessions = {}


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# @router.post("/chat")
# def chat(req: ChatRequest):

#     text = req.message.lower()

#     keywords = [
#         "trip",
#         "route",
#         "رحلة",
#         "فسحة",
#         "اماكن",
#         "أماكن",
#         "restaurant",
#         "مطعم",
#         "hotel",
#         "فندق",
#         "كافيه",
#         "cafe",
#         "زيارة"
#     ]

#     try:

#         # if any(word in text for word in keywords):

#         #     result = travel_ai.process(req.message)

#         #     return {
#         #         "type": "trip",
#         #         "data": result
#         #     }
#         if any(word in text for word in keywords):

#             result = travel_ai.process(req.message)
#             print("=" * 80)
#             print(json.dumps(result, indent=4, ensure_ascii=False))
#             print("=" * 80)

#             # استخراج الأماكن من النتيجة
#             places = []

#             if isinstance(result, dict):
#                 places = result.get("places", [])

#             # خلي Gemini يكتب وصف فقط
#             prompt = f"""
#             المستخدم طلب رحلة.

#             اكتب وصف جميل للرحلة.

#             لا تعمل جدول.

#             لا تكرر أسماء الأماكن.

#             البيانات:

#             {result}
#             """

#             response = model.generate_content(prompt)

#             extract_prompt = f"""
#                 من الرد التالي استخرج الأماكن فقط.

#                 أرجع JSON فقط.

#                 الصيغة:

#                 [
#                 {{
#                     "name":"",
#                     "category":"",
#                     "time":"",
#                     "estimated_cost":""
#                 }}
#                 ]

#                 النص:

#                 {response.text}
#                 """
#             extract = model.generate_content(extract_prompt)
            

#             try:
#                 places = json.loads(
#                     extract.text.replace("```json", "").replace("```", "")
#                 )
#             except:
#                 places = []

#             return {

#                 # "type": "trip",

#                 # "reply": response.text,

#                 # "places": places,

#                 # "poster": "/static/trip_poster.png",

#                 # "raw": result
#                 "success": True,
#                 "reply": response.text,
#                 "places": places,
#                 "poster_url": "/static/trip_poster.png",
#                 "session_id": req.session_id

#             }

#         if req.session_id not in sessions:
#             sessions[req.session_id] = model.start_chat(history=[])

#         response = sessions[req.session_id].send_message(req.message)

#         return {
#             "type": "chat",
#             "reply": response.text
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )

import os
import json

import google.generativeai as genai

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from travel_ai import TravelAI

load_dotenv()

router = APIRouter()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
أنت Smart Transport AI Assistant.

القواعد:

- اتكلم باللهجة المصرية.
- كن ودود ومنظم.
- لو المستخدم بيسأل سؤال عادي جاوبه.
- لو المستخدم طلب رحلة أو Route أو أماكن أو مطاعم استخدم النظام الداخلي.
- لا تخترع أماكن.
"""
)

travel_ai = TravelAI(API_KEY)

sessions = {}


# -----------------------------
# Schemas
# -----------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str


# -----------------------------
# Chat Endpoint
# -----------------------------
@router.post("/chat")
def chat(req: ChatRequest):

    text = req.message.lower()

    keywords = [
        "trip",
        "route",
        "plan",
        "planner",
        "travel",
        "visit",
        "places",
        "place",
        "restaurant",
        "cafe",
        "hotel",
        "museum",
        "park",
        "tour",

        "رحلة",
        "فسحة",
        "خروجة",
        "مكان",
        "أماكن",
        "مطعم",
        "كافيه",
        "فندق",
        "متحف",
        "حديقة",
        "زيارة",
        "برنامج",
        "جدول",
        "سفر"
    ]

    try:

        if any(word in text for word in keywords):

            result = travel_ai.process(req.message)

            print("=" * 80)
            print(json.dumps(result, indent=4, ensure_ascii=False))
            print("=" * 80)

            places = result.get("places", [])

            TYPE_MAP = {
                "museum": "متحف",
                "hotel": "فندق",
                "restaurant": "مطعم",
                "cafe": "كافيه",
                "viewpoint": "معلم سياحي",
                "attraction": "مكان ترفيهي",
                "park": "حديقة",
                "mall": "مول",
                "beach": "شاطئ"
            }

            for place in places:
                place["type_ar"] = TYPE_MAP.get(
                    place.get("type", ""),
                    place.get("type", "")
                )

            places_text = "\n".join([
                f"- {p['name']} ({p['type_ar']})"
                for p in places
            ])

            prompt = f"""
أنت Smart Trip AI.

المستخدم طلب:

{req.message}

الأماكن الحقيقية التي وفرها النظام:

{places_text}

مهم جداً:

- استخدم الأماكن الموجودة فقط.
- لا تضيف أي مكان من عندك.
- لا تعمل جدول.
- لا تكرر أسماء الأماكن.
- اكتب وصف جميل ومنظم للرحلة باللهجة المصرية.
- اشرح للمستخدم ليه الأماكن دي مناسبة.
- اختم الرد بجملة لطيفة فقط.
"""

            response = model.generate_content(prompt)

            return {
                "success": True,
                "reply": response.text,
                "places": places,
                "poster_url": "/static/trip_poster.png",
                "session_id": req.session_id
            }

        # -----------------------------
        # Chat عادي
        # -----------------------------

        if req.session_id not in sessions:
            sessions[req.session_id] = model.start_chat(history=[])

        response = sessions[req.session_id].send_message(req.message)

        return {
            "success": True,
            "reply": response.text,
            "session_id": req.session_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )