# from fastapi import FastAPI
# from app.routes import router

# app = FastAPI(
#     title="Smart Transport AI",
#     version="1.0.0"
# )

# @app.get("/")
# def home():
#     return {
#         "status": "running",
#         "project": "Smart Transport AI"
#     }

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# app.include_router(
#     router,
#     prefix="/ai",
#     tags=["AI"]
# )

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(
    title="Smart Transport AI",
    version="1.0.0"
)

# 🎯 ربط الملفات الثابتة (Static Files) بالسيرفر
# السطر ده بيخلي أي ملف في المجلد الرئيسي (زي trip_poster.png) 
# متاح للتحميل أو العرض مباشرة عبر الرابط: http://127.0.0.1:8000/static/trip_poster.png
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Smart Transport AI"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# تضمين الـ Router الخاص بالـ AI والـ Chatbot الجديد
app.include_router(
    router,
    prefix="/ai",
    tags=["AI"]
)