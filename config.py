from cryptography.fernet import Fernet
from fastapi_mail import ConnectionConfig
import os

class Config():
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_USERNAME")
    MAIL_TLS: bool = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_SSL: bool = True
    if MAIL_TLS:
        MAIL_PORT: int = 587
    else:
        MAIL_PORT: int = 465
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")

    CIPHER = Fernet(SECRET_KEY.encode())
    
    MAIL_CONFIG = ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM=MAIL_FROM,
        MAIL_PORT=MAIL_PORT,
        MAIL_SERVER=MAIL_SERVER,
        MAIL_STARTTLS=MAIL_TLS,
        MAIL_SSL_TLS=MAIL_SSL,
        USE_CREDENTIALS=True
    )

config = Config()