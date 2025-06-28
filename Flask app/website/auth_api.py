from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer, BadSignature
from .models import User, get_db
from .schemas import UserCreate, UserLogin
from .auth_utils import authenticate_user, create_user
from .notes_api import router as notes_router
from .dependencies import get_current_user

app = FastAPI()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
app.include_router(notes_router)

SECRET_KEY = "supersecretkey"  # Change this in production!
session_serializer = URLSafeSerializer(SECRET_KEY, salt="session")

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@app.post("/login")
def login_post(request: Request, db: Session = Depends(get_db), response: Response = None, email: str = Form(...), password: str = Form(...)):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "user": None, "error": "Incorrect email or password"})
    session_token = session_serializer.dumps(user.id)
    resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="session", value=session_token, httponly=True)
    return resp

@app.get("/logout")
def logout(response: Response):
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie("session")
    return resp

@app.get("/sign-up", response_class=HTMLResponse)
def signup_get(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("sign_up.html", {"request": request, "user": None})

@app.post("/sign-up")
def signup_post(request: Request, db: Session = Depends(get_db), response: Response = None, email: str = Form(...), first_name: str = Form(...), password1: str = Form(...), password2: str = Form(...)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return templates.TemplateResponse("sign_up.html", {"request": request, "user": None, "error": "Email already exists."})
    if len(email) < 4:
        return templates.TemplateResponse("sign_up.html", {"request": request, "user": None, "error": "Email must be greater than 3 characters."})
    if len(first_name) < 2:
        return templates.TemplateResponse("sign_up.html", {"request": request, "user": None, "error": "First name must be greater than 1 character."})
    if password1 != password2:
        return templates.TemplateResponse("sign_up.html", {"request": request, "user": None, "error": "Passwords don't match."})
    if len(password1) < 7:
        return templates.TemplateResponse("sign_up.html", {"request": request, "user": None, "error": "Password must be at least 7 characters."})
    class FormData:
        pass
    form_data = FormData()
    form_data.email = email
    form_data.first_name = first_name
    form_data.password1 = password1
    form_data.password2 = password2
    new_user = create_user(db, form_data)
    session_token = session_serializer.dumps(new_user.id)
    resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="session", value=session_token, httponly=True)
    return resp

@app.get("/", response_class=HTMLResponse)
def home(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.post("/")
def home_post(request: Request):
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
