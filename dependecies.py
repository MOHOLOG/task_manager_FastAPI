from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from crud import user as crud
import jwt
from auth import utils
from models.user import User

# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

http_bearer = HTTPBearer() #class instance for taking Bearer token from the header

def get_current_token_payload(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
    try:
        token = credentials.credentials
        payload = utils.decode_jwt(token)
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user(payload: dict = Depends(get_current_token_payload), db: Session = Depends(get_db)):
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = crud.get_user_by_username(username=username, db=db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    
    return current_user