from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from math import radians, cos, sin, asin, sqrt
from app.core.database import get_db
from app.core.security import get_current_user, require_marketplace_user
from app.models.user import User
from app.models.product import Product
from app.services.demand_alert_service import create_product_notifications
from app.schemas import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

def haversine(lat1,lon1,lat2,lon2):
    if None in (lat1,lon1,lat2,lon2): return 9999.0
    R=6371; lat1,lon1,lat2,lon2=map(radians,[lat1,lon1,lat2,lon2])
    a=sin((lat2-lat1)/2)**2+cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return round(2*R*asin(sqrt(a)),1)

@router.post("/", response_model=ProductOut, status_code=201)
async def create_product(data: ProductCreate, current_user: User = Depends(require_marketplace_user), db: AsyncSession = Depends(get_db)):
    d = data.model_dump(exclude={"broadcast_sms", "allow_location_based_alerts"})
    broadcast_sms = data.broadcast_sms
    if broadcast_sms and not current_user.is_verified:
        raise HTTPException(
            400,
            "Verify your phone with OTP before sending product SMS alerts",
        )
    if d["image_urls"]:
        d["image_url"] = d["image_urls"][0]
    if d.get("latitude") is None:
        d["latitude"] = current_user.latitude
    if d.get("longitude") is None:
        d["longitude"] = current_user.longitude
    d["district"] = d.get("district") or current_user.district
    # Normalize unit; ensure quantity_kg is stored in kg
    unit = (d.get("quantity_unit") or "kg").lower()
    if unit not in ("kg", "ton", "gram"):
        unit = "kg"
    d["quantity_unit"] = unit
    if unit == "ton":
        d["quantity_kg"] = d["quantity_kg"] * 1000
    elif unit == "gram":
        d["quantity_kg"] = d["quantity_kg"] / 1000
    product = Product(farmer_id=current_user.id, farmer=current_user, **d)
    db.add(product); await db.flush(); await db.refresh(product)
    if broadcast_sms:
        await create_product_notifications(db, product)
    return ProductOut.model_validate(product)

@router.get("/", response_model=List[ProductOut])
async def list_products(category: Optional[str]=None, district: Optional[str]=None,
    min_price: Optional[float]=None, max_price: Optional[float]=None,
    is_organic: Optional[bool]=None, farmer_id: Optional[int]=None,
    lat: Optional[float]=Query(None),
    lon: Optional[float]=Query(None), radius_km: float=200.0,
    limit: int=Query(20, le=100), offset: int=0, db: AsyncSession=Depends(get_db)):
    filters = [Product.status == "available", Product.is_active == True]
    if category: filters.append(Product.category.ilike(f"%{category}%"))
    if district: filters.append(Product.district.ilike(f"%{district}%"))
    if min_price is not None: filters.append(Product.price_per_kg >= min_price)
    if max_price is not None: filters.append(Product.price_per_kg <= max_price)
    if is_organic is not None: filters.append(Product.is_organic == is_organic)
    if farmer_id is not None: filters.append(Product.farmer_id == farmer_id)
    result = await db.execute(select(Product).options(selectinload(Product.farmer)).where(and_(*filters)).offset(offset).limit(limit))
    out = []
    for p in result.scalars().all():
        po = ProductOut.model_validate(p)
        if lat and lon and p.latitude and p.longitude:
            dist = haversine(lat,lon,p.latitude,p.longitude)
            if dist > radius_km: continue
            po.distance_km = dist
        out.append(po)
    if lat and lon: out.sort(key=lambda x: x.distance_km or 9999)
    return out

