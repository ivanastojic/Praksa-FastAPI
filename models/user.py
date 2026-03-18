from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    role = relationship("Role", back_populates="users")
    services = relationship("Service", back_populates="provider", cascade="all, delete")
    reviews = relationship("Review", back_populates="user", cascade="all, delete")

    @property
    def role_name(self):
        return self.role.name if self.role else None
