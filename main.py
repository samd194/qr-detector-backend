"""
Application entrypoint. Wiring only — routes and logic live in app/.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import scan, assistant, admin

app = FastAPI(title="QR Fraud Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router)
app.include_router(assistant.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}