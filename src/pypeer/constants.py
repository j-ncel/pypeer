import os


DEFAULT_FIREBASE_URL = "https://liminalport-default-rtdb.firebaseio.com/"
FIREBASE_DB_URL = os.getenv("PYPEER_URL", DEFAULT_FIREBASE_URL)
ICE_SERVERS = [
    {"urls": "stun:stun.l.google.com:19302"},
    {"urls": "stun:stun1.l.google.com:19302"},
    {"urls": "stun:stun2.l.google.com:19302"},
    {"urls": "stun:stun.l.google.com:19305"},
]
