"""
Verifies Firebase ID tokens sent from the Flutter app and checks admin status.
This is the real security boundary — never trust a client-side admin flag alone.
"""
from fastapi import Header, HTTPException
from firebase_admin import auth as firebase_auth

from app.firebase import db


async def get_current_uid(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    id_token = authorization.replace("Bearer ", "")
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def require_admin(authorization: str = Header(...)) -> str:
    uid = await get_current_uid(authorization)
    doc = db.collection("admins").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=403, detail="Admin access required")
    return uid