"""
Admin API — called from the Flutter app's admin screens.
Every route requires a valid Firebase ID token belonging to a UID
present in the 'admins' Firestore collection.
"""
from fastapi import APIRouter, Depends
from firebase_admin import auth as firebase_auth

from app.firebase import db
from app.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_stats(uid: str = Depends(require_admin)):
    users = list(db.collection("users").stream())
    scans = list(db.collection("scans").stream())
    reports = list(db.collection("reports").stream())

    scan_data = [s.to_dict() for s in scans]
    report_data = [r.to_dict() for r in reports]

    return {
        "total_users": len(users),
        "total_scans": len(scans),
        "safe_count": sum(1 for s in scan_data if s.get("risk_level") == "Safe"),
        "suspicious_count": sum(1 for s in scan_data if s.get("risk_level") == "Suspicious"),
        "dangerous_count": sum(1 for s in scan_data if s.get("risk_level") == "Dangerous"),
        "pending_reports": sum(1 for r in report_data if r.get("status") == "pending"),
    }


@router.get("/reports")
async def get_reports(uid: str = Depends(require_admin)):
    docs = db.collection("reports").order_by("reported_at", direction="DESCENDING").stream()
    reports = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if "reported_at" in data and data["reported_at"]:
            data["reported_at"] = data["reported_at"].isoformat()
        reports.append(data)
    return {"reports": reports}


@router.post("/reports/{report_id}/approve")
async def approve_report(report_id: str, uid: str = Depends(require_admin)):
    db.collection("reports").document(report_id).update({"status": "approved"})
    return {"success": True}


@router.post("/reports/{report_id}/reject")
async def reject_report(report_id: str, uid: str = Depends(require_admin)):
    db.collection("reports").document(report_id).update({"status": "rejected"})
    return {"success": True}


@router.get("/admins")
async def list_admins(uid: str = Depends(require_admin)):
    docs = db.collection("admins").stream()
    admins = []
    for doc in docs:
        data = doc.to_dict()
        admins.append({"uid": doc.id, "email": data.get("email", "")})
    return {"admins": admins}


@router.post("/admins")
async def add_admin(email: str, uid: str = Depends(require_admin)):
    try:
        user_record = firebase_auth.get_user_by_email(email)
    except Exception:
        return {"success": False, "error": "No user found with that email"}

    db.collection("admins").document(user_record.uid).set({"email": email})
    return {"success": True}


@router.delete("/admins/{target_uid}")
async def remove_admin(target_uid: str, uid: str = Depends(require_admin)):
    if target_uid == uid:
        return {"success": False, "error": "You cannot remove yourself"}
    db.collection("admins").document(target_uid).delete()
    return {"success": True}