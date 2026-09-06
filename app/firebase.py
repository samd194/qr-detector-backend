"""
Firebase Admin SDK singleton initializer.
Import `db` from here anywhere you need Firestore access.
"""
import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

_cred = credentials.Certificate(settings.firebase_service_account_path)
firebase_admin.initialize_app(_cred)

db = firestore.client()