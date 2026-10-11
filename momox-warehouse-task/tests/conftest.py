import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Item, ItemCategory, ItemStatus, Order, OrderItem, OrderStatus

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test_warehouse.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provide a clean database session for each test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ─── Sample Data ──────────────────────────────────────────────────────────────

SAMPLE_ITEMS = [
    Item(
        id="item-001",
        sku="BK-HP-001",
        name="Harry Potter and the Philosopher's Stone",
        category=ItemCategory.BOOK,
        weight_grams=350,
        width_cm=13.0,
        height_cm=20.0,
        depth_cm=2.5,
        shelf_location="A-02-15",
        status=ItemStatus.AVAILABLE,
    ),
    Item(
        id="item-002",
        sku="BK-LR-001",
        name="The Lord of the Rings: Fellowship",
        category=ItemCategory.BOOK,
        weight_grams=480,
        width_cm=14.0,
        height_cm=21.0,
        depth_cm=3.5,
        shelf_location="A-01-03",
        status=ItemStatus.AVAILABLE,
    ),
    Item(
        id="item-003",
        sku="MD-VN-001",
        name="Abbey Road - The Beatles (Vinyl)",
        category=ItemCategory.MEDIA,
        weight_grams=180,
        width_cm=31.5,
        height_cm=31.5,
        depth_cm=0.5,
        shelf_location="C-05-22",
        status=ItemStatus.AVAILABLE,
    ),
    Item(
        id="item-004",
        sku="FS-JK-001",
        name="Levi's Denim Jacket (Size M)",
        category=ItemCategory.FASHION,
        weight_grams=900,
        width_cm=50.0,
        height_cm=70.0,
        depth_cm=5.0,
        shelf_location="B-12-08",
        status=ItemStatus.AVAILABLE,
    ),
    Item(
        id="item-005",
        sku="BK-DC-001",
        name="Don Quixote",
        category=ItemCategory.BOOK,
        weight_grams=650,
        width_cm=15.0,
        height_cm=22.0,
        depth_cm=4.0,
        shelf_location="A-03-01",
        status=ItemStatus.RESERVED,  # Already reserved by another order
    ),
]


@pytest.fixture
def seed_items(db_session):
    """Seed the database with sample warehouse items."""
    for item in SAMPLE_ITEMS:
        # Create fresh copies to avoid SQLAlchemy state issues
        new_item = Item(
            id=item.id,
            sku=item.sku,
            name=item.name,
            category=item.category,
            weight_grams=item.weight_grams,
            width_cm=item.width_cm,
            height_cm=item.height_cm,
            depth_cm=item.depth_cm,
            shelf_location=item.shelf_location,
            status=item.status,
        )
        db_session.add(new_item)
    db_session.commit()
    return SAMPLE_ITEMS


@pytest.fixture
def seed_order_with_items(db_session, seed_items):
    """Seed a PENDING order with 3 items (ready to be picked)."""
    # Reserve the items for this order
    item_ids = ["item-001", "item-002", "item-003"]
    items = db_session.query(Item).filter(Item.id.in_(item_ids)).all()
    for item in items:
        item.status = ItemStatus.RESERVED

    # Create the order
    order = Order(
        id="order-001",
        customer_id="customer-123",
        status=OrderStatus.PENDING,
    )
    db_session.add(order)
    db_session.flush()

    # Link items to order
    for item_id in item_ids:
        db_session.add(OrderItem(order_id=order.id, item_id=item_id))

    db_session.commit()
    return order
