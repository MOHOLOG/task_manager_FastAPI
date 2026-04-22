from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.task import Task
from models.category import Category
from schemas.task import TaskCreate, TaskUpdate, PaginatedTaskResponse, TaskResponse
from schemas.sort import SortOrder



async def get_all_tasks(user_id: int, 
                  skip: int, 
                  limit: int, 
                  searched_title: str | None, 
                  sort_parameter: SortOrder,
                  db: AsyncSession):
    
    base_query = (
        select(Task)
        .options(selectinload(Task.category))
        .where(Task.user_id == user_id, Task.parent_id.is_(None))
    )

    if searched_title:
        base_query = base_query.where(Task.title.icontains(searched_title))
    
    count_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar() or 0

    if sort_parameter == SortOrder.newest:
        base_query = base_query.order_by(Task.created_at.desc())

    elif sort_parameter == SortOrder.oldest:
        base_query = base_query.order_by(Task.created_at.asc())

    elif sort_parameter == SortOrder.alphabetic:
        base_query = base_query.order_by(Task.title.asc())

    final_query = base_query.offset(skip).limit(limit)
    tasks = await db.execute(final_query)
    tasks = tasks.scalars().all()
    
    has_more = skip + len(tasks) < total

    return tasks, total, has_more

async def get_single_task(task_id: int,
                    user_id: int,
                    db:AsyncSession):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        return None
    
    return task

async def create_task(task: TaskCreate, 
                user_id: int, 
                db: AsyncSession):

    subtasks_list = task.subtasks

    subtasks_amount = len(subtasks_list)
    #This logis is for a "main" or "parent" task
    category_name = None

    if task.category_name: 
        category_name = task.category_name
        
        result = await db.execute(
            select(Category).where(
                Category.name == category_name,
                Category.user_id == user_id
            )
        )
        category_exists = result.scalar_one_or_none()

        if not category_exists:
            return None 

        new_task = Task(
            title=task.title, 
            done=task.done, 
            user_id=user_id,
            category_id=category_exists.id 
        )
            
    else:
        new_task = Task(title=task.title, done=task.done, user_id=user_id)

    db.add(new_task)
    await db.flush()

    parent_id = new_task.id
    #This logis is for subtasks of the parent task

    for subtask in subtasks_list:
        new_subtask = Task(
            title=subtask.title,
            done=subtask.done,
            user_id=user_id,
            parent_id=parent_id)
        
        db.add(new_subtask)

    await db.commit()
    await db.refresh(new_task)
    
    return new_task.id, new_task.title, category_name, subtasks_amount

async def delete_task(task_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    task_to_delete = result.scalar_one_or_none()
    if task_to_delete is None:
        return None
    
    await db.delete(task_to_delete)
    await db.commit()

    return task_to_delete

async def edit_task(task_id: int, task: TaskUpdate, user_id: int, db: AsyncSession):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    db_task = result.scalar_one_or_none()
    
    if db_task is None:
        return None

    update_data = task.model_dump(exclude_unset=True)

    if "title" in update_data:
        db_task.title = update_data["title"]
        
    if "done" in update_data:
        db_task.done = update_data["done"]

    if "category_name" in update_data:
        cat_name = update_data["category_name"]
        
        if cat_name is None:
            db_task.category_id = None
        else:
            # They sent a string, so we find the new folder
            category = (await db.execute(
                select(Category).where(Category.name == cat_name, Category.user_id == user_id)
            )).scalar_one_or_none()
            
            if category:
                db_task.category_id = category.id
            # (Optional: You could raise an error here if the category isn't found)
        
    if "subtasks" in update_data:
        new_subtasks_list = update_data["subtasks"]

        await db.execute(delete(Task).where(Task.parent_id == db_task.id))

        for subtask in new_subtasks_list:
            new_subtask = Task(
                title=subtask["title"],
                done=subtask.get("done", False),
                user_id=user_id,
                parent_id=db_task.id
            )
            db.add(new_subtask)
            
    await db.commit()
    await db.refresh(db_task)
    return db_task
    

async def add_subtask_to_task(subtask: TaskCreate,
                task_id: int,
                user_id: int,
                db: AsyncSession):
    
    parent_exists = (await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))).scalar_one_or_none()

    if parent_exists is None:
        return None

    new_subtask = Task(
        title=subtask.title,
        done=subtask.done,
        user_id=user_id,
        parent_id=task_id
    )

    db.add(new_subtask)
    await db.commit()
    await db.refresh(new_subtask)

    return new_subtask
    
async def get_subtasks(task_id: int,
                 user_id: int,
                 skip: int,
                 limit: int,
                 searched_title: str | None,
                 sort_parameter: SortOrder,
                 db: AsyncSession):
    
    base_query = select(Task).where(Task.parent_id == task_id, Task.user_id == user_id)

    if searched_title:
        base_query = base_query.where(Task.title.icontains(searched_title))

    count_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar() or 0

    if sort_parameter == SortOrder.newest:
        base_query = base_query.order_by(Task.created_at.desc())
    
    elif sort_parameter == SortOrder.oldest:
        base_query = base_query.order_by(Task.created_at.asc())

    elif sort_parameter == SortOrder.alphabetic:
        base_query = base_query.order_by(Task.title.asc())
    
    final_query = base_query.offset(skip).limit(limit)
    tasks = (await db.execute(final_query)).scalars().all()

    has_more = skip + len(tasks) < total

    return tasks, total, has_more