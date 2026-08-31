"""工单应用服务。"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import HumanTicket, TicketComment, TicketAssignLog
from app.repositories.ticket_repo import TicketRepository


class TicketService:
    """工单分配/流转/回复管理。"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ticket_repo = TicketRepository(session)

    async def create_ticket(self, session_id: int, reason: str, priority: int = 2, snapshot: dict | None = None) -> HumanTicket:
        import json
        ticket_no = f"T{datetime.utcnow().strftime('%Y%m%d')}-{await self.ticket_repo.count():04d}"
        ticket = HumanTicket(
            session_id=session_id,
            ticket_no=ticket_no,
            reason=reason,
            priority=priority,
            snapshot=json.dumps(snapshot) if snapshot else None,
            status=1,  # pending
        )
        return await self.ticket_repo.add(ticket)

    async def assign_ticket(self, ticket_id: int, assignee_id: int, operator_id: int) -> HumanTicket:
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("工单不存在")
        ticket.assignee_id = assignee_id
        ticket.status = 2  # assigned
        await self.session.flush()
        # 记录流转
        log = TicketAssignLog(
            ticket_id=ticket_id,
            to_agent_id=assignee_id,
            action="assign",
            operator_id=operator_id,
        )
        self.session.add(log)
        await self.session.flush()
        return ticket

    async def resolve_ticket(self, ticket_id: int) -> HumanTicket:
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("工单不存在")
        ticket.status = 4  # resolved
        ticket.resolved_at = datetime.utcnow()
        await self.session.flush()
        return ticket

    async def list_pending(self, skip: int = 0, limit: int = 50) -> Sequence[HumanTicket]:
        return await self.ticket_repo.list_pending(skip, limit)