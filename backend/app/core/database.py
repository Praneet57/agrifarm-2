from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def _ensure_columns(conn):
    """Add missing columns to existing tables (create_all only creates tables)."""
    from sqlalchemy import text

    # products: quantity_unit
    prod_cols = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='products'"
    ))
    prod_existing = {r[0] for r in prod_cols.fetchall()}
    if "quantity_unit" not in prod_existing:
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN quantity_unit VARCHAR(10) DEFAULT 'kg'"
        ))
    if "image_urls" not in prod_existing:
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN image_urls JSON NOT NULL DEFAULT '[]'"
        ))
    if "video_url" not in prod_existing:
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN video_url VARCHAR(500) NULL"
        ))
    if "pickup_address" not in prod_existing:
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN pickup_address TEXT NULL"
        ))
    # orders: district, latitude, longitude
    order_cols = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='orders'"
    ))
    existing = {r[0] for r in order_cols.fetchall()}
    if "district" not in existing:
        await conn.execute(text(
            "ALTER TABLE orders ADD COLUMN district VARCHAR(100) NULL"
        ))
    if "latitude" not in existing:
        await conn.execute(text(
            "ALTER TABLE orders ADD COLUMN latitude FLOAT NULL"
        ))
    if "longitude" not in existing:
        await conn.execute(text(
            "ALTER TABLE orders ADD COLUMN longitude FLOAT NULL"
        ))
    if "dispatched_at" not in existing:
        await conn.execute(text(
            "ALTER TABLE orders ADD COLUMN dispatched_at TIMESTAMP WITH TIME ZONE NULL"
        ))

    user_cols = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='users'"
    ))
    user_existing = {r[0] for r in user_cols.fetchall()}
    user_columns = {
        "farmer_conversion_status": "VARCHAR(20) NULL",
        "farmer_terms_accepted": "BOOLEAN DEFAULT FALSE",
        "farmer_conversion_requested_at": "TIMESTAMP WITH TIME ZONE NULL",
        "farmer_conversion_reviewed_at": "TIMESTAMP WITH TIME ZONE NULL",
        "farmer_conversion_reviewed_by": "INTEGER NULL",
        "taluk": "VARCHAR(100) NULL",
        "area": "VARCHAR(150) NULL",
        "door_no_farm": "VARCHAR(150) NULL",
        "purpose": "VARCHAR(20) NULL",
        "products_to_sell": "VARCHAR(500) NULL",
        "products_to_buy": "VARCHAR(500) NULL",
        "farm_type": "VARCHAR(150) NULL",
        "farm_agriculture_details": "VARCHAR(1000) NULL",
        "preferred_language": "VARCHAR(2) NOT NULL DEFAULT 'en'",
    }
    for name, definition in user_columns.items():
        if name not in user_existing:
            await conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))

    demand_cols = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='demands'"
    ))
    demand_existing = {r[0] for r in demand_cols.fetchall()}
    for name in ("is_urgent", "allow_location_based_alerts"):
        if name not in demand_existing:
            await conn.execute(text(
                f"ALTER TABLE demands ADD COLUMN {name} BOOLEAN NOT NULL DEFAULT FALSE"
            ))
    if "sms_alerts_opt_in" not in user_existing:
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN sms_alerts_opt_in BOOLEAN NOT NULL DEFAULT FALSE"
        ))
    if "sms_alert_consent_at" not in user_existing:
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN sms_alert_consent_at TIMESTAMP WITH TIME ZONE NULL"
        ))
    if "sms_alerts_opted_out_at" not in user_existing:
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN sms_alerts_opted_out_at TIMESTAMP WITH TIME ZONE NULL"
        ))
    if "share_location_for_alerts" not in user_existing:
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN share_location_for_alerts BOOLEAN NOT NULL DEFAULT FALSE"
        ))
    if "location_sharing_consent_at" not in user_existing:
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN location_sharing_consent_at TIMESTAMP WITH TIME ZONE NULL"
        ))
    await conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_users_alert_coordinates ON users (latitude, longitude)"
    ))
    notification_cols = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='demand_sms_notifications'"
    ))
    notification_existing = {r[0] for r in notification_cols.fetchall()}
    notification_columns = {
        "delivered_at": "TIMESTAMP WITH TIME ZONE NULL",
        "provider_updated_at": "TIMESTAMP WITH TIME ZONE NULL",
        "provider_status": "VARCHAR(24) NULL",
    }
    for name, definition in notification_columns.items():
        if notification_existing and name not in notification_existing:
            await conn.execute(text(
                f"ALTER TABLE demand_sms_notifications ADD COLUMN {name} {definition}"
            ))
async def init_db():
    from app.models import user, product, demand, order, payment, support, demand_notification  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_columns(conn)
