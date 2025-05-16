from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Bike(Base):
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # SQLite doesn't require length constraints
    price = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)  # Use Text for longer content in SQLite
    bought = Column(Boolean, default=False)
    images = relationship("BikeImage", back_populates="bike")
    cart_items = relationship("CartItem", back_populates="bike")
    order_items = relationship("OrderItem", back_populates="bike")


class BikeImage(Base):
    __tablename__ = "bike_images"
    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    image_url = Column(String, nullable=False)  # SQLite doesn't need length limits
    is_main = Column(Boolean, default=False)
    bike = relationship("Bike", back_populates="images")


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    quantity = Column(Integer, nullable=False)
    session_id = Column(String, nullable=False)
    bike = relationship("Bike", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    quantity = Column(Integer, nullable=False)
    bike = relationship("Bike", back_populates="order_items")
    order = relationship("Order", back_populates="items")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
