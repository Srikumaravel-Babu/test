import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Float, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ItemCategory(str, enum.Enum):
    BOOK = "BOOK"
    MEDIA = "MEDIA"
    FASHION = "FASHION"


class ItemStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    PICKED = "PICKED"
    SHIPPED = "SHIPPED"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY_TO_SHIP = "READY_TO_SHIP"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(Enum(ItemCategory), nullable=False)
    weight_grams = Column(Integer, nullable=False)
    width_cm = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    depth_cm = Column(Float, nullable=False)
    shelf_location = Column(String, nullable=False, index=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.AVAILABLE, nullable=False)

    order_items = relationship("OrderItem", back_populates="item")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)

    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")
