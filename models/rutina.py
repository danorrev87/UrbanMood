from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from db import Base

class Rutina(Base):
    """
    Rutina asignada a un usuario.
    Creada por un coach, contiene múltiples ejercicios con sus configuraciones.
    """
    __tablename__ = 'rutinas'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)  # ej: "Rutina Fullbody Semana 1"
    description = Column(Text, nullable=True)  # notas del coach
    
    # Asignación
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_by_coach_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Vigencia (opcional - para rutinas con fecha de inicio/fin)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='rutinas_asignadas')
    coach = relationship('User', foreign_keys=[created_by_coach_id], backref='rutinas_creadas')
    ejercicios = relationship('RutinaEjercicio', back_populates='rutina', cascade='all, delete-orphan', order_by='RutinaEjercicio.orden')

    def __repr__(self):
        return f"<Rutina {self.name} (User: {self.user_id})>"

    def to_dict(self, include_ejercicios=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
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
