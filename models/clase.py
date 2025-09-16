from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from db import Base

class Clase(Base):
    __tablename__ = 'clases'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Clase {self.name}>"
