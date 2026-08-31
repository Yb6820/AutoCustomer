"""工单接口。"""
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.services.ticket_service import TicketService

router = APIRouter()


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_no: str
    session_id: int
    reason: str | None
    status: int
    priority: int
    assignee_id: int | None
    created_at: str


class TicketCreateRequest(BaseModel):
    session_id: int
    reason: str = ""
    priority: int = 2


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = TicketService(session)
    tickets = await svc.list_pending(skip, limit)
    return [TicketResponse.model_validate(t) for t in tickets]


@router.post("", response_model=TicketResponse)
async def create_ticket(
    req: TicketCreateRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = TicketService(session)
    ticket = await svc.create_ticket(req.session_id, req.reason, req.priority)
    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    assignee_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = TicketService(session)
    try:
        await svc.assign_ticket(ticket_id, assignee_id, user.id)
        return {"message": "工单已分配"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = TicketService(session)
    try:
        await svc.resolve_ticket(ticket_id)
        return {"message": "工单已解决"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))