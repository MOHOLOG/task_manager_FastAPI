from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models.category import Category
from schemas.sort import SortOrder
from schemas.category import CategoryCreate



def get_categories(user_id: int, 
                   skip: int, 
                   limit: int, 
                   searched_name: str | None, 
                   sort_parameter: SortOrder, 
                   db: Session, ):
    
    base_query = select(Category).where(Category.user_id == user_id)

    if searched_name:
        base_query = base_query.where(Category.name.icontains(searched_name))
    
    count_result = db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar() or 0

    if sort_parameter == SortOrder.alphabetic:
        base_query = base_query.order_by(Category.name.asc())

    final_query = base_query.offset(skip).limit(limit)
    categories = db.execute(final_query).scalars().all()
    
    has_more = skip + len(categories) < total

    return categories, total, has_more

def create_category(category: CategoryCreate,
                    user_id: int,
                    db: Session):
    
    category_name = category.name
    new_category = Category(name=category_name, user_id=user_id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return category_name

def edit_category(category_id: int,
                  user_id: int,
                  new_name: str,
                  db: Session):
    
    base_query = select(Category).where(Category.id == category_id, Category.user_id == user_id)
    category = db.execute(base_query).scalar_one_or_none()

    if category is None:
        return None
    
    existing_name_query = select(Category).where(Category.user_id == user_id, Category.name == new_name)
    category_exists = db.execute(existing_name_query).scalar_one_or_none()

    if category_exists:
        raise ValueError("A category with this name already exists!")
        
    category.name = new_name
    db.commit()
    db.refresh(category)

    return category


def delete_category(category_id: int,
                    user_id: int,
                    db: Session):
    
    category_to_delete = db.execute(select(Category).where(Category.id == category_id, Category.user_id == user_id)).scalar_one_or_none()

    if category_to_delete is None:
        return None
    
    db.delete(category_to_delete)
    db.commit()

    return category_to_delete