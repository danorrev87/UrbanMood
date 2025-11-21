from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text
from db import Base

class BodySection(enum.Enum):
    """Secciones corporales para categorizar ejercicios (matching gym paper forms)"""
    pecho = 'pecho'
    espalda = 'espalda'
    hombros = 'hombros'
    biceps = 'biceps'
    triceps = 'triceps'
    piernas = 'piernas'
    abdomen = 'abdomen'
    gluteos = 'gluteos'
    cardio = 'cardio'
    funcional = 'funcional'
    estiramiento = 'estiramiento'

class ExerciseType(enum.Enum):
    """Tipo de ejercicio"""
    fuerza = 'fuerza'
    cardio = 'cardio'
    flexibilidad = 'flexibilidad'
    funcional = 'funcional'
    hiit = 'hiit'
    core = 'core'

class Ejercicio(Base):
    """
    Catálogo de ejercicios disponibles.
    Los coaches seleccionan de aquí al armar rutinas.
    """
    __tablename__ = 'ejercicios'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)  # instrucciones del ejercicio
    image_url = Column(String(255), nullable=True)  # ruta a imagen del ejercicio
    body_section = Column(Enum(BodySection), nullable=False, index=True)
    exercise_type = Column(Enum(ExerciseType), nullable=False, default=ExerciseType.fuerza)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Ejercicio {self.name} ({self.body_section.value})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'body_section': self.body_section.value,
            'exercise_type': self.exercise_type.value,
            'is_active': self.is_active
        }
