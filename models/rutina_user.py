from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base


class RutinaUser(Base):
    """
    Tabla de asociación entre Rutina y User.
    Permite asignar múltiples usuarios a una misma rutina.
    is_active controla que solo haya 1 rutina activa por usuario.
    """
    __tablename__ = 'rutina_users'

    id = Column(Integer, primary_key=True)
    rutina_id = Column(Integer, ForeignKey('rutinas.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    rutina = relationship('Rutina', back_populates='assigned_users')
    user = relationship('User', backref='rutina_assignments')

    __table_args__ = (UniqueConstraint('rutina_id', 'user_id'),)

    def __repr__(self):
        return f"<RutinaUser rutina={self.rutina_id} user={self.user_id} active={self.is_active}>"
