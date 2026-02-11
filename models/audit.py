from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(64), nullable=False)
    entity = Column(String(64))
    entity_id = Column(Integer)
    meta = Column(Text)  # JSON serialized string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship('User', backref='audit_logs')
