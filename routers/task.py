from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from schemas.task import TaskCreate, TaskResponse, TaskUpdate, PaginatedTaskResponse
from schemas.sort import SortOrder
from crud import task as crud
from models.user import User
from models.task import Task
from database import get_db
from dependecies import get_current_user

router = APIRouter()

@router.post("/tasks")
async def create_task(task: TaskCreate, 
                db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    res = await crud.create_task(task=task, user_id=current_user.id, db=db)

    if res is None:
        raise HTTPException(status_code=404, detail="Category not found")
        
    new_task_id, new_task_title, category_name, subtasks_amount = res
    
    return {
        "message": "Task added",
        "task_id": new_task_id,
        "task_title": new_task_title,
        "category": category_name,
        "amount of subtasks": subtasks_amount
    }


@router.get("/tasks", response_model=PaginatedTaskResponse)
async def get_all_tasks(
    current_user: User = Depends(get_current_user),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    searched_title: Annotated[str | None, Query(alias="title")] = None,
    sort_parameter: Annotated[SortOrder, Query(alias="sort")] = SortOrder.newest,
    db: AsyncSession = Depends(get_db)
):
    tasks, total, has_more = await crud.get_all_tasks(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit, 
        searched_title=searched_title, 
        sort_parameter=sort_parameter
    )

    return PaginatedTaskResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        skip=skip,
        limit=limit,
        total=total,
        has_more=has_more
    )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_single_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    task = await crud.get_single_task(user_id=current_user.id, task_id=task_id, db=db)
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.patch("/tasks/{task_id}")
async def edit_task(task_id: int, 
              task: TaskUpdate, 
              current_user: User = Depends(get_current_user),
              db: AsyncSession = Depends(get_db)):
    
    current_user_id = current_user.id
    res = await crud.edit_task(task_id=task_id, task=task, user_id=current_user_id, db=db)
    if res is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "message": "Task edited", 
        "task_id": task_id,
        "new_title": task.title
        }


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, 
                db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    current_user_id = current_user.id  
    res = await crud.delete_task(task_id=task_id, user_id=current_user_id, db=db)
    if res is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Tasks deleted", "task_id": task_id}

@router.post("/tasks/{task_id}/subtasks")
async def add_subtask(subtask: TaskCreate,
                task_id: int,
                current_user: User = Depends(get_current_user),
                db: AsyncSession = Depends(get_db)):
    
    current_user_id = current_user.id
    new_subtask = await crud.add_subtask_to_task(subtask=subtask, user_id=current_user_id, task_id=task_id, db=db)

    if new_subtask is None:
        raise HTTPException(status_code=404, detail="Parent not found")

    return{
        "message": "Subtask successfully added to the task",
        "subtask title": new_subtask.title,
        "task_id": new_subtask.parent_id
    }

@router.get("/tasks/{task_id}/subtasks")
async def get_subtasks(    
    task_id: int,
    current_user: User = Depends(get_current_user),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    searched_title: Annotated[str | None, Query(alias="title")] = None,
    sort_parameter: Annotated[SortOrder, Query(alias="sort")] = SortOrder.newest,
    db: AsyncSession = Depends(get_db)):
    
    current_user_id = current_user.id
    res = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == current_user_id))
    task = res.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    tasks, total, has_more = await crud.get_subtasks(
        task_id=task_id,
        user_id=current_user_id,
        skip=skip,
        limit=limit,
        searched_title=searched_title,
        sort_parameter=sort_parameter,
        db=db)
    
    return PaginatedTaskResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        skip=skip,
        limit=limit,
        total=total,
        has_more=has_more
    )