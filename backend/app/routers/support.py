from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, require_admin, require_buyer
from app.models.order import Order
from app.models.support import SupportMessage, SupportTicket
from app.models.user import User


router = APIRouter(prefix="/support", tags=["Customer Support"])


class SupportTicketCreate(BaseModel):
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=1, max_length=4000)
    order_id: Optional[int] = None


class SupportMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class SupportTicketStatusUpdate(BaseModel):
    status: str


def _ticket_payload(ticket: SupportTicket):
    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "status": ticket.status,
        "order_id": ticket.order_id,
        "order_number": ticket.order.order_number if ticket.order else None,
        "user_id": ticket.user_id,
        "customer_name": ticket.user.full_name,
        "customer_phone": ticket.user.phone,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "messages": [
            {
                "id": message.id,
                "sender_id": message.sender_id,
                "sender_name": message.sender.full_name,
                "sender_role": message.sender.role,
                "message": message.message,
                "created_at": message.created_at,
            }
            for message in sorted(ticket.messages, key=lambda item: item.created_at or datetime.min.replace(tzinfo=timezone.utc))
        ],
    }


def _ticket_query():
    return select(SupportTicket).options(
        selectinload(SupportTicket.user),
        selectinload(SupportTicket.order),
        selectinload(SupportTicket.messages).selectinload(SupportMessage.sender),
    )


async def _get_accessible_ticket(ticket_id: int, db: AsyncSession, current_user: User):
    result = await db.execute(_ticket_query().where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(404, "Support conversation not found")
    if current_user.role != "admin" and ticket.user_id != current_user.id:
        raise HTTPException(403, "Not your support conversation")
    return ticket


@router.post("/tickets", status_code=201)
async def create_support_ticket(
    data: SupportTicketCreate,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db),
):
    subject = data.subject.strip()
    message_text = data.message.strip()
    if len(subject) < 3 or not message_text:
        raise HTTPException(422, "A subject and message are required")

    order = None
    if data.order_id is not None:
        result = await db.execute(
            select(Order).where(Order.id == data.order_id, Order.buyer_id == current_user.id)
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise HTTPException(404, "Purchase order not found")

    ticket = SupportTicket(
        user_id=current_user.id,
        order_id=order.id if order else None,
        subject=subject,
    )
    message = SupportMessage(sender_id=current_user.id, message=message_text)
    ticket.messages.append(message)
    db.add(ticket)
    await db.flush()
    result = await db.execute(_ticket_query().where(SupportTicket.id == ticket.id))
    return _ticket_payload(result.scalar_one())


@router.get("/tickets/my")
async def list_my_support_tickets(
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        _ticket_query()
        .where(SupportTicket.user_id == current_user.id)
        .order_by(SupportTicket.updated_at.desc(), SupportTicket.id.desc())
    )
    return [_ticket_payload(ticket) for ticket in result.scalars().all()]


@router.get("/admin/tickets")
async def list_admin_support_tickets(
    status: Optional[str] = Query(default=None, max_length=30),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = _ticket_query()
    if status:
        query = query.where(SupportTicket.status == status)
    result = await db.execute(
        query.order_by(SupportTicket.updated_at.desc(), SupportTicket.id.desc())
    )
    return [_ticket_payload(ticket) for ticket in result.scalars().all()]


@router.get("/tickets/{ticket_id}")
async def get_support_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = await _get_accessible_ticket(ticket_id, db, current_user)
    return _ticket_payload(ticket)


@router.post("/tickets/{ticket_id}/messages")
async def reply_to_support_ticket(
    ticket_id: int,
    data: SupportMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = await _get_accessible_ticket(ticket_id, db, current_user)
    if current_user.role not in ("buyer", "admin"):
        raise HTTPException(403, "Customer support is available to buyers and admins")
    message_text = data.message.strip()
    if not message_text:
        raise HTTPException(422, "A message is required")
    if current_user.role == "buyer":
        ticket.status = "open"
    else:
        ticket.status = "awaiting_customer"

    ticket.updated_at = datetime.now(timezone.utc)
    db.add(SupportMessage(ticket_id=ticket.id, sender_id=current_user.id, message=message_text))
    await db.flush()
    result = await db.execute(_ticket_query().where(SupportTicket.id == ticket.id))
    return _ticket_payload(result.scalar_one())


@router.patch("/admin/tickets/{ticket_id}")
async def update_support_ticket_status(
    ticket_id: int,
    data: SupportTicketStatusUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if data.status not in ("open", "awaiting_customer", "resolved"):
        raise HTTPException(400, "Status must be open, awaiting_customer, or resolved")
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(404, "Support conversation not found")
    ticket.status = data.status
    ticket.updated_at = datetime.now(timezone.utc)
    await db.flush()
    refreshed = await _get_accessible_ticket(ticket_id, db, _admin)
    return _ticket_payload(refreshed)
