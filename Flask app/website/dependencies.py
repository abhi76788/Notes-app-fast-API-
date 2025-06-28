from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Cookie, Depends
from .models import User, get_db
from sqlalchemy.orm import Session

SECRET_KEY = "supersecretkey"  # Should match your app's secret key
session_serializer = URLSafeSerializer(SECRET_KEY, salt="session")

def get_current_user(session: str = Cookie(None), db: Session = Depends(get_db)):
    if not session:
        return None
    try:
        user_id = session_serializer.loads(session)
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except BadSignature:
        return None
