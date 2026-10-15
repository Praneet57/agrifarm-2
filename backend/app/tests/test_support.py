import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestCustomerSupport:
    async def test_buyer_messages_reach_admin_and_admin_can_reply(
        self, client: AsyncClient, farmer_token, buyer_token
    ):
        farmer = (
            await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {farmer_token}"},
            )
        ).json()
        product = await client.post(
            "/api/v1/products",
            headers={"Authorization": f"Bearer {farmer_token}"},
            json={
                "name": "Support Test Tomatoes",
                "category": "Vegetables",
                "quantity_kg": 25,
                "price_per_kg": 40,
            },
        )
        order = await client.post(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "product_id": product.json()["id"],
                "farmer_id": farmer["id"],
                "quantity_kg": 2,
                "price_per_kg": 40,
                "delivery_address": "12 Market Road",
                "district": "Chennai",
            },
        )
        assert order.status_code == 201

        headers = {"Authorization": f"Bearer {buyer_token}"}
        created = await client.post(
            "/api/v1/support/tickets",
            headers=headers,
            json={
                "order_id": order.json()["id"],
                "subject": "Delivery update",
                "message": "Please confirm the delivery date.",
            },
        )
        assert created.status_code == 201
        ticket = created.json()
        assert ticket["order_number"] == order.json()["order_number"]
        assert ticket["messages"][0]["message"] == "Please confirm the delivery date."

        farmer_read = await client.get(
            f"/api/v1/support/tickets/{ticket['id']}",
            headers={"Authorization": f"Bearer {farmer_token}"},
        )
        assert farmer_read.status_code == 403

        registered = await client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Support Admin",
                "phone": "9111111099",
                "password": "admin123",
                "role": "admin",
            },
        )
        assert registered.status_code == 201
        logged_in = await client.post(
            "/api/v1/auth/login",
            json={"phone": "9111111099", "password": "admin123"},
        )
        admin_headers = {"Authorization": f"Bearer {logged_in.json()['access_token']}"}

        inbox = await client.get("/api/v1/support/admin/tickets", headers=admin_headers)
        assert inbox.status_code == 200
        assert any(item["id"] == ticket["id"] for item in inbox.json())

        reply = await client.post(
            f"/api/v1/support/tickets/{ticket['id']}/messages",
            headers=admin_headers,
            json={"message": "We are checking with the farmer."},
        )
        assert reply.status_code == 200
        assert reply.json()["status"] == "awaiting_customer"

        thread = await client.get(
            f"/api/v1/support/tickets/{ticket['id']}",
            headers=headers,
        )
        assert thread.status_code == 200
        assert thread.json()["messages"][-1]["sender_role"] == "admin"
        assert thread.json()["messages"][-1]["message"] == "We are checking with the farmer."

        buyer_reply = await client.post(
            f"/api/v1/support/tickets/{ticket['id']}/messages",
            headers=headers,
            json={"message": "Thank you, please update me when confirmed."},
        )
        assert buyer_reply.status_code == 200
        assert buyer_reply.json()["status"] == "open"

    async def test_farmer_cannot_open_customer_support_ticket(
        self, client: AsyncClient, farmer_token
    ):
        response = await client.post(
            "/api/v1/support/tickets",
            headers={"Authorization": f"Bearer {farmer_token}"},
            json={"subject": "Help request", "message": "Need help"},
        )
        assert response.status_code == 403
