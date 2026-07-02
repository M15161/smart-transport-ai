from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Smart Transport AI",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Smart Transport AI"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(
    router,
    prefix="/ai",
    tags=["AI"]
)