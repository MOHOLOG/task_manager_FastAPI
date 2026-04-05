from datetime import datetime, timedelta, timezone
from schemas.auth_jwt import Auth_JWT
import bcrypt
import jwt

Auth_JWT = Auth_JWT()

def verify_password(passed_password: bytes, stored_password: bytes):
    return bcrypt.checkpw(passed_password, stored_password)
    
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    return hashed_password


def encode_jwt(
        payload: dict,
        private_key: str = Auth_JWT.private_key_path.read_text(), 
        algorithm: str = Auth_JWT.algorithm,
        expire_timedelta: timedelta | None = None,
        expire_minutes: int = Auth_JWT.access_token_expire_minutes):
    
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire, "iat": now})

    encoded = jwt.encode(to_encode, private_key, algorithm)

    return encoded

def decode_jwt(
        token: str, 
        public_key: str = Auth_JWT.public_key_path.read_text(), 
        algorithm: str = Auth_JWT.algorithm):
    
    decoded = jwt.decode(token, public_key, algorithm)

    return decoded