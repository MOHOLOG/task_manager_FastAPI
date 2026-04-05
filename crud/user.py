from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from schemas.sort import SortOrder
from auth import utils
from database import get_db

def create_user(user: UserCreate, db: Session = Depends(get_db)):
    passed_username = user.username
    passed_password = user.password

    hashed_password = utils.hash_password(passed_password)    
    
    new_user = User(username=passed_username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_user_by_username(username: str, db: Session = Depends(get_db)):
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()

def get_users(skip: int,
              limit: int,
              searched_username: str | None,
              sort_parameter: SortOrder,
              db: Session):
    
    base_query = select(User)

    if searched_username:
        base_query = base_query.where(User.username.icontains(searched_username))

    count_result = db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar() or 0

    if sort_parameter == SortOrder.alphabetic:
        base_query = base_query.order_by(User.username.asc())

    elif sort_parameter == SortOrder.newest:
        base_query = base_query.order_by(User.created_at.desc())
    
    elif sort_parameter == SortOrder.oldest:
        base_query = base_query.order_by(User.created_at.asc())

    final_query = base_query.offset(skip).limit(limit)
    users = db.execute(final_query).scalars().all()

    has_more = skip + len(users) < total

    return users, total, has_more

def edit_user(current_user: User,
              new_username: str | None,
              new_password: str | None,
              current_password: str | None,
              db: Session):
    
    if new_password and current_password:
        if not utils.verify_password(current_password.encode("utf-8"), current_user.hashed_password.encode("utf-8")):
            raise ValueError("Incorrect current password")
        
        current_user.hashed_password = utils.hash_password(new_password)
    
    else:
        raise ValueError("Enter current password")

    if new_username:
        current_user.username = new_username

    db.commit()
    db.refresh(current_user)

    return current_user