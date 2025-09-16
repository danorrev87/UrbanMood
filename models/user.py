from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship
from db import Base

class UserRole(enum.Enum):
    user = 'user'
    coach = 'coach'
    admin = 'admin'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(191), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))  # nullable until invitation accepted
    name = Column(String(120), nullable=False)
    phone = Column(String(40))
    birth_date = Column(Date, nullable=True)
    address = Column(String(255))
    gender = Column(String(40), nullable=True)  # store value from controlled list
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user, index=True)
    preferred_location_id = Column(Integer)  # future FK
    is_active = Column(Boolean, default=False, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    created_by = relationship('User', remote_side=[id], uselist=False)

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = datetime.utcnow().date()
        years = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return years
