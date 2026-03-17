from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    category = relationship("Category", back_populates="services")
    provider = relationship("User", back_populates="services")
    reviews = relationship("Review", back_populates="service", cascade="all, delete")