from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import category as crud
from database import get_db
from dependecies import get_current_user
from models.user import User
from schemas.category import CategoryCreate, CategoryResponse, PaginatedCategoryResponse
from schemas.sort import SortOrder

router = APIRouter()


@router.post("/categories")
async def create_category(
    category: CategoryCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    current_user_id = current_user.id
    category_name = await crud.create_category(
        category=category, user_id=current_user_id, db=db
    )

    return {"message": "Category created successfully", "category name": category_name}


@router.get("/categories", response_model=PaginatedCategoryResponse)
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    searched_name: Annotated[str | None, Query(alias="name")] = None,
    sort_parameter: Annotated[SortOrder, Query(alias="sort")] = SortOrder.alphabetic,
):

    categories, total, has_more = await crud.get_categories(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        searched_name=searched_name,
        sort_parameter=sort_parameter,
    )

    return PaginatedCategoryResponse(
        categories=[CategoryResponse.model_validate(c) for c in categories],
        skip=skip,
        limit=limit,
        total=total,
        has_more=has_more,
    )


@router.patch("/categories/{category_id}")
async def edit_category(
    category_id: int,
    new_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        category = await crud.edit_category(
            category_id=category_id, user_id=current_user.id, new_name=new_name, db=db
        )

        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Category updated successfully", "new category name": new_name}


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    current_user_id = current_user.id

    res = await crud.delete_category(
        category_id=category_id, user_id=current_user_id, db=db
    )
    if res is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category deleted successfully", "category id": category_id}
