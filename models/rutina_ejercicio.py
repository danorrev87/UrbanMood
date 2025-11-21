from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from db import Base

class RutinaEjercicio(Base):
    """
    Tabla de asociación entre Rutina y Ejercicio.
    Almacena la configuración específica: series, repeticiones, peso, notas, orden.
    """
    __tablename__ = 'rutina_ejercicios'
    
    id = Column(Integer, primary_key=True)
    rutina_id = Column(Integer, ForeignKey('rutinas.id'), nullable=False, index=True)
    ejercicio_id = Column(Integer, ForeignKey('ejercicios.id'), nullable=False, index=True)
    
    # Configuración del ejercicio en esta rutina
    series = Column(Integer, nullable=False, default=3)  # número de series
    repeticiones = Column(String(40), nullable=True)  # ej: "12", "10-12", "al fallo"
    peso = Column(String(40), nullable=True)  # ej: "20kg", "peso corporal", "banda roja"
    descanso = Column(String(40), nullable=True)  # ej: "60 seg", "90 seg"
    notas = Column(Text, nullable=True)  # instrucciones específicas del coach
    
    # Orden en la rutina (para mantener secuencia)
    orden = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    rutina = relationship('Rutina', back_populates='ejercicios')
    ejercicio = relationship('Ejercicio', backref='rutina_asignaciones')

    def __repr__(self):
        return f"<RutinaEjercicio Rutina:{self.rutina_id} Ejercicio:{self.ejercicio_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'ejercicio_id': self.ejercicio_id,
            'ejercicio_name': self.ejercicio.name if self.ejercicio else None,
            'ejercicio_image_url': self.ejercicio.image_url if self.ejercicio else None,
            'ejercicio_body_section': self.ejercicio.body_section.value if self.ejercicio else None,
            'series': self.series,
            'repeticiones': self.repeticiones,
            'peso': self.peso,
            'descanso': self.descanso,
            'notas': self.notas,
            'orden': self.orden
        }
