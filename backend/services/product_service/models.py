from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Bike(Base):
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String(2000), nullable=True)
    image_url = Column(String(500), nullable=True)
    images = relationship("BikeImage", back_populates="bike")

class BikeImage(Base):
    __tablename__ = "bike_images"
    id = Column(Integer, primary_key=True)
    bike_id = Column(Integer, ForeignKey('bikes.id'), nullable=False)
    image_url = Column(String(500), nullable=False)
    bike = relationship("Bike", back_populates="images")
