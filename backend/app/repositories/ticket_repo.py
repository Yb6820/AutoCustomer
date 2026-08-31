"""Ticket repository."""
from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import AgentGroup, AgentProfile, HumanTicket, TicketComment, TicketAssignLog
from app.repositories.base import BaseRepository


class AgentGroupRepository(BaseRepository[AgentGroup]):
    model = AgentGroup


class AgentProfileRepository(BaseRepository[AgentProfile]):
    model = AgentProfile

    async def get_by_user_id(self, user_id: int) -> Optional[AgentProfile]:
        result = await self.session.execute(
            select(AgentProfile).where(AgentProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()


class TicketRepository(BaseRepository[HumanTicket]):
    model = HumanTicket

    async def list_by_assignee(self, assignee_id: int, skip: int = 0, limit: int = 50) -> Sequence[HumanTicket]:
        result = await self.session.execute(
            select(HumanTicket)
            .where(HumanTicket.assignee_id == assignee_id)
            .order_by(HumanTicket.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list_pending(self, skip: int = 0, limit: int = 50) -> Sequence[HumanTicket]:
        result = await self.session.execute(
            select(HumanTicket)
            .where(HumanTicket.status == 1)
            .order_by(HumanTicket.priority.desc(), HumanTicket.created_at)
            .offset(skip).limit(limit)
        )
        return result.scalars().all()