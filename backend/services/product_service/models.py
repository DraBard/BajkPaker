from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Bike(Base):
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String(10000), nullable=True)  # Specify length for VARCHAR
    bought = Column(Boolean, default=False)
    images = relationship("BikeImage", back_populates="bike")


class BikeImage(Base):
    __tablename__ = "bike_images"
    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    image_url = Column(String(2048), nullable=False)  # Limit URL length
    is_main = Column(Boolean, default=False)
    bike = relationship("Bike", back_populates="images")