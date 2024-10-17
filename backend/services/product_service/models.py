from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Bike(Base):
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(2000), nullable=True)
    bought = Column(Boolean, default=False)
    images = relationship("BikeImage", back_populates="bike")

class BikeImage(Base):
    __tablename__ = "bike_images"
    id = Column(Integer, primary_key=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    image_url = Column(String(255), nullable=False)
    is_main = Column(Boolean, default=False)
    bike = relationship("Bike", back_populates="images")

