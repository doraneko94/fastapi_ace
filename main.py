from fastapi import FastAPI
from database import engine, Base
from starlette.middleware.sessions import SessionMiddleware

import auth
from config import config

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)