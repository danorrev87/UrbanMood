from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base


class WorkoutLog(Base):
    __tablename__ = 'workout_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    rutina_ejercicio_id = Column(Integer, ForeignKey('rutina_ejercicios.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    completed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User')
    rutina_ejercicio = relationship('RutinaEjercicio')

    __table_args__ = (
        UniqueConstraint('user_id', 'rutina_ejercicio_id', 'date', name='uq_workout_log'),
    )

    def __repr__(self):
        return f"<WorkoutLog user={self.user_id} re={self.rutina_ejercicio_id} date={self.date}>"
