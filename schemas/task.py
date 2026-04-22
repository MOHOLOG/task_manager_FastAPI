from pydantic import BaseModel, ConfigDict
from datetime import datetime
from schemas.category import CategoryResponse

class TaskBase(BaseModel):
    title: str
    done: bool = False

class TaskCreate(TaskBase):
    category_name: str | None = None
    subtasks: list["TaskCreate"] = []

class TaskUpdate(TaskBase):
    title: str | None = None
    done: bool | None = None
    category_name: str | None = None
    subtasks: list["TaskCreate"] = []
    parent_id: int | None = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    category: CategoryResponse | None = None
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedTaskResponse(BaseModel):
    tasks: list[TaskResponse]
    skip: int
    limit: int
    total: int
    has_more: bool
