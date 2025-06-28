from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .models import Note, User, get_db
from .dependencies import get_current_user
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    notes = db.query(Note).filter(Note.user_id == user.id).all() if user else []
    return templates.TemplateResponse("home.html", {"request": request, "notes": notes, "user": user})

@router.post("/add-note")
def add_note(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user), data: str = Form(...)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    note = Note(data=data, user_id=user.id)
    db.add(note)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.post("/delete-note")
async def delete_note(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    data = await request.json()
    note_id = data.get("noteId")
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if note:
        db.delete(note)
        db.commit()
        return JSONResponse(content={"success": True})
    return JSONResponse(content={"success": False}, status_code=status.HTTP_404_NOT_FOUND)
