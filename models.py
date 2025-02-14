from database import Base
from sqlalchemy import Boolean, Column, Float, Integer, String

from config import config

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    encrypted_email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rating = Column(Float, default=1500.0)
    is_verified = Column(Boolean, default=False)

    @staticmethod
    def encrypt_email(email: str) -> str:
        return config.CIPHER.encrypt(email.encode()).decode()
    
    @staticmethod
    def decrypt_email(encrypted_email: str) -> str:
        return config.CIPHER.decrypt(encrypted_email.encode()).decode()