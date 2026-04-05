from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import PaginatedUserResponse, UserCreate, UserUpdate, UserResponse
from schemas.token import TokenResponse
from schemas.sort import SortOrder
from crud import user as crud
from auth import utils
from datetime import datetime
import jwt
from dependecies import get_current_user, get_current_token_payload, get_current_admin_user

router = APIRouter()

@router.post("/register")
def user_register(user: UserCreate, db: Session = Depends(get_db)):
    res = crud.get_user_by_username(username = user.username, db=db)
    if res is None:
        crud.create_user(user, db)
        return {
            "message": "User was created successfully!",
            "username": user.username
            }
    else:
        raise HTTPException(status_code=409, detail="This username is already taken")

@router.post("/login", response_model=TokenResponse)
def user_login(user: UserCreate, db: Session = Depends(get_db)):
    stored_user = crud.get_user_by_username(username=user.username, db=db)
    if stored_user:
        stored_password = stored_user.hashed_password.encode("utf-8")
        passed_password = user.password.encode("utf-8")
        is_correct_password = utils.verify_password(passed_password, stored_password)
        
        if is_correct_password:
            jwt_payload = {"sub": user.username}
            secret_token = utils.encode_jwt(jwt_payload)

            return TokenResponse(access_token=secret_token, token_type='bearer')
            
        else:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    

@router.get("/users", response_model=PaginatedUserResponse, dependencies=[Depends(get_current_admin_user)])
def get_users(skip: Annotated[int, Query(ge=0)] = 0,
              limit: Annotated[int, Query(ge=1, le=100)] = 10,
              searched_username: Annotated[str | None, Query(alias="username")] = None,
              sort_parameter: Annotated[SortOrder, Query(alias="sort")] = SortOrder.newest,
              db: Session = Depends(get_db)):
    
    users, total, has_more = crud.get_users(skip=skip,
                         limit=limit,
                         searched_username=searched_username,
                         sort_parameter=sort_parameter,
                         db=db)
    
    return PaginatedUserResponse(
        users = [UserResponse.model_validate(user) for user in users],
        total = total,
        skip = skip,
        limit = limit,
        has_more = has_more
    )

@router.get("/me")
def read_users_me(
    current_user: User = Depends(get_current_user),
    payload: dict = Depends(get_current_token_payload)
    ):

    iat = payload.get("iat", 1)
    exp = payload.get("exp", 1)
    return {
        "username": current_user.username,
        "iat": datetime.fromtimestamp(iat),
        "token_expire_time": datetime.fromtimestamp(exp)
    }

@router.patch("/users/me")
def edit_user(update_data: UserUpdate,
              current_user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    
    try:
        updated_user = crud.edit_user(
            current_user=current_user,
            new_username=update_data.username,
            new_password=update_data.password,
            current_password=update_data.current_password,
            db=db
        )

        return {
            "message": "User updated successfully!",
            "new username": updated_user.username
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

