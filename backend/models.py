from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ErrorLog(Base):
    __tablename__ = "error_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    step = Column(String(255))
    sku = Column(String(255), nullable=True)
    message = Column(Text)

class RotationStatus(Base):
    __tablename__ = "rotation_status"
    id = Column(Integer, primary_key=True, index=True)
    last_run = Column(DateTime, default=datetime.utcnow)
    last_sku = Column(String(255), nullable=True)
    success = Column(Boolean, default=True)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
