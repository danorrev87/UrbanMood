from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from db import Base

class Rutina(Base):
    """
    Rutina creada por un coach.
    Puede ser asignada a múltiples usuarios a través de la tabla rutina_users.
    """
    __tablename__ = 'rutinas'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)

    # Creador
    created_by_coach_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Vigencia (opcional)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Estado
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    coach = relationship('User', foreign_keys=[created_by_coach_id], backref='rutinas_creadas')
    ejercicios = relationship('RutinaEjercicio', back_populates='rutina', cascade='all, delete-orphan', order_by='RutinaEjercicio.orden')
    assigned_users = relationship('RutinaUser', back_populates='rutina', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Rutina {self.name}>"

    def to_dict(self, include_ejercicios=False):
        assigned = []
        for au in self.assigned_users:
            assigned.append({
                'user_id': au.user_id,
                'user_name': au.user.name if au.user else None,
                'user_email': au.user.email if au.user else None,
                'is_active': au.is_active,
            })

        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'assigned_users': assigned,
            'coach_id': self.created_by_coach_id,
            'coach_name': self.coach.name if self.coach else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_ejercicios:
            data['ejercicios'] = [re.to_dict() for re in self.ejercicios]
        return data
