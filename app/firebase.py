"""
Firebase Admin SDK singleton initializer.
Import `db` from here anywhere you need Firestore access.
"""
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

# On Render, the service account JSON is provided as an environment variable
# (its full contents, as a string) rather than a file on disk.
firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if firebase_creds_json:
    cred_dict = json.loads(firebase_creds_json)
    _cred = credentials.Certificate(cred_dict)
else:
    # Local development: fall back to the actual file
    _cred = credentials.Certificate(settings.firebase_service_account_path)

firebase_admin.initialize_app(_cred)

db = firestore.client()