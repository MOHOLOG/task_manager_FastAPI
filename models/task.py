from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.category import Category

class Task(Base):
    __tablename__ = 'tasks'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    category: Mapped["Category"] = relationship(back_populates="tasks")

    #actually, nullable=True was created automaticlly after i put " | None" in Mapped. but it is better to explicitly declare this parameter
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True) 
    parent: Mapped[Task | None] = relationship(back_populates="subtasks", remote_side=[id])
    subtasks: Mapped[list[Task]] = relationship(back_populates="parent")  