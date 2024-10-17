# backend/services/order_service/models.py

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

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    quantity = Column(Integer, nullable=False)
    bike = relationship("Bike")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    total_price = Column(Float, nullable=False)
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    quantity = Column(Integer, nullable=False)
    bike = relationship("Bike")
    order = relationship("Order", back_populates="items")