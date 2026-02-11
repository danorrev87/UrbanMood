from datetime import datetime, timedelta
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db import Base

class InvitationPurpose(enum.Enum):
    invite = 'invite'
    reset = 'reset'

class InvitationToken(Base):
    __tablename__ = 'invitation_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    purpose = Column(Enum(InvitationPurpose), nullable=False, default=InvitationPurpose.invite)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    invalidated = Column(Boolean, default=False, nullable=False)

    user = relationship('User', backref='invitation_tokens')

    @staticmethod
    def new_expiry(hours=72):
        return datetime.utcnow() + timedelta(hours=hours)
