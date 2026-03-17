from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    services = relationship("Service", back_populates="category", cascade="all, delete")