@router.get("/recommended", response_model=List[ProductOut])
async def recommended_products(
    district: Optional[str]=None,
    category: Optional[str]=None,
    limit: int=Query(8, le=20),
    radius_km: float=Query(80.0),
    max_price: Optional[float]=None,
    is_organic: Optional[bool]=None,
    lat: Optional[float]=Query(None),
    lon: Optional[float]=Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    district_name = (district or current_user.district or "").strip()
    filters = [Product.status == "available", Product.is_active == True]
    if category: filters.append(Product.category.ilike(f"%{category}%"))
    if max_price is not None: filters.append(Product.price_per_kg <= max_price)
    if is_organic is not None: filters.append(Product.is_organic == is_organic)

    result = await db.execute(select(Product).options(selectinload(Product.farmer)).where(and_(*filters)).limit(100))
    products = []
    for p in result.scalars().all():
        po = ProductOut.model_validate(p)
        same_district = bool(p.district and district_name and p.district.lower() == district_name.lower())
        if lat and lon and p.latitude and p.longitude:
            po.distance_km = haversine(lat, lon, p.latitude, p.longitude)
            if po.distance_km > radius_km and not same_district:
                continue
        elif district_name and not same_district:
            po.distance_km = 9999
        else:
            po.distance_km = 0 if same_district else 9999
        if district_name and not same_district and not (lat and lon and p.latitude and p.longitude):
            continue
        products.append(po)

    products.sort(key=lambda x: (
        0 if (x.district and district_name and x.district.lower() == district_name.lower()) else 1,
        x.distance_km if x.distance_km is not None else 9999,
        x.created_at or 0,
    ))
    return products[:limit]

@router.get("/my", response_model=List[ProductOut])
async def my_products(current_user: User = Depends(require_marketplace_user), db: AsyncSession = Depends(get_db)):
    # Only show active listings in "My Products" (soft delete sets is_active=False)
    filters = [
        Product.farmer_id == current_user.id,
        Product.is_active == True,
        Product.status == "available",
    ]
    result = await db.execute(select(Product).options(selectinload(Product.farmer)).where(and_(*filters)))
    return [ProductOut.model_validate(p) for p in result.scalars().all()]

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).options(selectinload(Product.farmer)).where(Product.id == product_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "Product not found")
    p.views_count += 1; await db.flush()
    return ProductOut.model_validate(p)

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, data: ProductUpdate, current_user: User = Depends(require_marketplace_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).options(selectinload(Product.farmer)).where(Product.id == product_id, Product.farmer_id == current_user.id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "Product not found")
    updates = data.model_dump(exclude_unset=True)
    if "image_urls" in updates and updates["image_urls"] is not None:
        updates["image_url"] = updates["image_urls"][0] if updates["image_urls"] else None
    # If unit changes, re-normalize the quantity to kg
    if "quantity_unit" in updates and updates["quantity_unit"] is not None:
        unit = updates["quantity_unit"].lower()
        if unit not in ("kg", "ton", "gram"):
            unit = "kg"
        updates["quantity_unit"] = unit
        if "quantity_kg" in updates and updates["quantity_kg"] is not None:
            if unit == "ton":
                updates["quantity_kg"] = updates["quantity_kg"] * 1000
            elif unit == "gram":
                updates["quantity_kg"] = updates["quantity_kg"] / 1000
    for k,v in updates.items(): setattr(p, k, v)
    await db.flush(); return ProductOut.model_validate(p)

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, current_user: User = Depends(require_marketplace_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.farmer_id == current_user.id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "Product not found")
    p.is_active = False; await db.flush()


@router.post("/upload-image", response_model=dict)
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_marketplace_user),
):
    # Validate file type
    allowed = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Only JPG, PNG, WEBP images allowed")

    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, "Image must be under 5MB")

    import os
    import uuid

    # In docker-compose we mount host ./uploads to container /app/uploads
    upload_dir = os.path.join("/app/uploads", "products")

    os.makedirs(upload_dir, exist_ok=True)

    ext = (file.filename.split(".")[-1] or "jpg").lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        ext = "jpg"

    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as uploaded_file:
        uploaded_file.write(contents)

    image_url = f"/uploads/products/{filename}"
    return {"image_url": image_url, "filename": filename}


@router.post("/upload-media", response_model=dict)
async def upload_product_media(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_marketplace_user),
):
    import os
    import uuid

    if not files:
        raise HTTPException(400, "Select at least one photo or video")

    image_extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    video_extensions = {
        "video/mp4": ".mp4",
        "video/webm": ".webm",
        "video/ogg": ".ogv",
    }
    media_files = []
    for file in files:
        content_type = file.content_type or ""
        extension = image_extensions.get(content_type) or video_extensions.get(content_type)
        if extension is None:
            raise HTTPException(400, "Use JPG, PNG, WEBP photos or MP4, WEBM, OGG videos")
        media_files.append((file, extension, content_type in video_extensions))
    if sum(is_video for _, _, is_video in media_files) > 1:
        raise HTTPException(400, "Upload only one video per product")

    image_urls = []
    video_url = None
    total_size = 0
    prepared_media = []
    upload_dir = os.path.join("/app/uploads", "products")
    os.makedirs(upload_dir, exist_ok=True)

    for file, extension, is_video in media_files:
        max_size = 50 * 1024 * 1024 if is_video else 5 * 1024 * 1024
        contents = await file.read(max_size + 1)
        if not contents:
            raise HTTPException(400, "Selected media file is empty")
        if len(contents) > max_size:
            label = "Video" if is_video else "Photo"
            raise HTTPException(400, f"{label} must be under {max_size // (1024 * 1024)}MB")
        total_size += len(contents)
        if total_size > 60 * 1024 * 1024:
            raise HTTPException(400, "Selected media must total less than 60MB")
        prepared_media.append((extension, is_video, contents))

    for extension, is_video, contents in prepared_media:
        filename = f"{uuid.uuid4().hex}{extension}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, "wb") as uploaded_file:
            uploaded_file.write(contents)
        media_url = f"/uploads/products/{filename}"

        if is_video:
            video_url = media_url
        else:
            image_urls.append(media_url)

    return {"image_urls": image_urls, "video_url": video_url}
