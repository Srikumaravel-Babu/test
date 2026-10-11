import enum
from datetime import datetime

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────


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


class BoxSize(str, enum.Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


# ─── Item Schemas ─────────────────────────────────────────────────────────────


class ItemResponse(BaseModel):
    id: str
    sku: str
    name: str
    category: ItemCategory
    weight_grams: int
    shelf_location: str
    status: ItemStatus

    model_config = {"from_attributes": True}


# ─── Order Schemas ────────────────────────────────────────────────────────────


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    item_ids: list[str] = Field(..., min_length=1)


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    created_at: datetime
    status: OrderStatus
    items: list[ItemResponse]

    model_config = {"from_attributes": True}


# ─── Pick List Schemas ────────────────────────────────────────────────────────


class PickListItem(BaseModel):
    """A single item in the pick list, sorted by shelf location."""

    item_id: str
    name: str
    shelf_location: str
    category: ItemCategory
    weight_grams: int

    model_config = {"from_attributes": True}


class PickListResponse(BaseModel):
    """
    The response for POST /orders/{order_id}/pick.

    Contains items sorted by shelf_location for efficient warehouse traversal,
    and a suggested box size based on total weight.
    """

    order_id: str
    box_size: BoxSize
    total_weight_grams: int
    items: list[PickListItem]
