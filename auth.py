from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from database import SessionLocal
from models import User
from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema
import bcrypt
import urllib.parse

from config import config
from consts import DOMAIN

router = APIRouter()
serializer = URLSafeTimedSerializer(config.SECRET_KEY)
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def generate_token(email: str, salt: str) -> str:
    token = serializer.dumps(email, salt=salt)
    return urllib.parse.quote(token)

def verify_token(token: str, salt: str, max_age=3600) -> str:
    try:
        token = urllib.parse.unquote(token)
        email = serializer.loads(token, salt=salt, max_age=max_age)
        return email
    except Exception as e:
        raise HTTPException(status_code=400, detail="無効なトークン")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(password)
    encrypted_email = User.encrypt_email(email)
    db_user = User(username=username, encrypted_email=encrypted_email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()

    token = generate_token(email, salt="email-confirm")
    confirm_url = f"{DOMAIN}confirm/{token}"

    message = MessageSchema(
        subject="メールアドレスの確認",
        recipients=[email],
        body=f"以下のリンクをクリックしてメールアドレスを確認してください:\n{confirm_url}",
        subtype="plain"
    )
    fm = FastMail(config.MAIL_CONFIG)
    await fm.send_message(message)

    return templates.TemplateResponse("register_success.html", {"request": request})

@router.get("/confirm/{token}")
def confirm_email(request: Request, token: str, db: Session = Depends(get_db)):
    try:
        email = verify_token(token, salt="email-confirm", max_age=3600)
        print(email)
        for user in db.query(User).all()[::-1]:
            print(User.decrypt_email(user.encrypted_email))
            if email == User.decrypt_email(user.encrypted_email):
                user.is_verified = True
                db.commit()
                return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
            
        raise HTTPException(status_code=400, detail="無効なトークン")
    except:
        raise HTTPException(status_code=400, detail="無効なトークン")
    
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == username).first()

    if not db_user or not verify_password(password, db_user.hashed_password):

        raise HTTPException(status_code=400, detail="無効な認証情報")
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/dashboard")
def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@router.get("/logout")
def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/reset-password")
async def reset_password(email: str = Form(...), db: Session = Depends(get_db)):
    encrypted_email = User.encrypt_email(email)
    user = db.query(User).filter(User.email_encrypted == encrypted_email).first()

    if not user:
        raise HTTPException(status_code=400, detail="このメールアドレスは登録されていません。")

    token = serializer.dumps(email, salt="password-reset")
    reset_url = f"{DOMAIN}reset/{token}"

    message = MessageSchema(
        subject="パスワードリセット",
        recipients=[email],
        body=f"以下のリンクをクリックして新しいパスワードを設定してください:\n{reset_url}",
        subtype="plain"
    )
    fm = FastMail(config.MAIL_CONFIG)
    await fm.send_message(message)

    return templates.TemplateResponse("reset_email_sent.html", {"request": Request, "email": email})

@router.get("/reset/{token}")
def reset_password_page(request: Request, token: str):
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

@router.post("/reset-password-confirm")
def reset_password_confirm(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        email = serializer.loads(token, salt="password-reset")
        encrypted_email = User.encrypt_email(email)
        user = db.query(User).filter(User.encrypted_email == encrypted_email).first()

        if not user:
            raise HTTPException(status_code=400, detail="無効なトークン")

        user.hashed_password = hash_password(new_password)
        db.commit()

        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    except:
        raise HTTPException(status_code=400, detail="無効なトークン")