import pytest
from httpx import AsyncClient
pytestmark = pytest.mark.asyncio

class TestProducts:
    async def test_create_product(self, client: AsyncClient, farmer_token):
        r = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name":"Test Mangoes","category":"Fruits","quantity_kg":500,"price_per_kg":120,"is_organic":True,
                  "harvest_date":"2026-10-01T00:00:00Z","expiry_date":"2026-10-15T00:00:00Z"})
        assert r.status_code == 201; assert r.json()["name"] == "Test Mangoes"
        assert r.json()["harvest_date"].startswith("2026-10-01")
        assert r.json()["expiry_date"].startswith("2026-10-15")

    async def test_buyer_can_create_product(self, client: AsyncClient, buyer_token):
        r = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {buyer_token}"},
            json={"name":"X","category":"Fruits","quantity_kg":10,"price_per_kg":5})
        assert r.status_code == 201

    async def test_list_products(self, client: AsyncClient):
        r = await client.get("/api/v1/products")
        assert r.status_code == 200; assert isinstance(r.json(), list)

    async def test_recommended_products_for_buyer_district(self, client: AsyncClient, farmer_token, buyer_token):
        await client.post("/api/v1/products", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name":"Chennai Rice","category":"Grains","quantity_kg":200,"price_per_kg":32,"district":"Chennai"})
        await client.post("/api/v1/products", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name":"Coimbatore Mangoes","category":"Fruits","quantity_kg":150,"price_per_kg":60,"district":"Coimbatore"})
        r = await client.get("/api/v1/products/recommended?district=Chennai", headers={"Authorization": f"Bearer {buyer_token}"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert all(item["district"] == "Chennai" for item in data)

    async def test_product_views_increment(self, client: AsyncClient, farmer_token):
        cr = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name":"View Test","category":"Grains","quantity_kg":100,"price_per_kg":30})
        pid = cr.json()["id"]
        r = await client.get(f"/api/v1/products/{pid}")
        assert r.json()["views_count"] >= 1

class TestDemands:
    async def test_create_demand(self, client: AsyncClient, buyer_token):
        r = await client.post("/api/v1/demands", headers={"Authorization": f"Bearer {buyer_token}"},
            json={"product_name":"Tomatoes","category":"Vegetables","quantity_kg":500,"max_price_per_kg":25})
        assert r.status_code == 201

    async def test_farmer_cannot_create_demand(self, client: AsyncClient, farmer_token):
        r = await client.post("/api/v1/demands", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"product_name":"X","category":"Fruits","quantity_kg":10,"max_price_per_kg":5})
        assert r.status_code == 403

class TestOrders:
    async def test_chat_rooms_show_participant_and_latest_message(self, client: AsyncClient, farmer_token, buyer_token, db):
        from app.models.payment import ChatMessage

        farmer = (await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {farmer_token}"})).json()
        buyer = (await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {buyer_token}"})).json()
        product = await client.post(
            "/api/v1/products",
            headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name": "Chat Test Rice", "category": "Grains", "quantity_kg": 100, "price_per_kg": 45},
        )
        order = await client.post(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "product_id": product.json()["id"],
                "farmer_id": farmer["id"],
                "quantity_kg": 20,
                "price_per_kg": 45,
                "delivery_address": "Home",
                "district": "Coimbatore",
            },
        )
        assert order.status_code == 201

        db.add_all(
            [
                ChatMessage(
                    order_id=order.json()["id"],
                    sender_id=buyer["id"],
                    message="Hello",
                    message_type="text",
                ),
                ChatMessage(
                    order_id=order.json()["id"],
                    sender_id=buyer["id"],
                    message="Can you deliver tomorrow?",
                    message_type="text",
                ),
            ]
        )
        await db.flush()

        rooms = await client.get(
            "/api/v1/chat/rooms/my",
            headers={"Authorization": f"Bearer {farmer_token}"},
        )

        assert rooms.status_code == 200
        room = next(item for item in rooms.json() if item["order_id"] == order.json()["id"])
        assert room["participant_name"] == buyer["full_name"]
        assert room["last_message"] == "Can you deliver tomorrow?"
        assert room["last_message_sender_id"] == buyer["id"]
        assert room["unread_count"] == 2
        assert room["last_message_at"] is not None

    async def test_order_payload_returns_product_name(self, client: AsyncClient, farmer_token, buyer_token):
        farmer_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {farmer_token}"})
        farmer_id = farmer_me.json()["id"]

        product = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name":"Order Product Tomato","category":"Vegetables","quantity_kg":100,"price_per_kg":45,
                  "district":"Dindigul", "delivery_address":"Farm"})
        product_id = product.json()["id"]

        cr = await client.post("/api/v1/orders", headers={"Authorization": f"Bearer {buyer_token}"},
            json={"product_id":product_id,"farmer_id":farmer_id,"quantity_kg":20,"price_per_kg":45,
                  "delivery_address":"Home","district":"Dindigul"})

        assert cr.status_code == 201
        assert cr.json()["product_name"] == "Order Product Tomato"

    async def test_farmer_can_buy_product(self, client: AsyncClient, farmer_token, buyer_token):
        buyer = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {buyer_token}"})
        product = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {buyer_token}"},
            json={"name":"Buyer Listed Rice","category":"Grains","quantity_kg":100,"price_per_kg":45})
        cr = await client.post("/api/v1/orders", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"product_id":product.json()["id"],"farmer_id":buyer.json()["id"],"quantity_kg":20,"price_per_kg":45,
                  "delivery_address":"Farm","district":"Dindigul"})
        assert cr.status_code == 201

    async def test_order_lifecycle(self, client: AsyncClient, farmer_token, buyer_token):
        fm = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {farmer_token}"})
        farmer_id = fm.json()["id"]
        pr = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name":"Order Test Rice","category":"Grains","quantity_kg":100,"price_per_kg":45})
        pid = pr.json()["id"]
        cr = await client.post("/api/v1/orders", headers={"Authorization": f"Bearer {buyer_token}"},
            json={"product_id":pid,"farmer_id":farmer_id,"quantity_kg":20,"price_per_kg":45})
        assert cr.status_code == 201; oid = cr.json()["id"]
        assert cr.json()["status"] == "pending"
        ar = await client.patch(f"/api/v1/orders/{oid}/status", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"status":"accepted"})
        assert ar.json()["status"] == "accepted"
        br = await client.patch(f"/api/v1/orders/{oid}/status", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"status":"completed"})
        assert br.status_code == 400

    async def test_other_farmer_cannot_manage_order(self, client: AsyncClient, farmer_token, buyer_token):
        fm = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {farmer_token}"})
        farmer_id = fm.json()["id"]
        pr = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {farmer_token}"},
            json={"name":"Protected Grain","category":"Grains","quantity_kg":100,"price_per_kg":50})
        pid = pr.json()["id"]
        cr = await client.post("/api/v1/orders", headers={"Authorization": f"Bearer {buyer_token}"},
            json={"product_id":pid,"farmer_id":farmer_id,"quantity_kg":10,"price_per_kg":50})
        assert cr.status_code == 201; oid = cr.json()["id"]

        await client.post("/api/v1/auth/register", json={"full_name":"Other Farmer","phone":"9111111003","password":"farmer123","role":"farmer","district":"Madurai"})
        other_farmer = await client.post("/api/v1/auth/login", json={"phone":"9111111003","password":"farmer123"})
        other_farmer_token = other_farmer.json()["access_token"]

        r = await client.patch(f"/api/v1/orders/{oid}/status", headers={"Authorization": f"Bearer {other_farmer_token}"},
            json={"status":"accepted"})
        assert r.status_code == 403
