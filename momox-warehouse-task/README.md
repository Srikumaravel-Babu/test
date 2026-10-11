# Warehouse Pick List Service

## Context

You are working on the warehouse management system at **momox**, a second-hand e-commerce company based in Berlin. The warehouse in Leipzig stores millions of unique second-hand items (books, media, fashion).

When a customer places an order, the system needs to tell warehouse employees:
1. **Which items to pick** from the shelves
2. **In what order** to walk through the warehouse (sorted by shelf location)
3. **What box size** to use for packing

The existing codebase already has models, database setup, and a basic health endpoint. An endpoint to create orders (`POST /orders`) is also already implemented.

---

## Your Task

**Implement the `POST /orders/{order_id}/pick` endpoint** that generates a pick list for warehouse employees.

This endpoint should:

1. **Look up the order** by `order_id` — return `404` if not found
2. **Validate the order status** — only orders with status `PENDING` can be picked (return `409 Conflict` otherwise)
3. **Generate a pick list** — return the order's items sorted by `shelf_location` (so employees walk through aisles efficiently: `A-01-01` → `A-01-02` → `B-03-01`)
4. **Suggest a box size** based on total weight:
   - `SMALL` — total weight ≤ 500g
   - `MEDIUM` — total weight ≤ 2000g
   - `LARGE` — total weight > 2000g
5. **Update statuses**:
   - Set each item's status to `PICKED`
   - Set the order's status to `PROCESSING`
6. **Return the pick list response** (see schema below)

### Expected Response Schema

```json
{
  "order_id": "uuid",
  "box_size": "SMALL | MEDIUM | LARGE",
  "total_weight_grams": 750,
  "items": [
    {
      "item_id": "uuid",
      "name": "Harry Potter and the Philosopher's Stone",
      "shelf_location": "A-02-15",
      "category": "BOOK",
      "weight_grams": 350
    }
  ]
}
```

---

## Getting Started

```bash
# Clone and set up
git clone <this-repo>
cd momox-warehouse-task

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn app.main:app --reload

# Run tests (there is one existing test + a placeholder for yours)
pytest tests/ -v
```

The app uses **SQLite** so no database setup is needed.

---

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app setup
│   ├── models.py          # SQLAlchemy models (Item, Order, OrderItem)
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database connection setup
│   └── routers/
│       ├── __init__.py
│       └── orders.py      # Order endpoints — YOUR WORK GOES HERE
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Test fixtures (pre-seeded database)
│   └── test_orders.py     # Tests
├── requirements.txt
└── README.md
```

---

## Hints

- Look at the existing `POST /orders` endpoint in `app/routers/orders.py` for patterns to follow
- Look at `app/schemas.py` for the Pydantic models — `PickListResponse` is already defined for you
- The test fixtures in `tests/conftest.py` seed the database with sample items and an order
- Think out loud as you work — we want to understand your thought process!

---

## What We're Looking For

- Clean, readable code that follows existing patterns
- Proper error handling (404, 409)
- Correct use of SQLAlchemy queries and transactions
- Input validation
- Your thought process as you build
