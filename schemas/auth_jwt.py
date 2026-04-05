from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent

class Auth_JWT(BaseModel):
    private_key_path: Path = BASE_DIR / 'certs' / 'private_key.pem'
    public_key_path: Path = BASE_DIR / 'certs' / 'public_key.pem'
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30