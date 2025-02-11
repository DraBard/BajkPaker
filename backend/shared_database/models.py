from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
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
    cart_items = relationship("CartItem", back_populates="bike")
    order_items = relationship("OrderItem", back_populates="bike")


class BikeImage(Base):
    __tablename__ = "bike_images"
    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    image_url = Column(String(2048), nullable=False)  # Limit URL length
    is_main = Column(Boolean, default=False)
    bike = relationship("Bike", back_populates="images")


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    quantity = Column(Integer, nullable=False)
    bike = relationship("Bike", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Integer, nullable=False)
    status = Column(String(50), default="pending")  # Limit status length
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
    username = Column(String(124), unique=True, index=True)  # Limit username length
    password = Column(String(255))  # Limit password length
    email = Column(String(255), unique=True, index=True, nullable=False)  # Limit email length
