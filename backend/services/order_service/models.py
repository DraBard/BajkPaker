from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Bike(Base):
    """
    Local copy of bike data from the product service.
    This is used for order history and cart functionality.
    """
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(10000), nullable=True)
    bought = Column(Boolean, default=False)

class CartItem(Base):
    """Cart items are temporary and linked to a session."""
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    quantity = Column(Integer, nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    bike = relationship("Bike")

class Order(Base):
    """Order record with status and total price."""
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    customer_info = Column(JSON, nullable=True)  # Store customer info as JSON
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    """Individual items within an order."""
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="items")
    bike = relationship("Bike")
