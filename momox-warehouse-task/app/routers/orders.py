import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item, Order, OrderItem, ItemStatus, OrderStatus
from app.schemas import (
    CreateOrderRequest,
    OrderResponse,
    ItemResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    Create a new order from a list of item IDs.

    - Validates all items exist and are AVAILABLE
    - Reserves the items (sets status to RESERVED)
    - Creates the order and links the items
    - Returns the created order with item details

    If any item is not available, the entire order is rejected.
    """
    # Fetch all requested items
    items = db.query(Item).filter(Item.id.in_(request.item_ids)).all()

    # Check all items exist
    if len(items) != len(request.item_ids):
        found_ids = {item.id for item in items}
        missing = [iid for iid in request.item_ids if iid not in found_ids]
        raise HTTPException(
            status_code=404,
            detail=f"Items not found: {missing}",
        )

    # Check all items are available
    unavailable = [item for item in items if item.status != ItemStatus.AVAILABLE]
    if unavailable:
        raise HTTPException(
            status_code=409,
            detail=f"Items not available: {[item.id for item in unavailable]}",
        )

    # Create the order
    order = Order(customer_id=request.customer_id)
    db.add(order)
    db.flush()  # Get the order ID

    # Link items to order and reserve them
    for item in items:
        order_item = OrderItem(order_id=order.id, item_id=item.id)
        db.add(order_item)
        item.status = ItemStatus.RESERVED

    db.commit()
    db.refresh(order)

    logger.info(f"Order {order.id} created with {len(items)} items")

    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        created_at=order.created_at,
        status=order.status,
        items=[
            ItemResponse(
                id=item.id,
                sku=item.sku,
                name=item.name,
                category=item.category,
                weight_grams=item.weight_grams,
                shelf_location=item.shelf_location,
                status=item.status,
            )
            for item in items
        ],
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    """Retrieve an order by ID with all its items."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = [oi.item for oi in order.order_items]

    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        created_at=order.created_at,
        status=order.status,
        items=[
            ItemResponse(
                id=item.id,
                sku=item.sku,
                name=item.name,
                category=item.category,
                weight_grams=item.weight_grams,
                shelf_location=item.shelf_location,
                status=item.status,
            )
            for item in items
        ],
    )


# ──────────────────────────────────────────────────────────────────────────────
# TODO: Implement POST /orders/{order_id}/pick
#
# This endpoint should generate a pick list for warehouse employees.
# See README.md for full requirements.
#
# Hints:
#   - Follow the same patterns used in create_order and get_order above
#   - The PickListResponse and PickListItem schemas are already defined
#     in app/schemas.py — import and use them
#   - Remember to handle edge cases (order not found, wrong status)
#   - Sort items by shelf_location for efficient warehouse traversal
#   - Calculate box size based on total weight (see README for thresholds)
# ──────────────────────────────────────────────────────────────────────────────
