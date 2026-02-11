from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from db import Base

class Sucursal(Base):
    __tablename__ = 'sucursales'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    address = Column(String(255))
    phone = Column(String(40))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
