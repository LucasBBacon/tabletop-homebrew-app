# app/models/user.py

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, DateTime, String, Text, func
from app.database.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password = Column(
        Text,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    verification_token = Column(
        String(255),
        nullable=True,
    )
    full_name = Column(
        String(100),
        nullable=True,
    )
    phone_number = Column(
        String(15),
        nullable=True,
    )
    