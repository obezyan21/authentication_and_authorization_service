from typing import Dict, Any

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from app.config import get_auth_data

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
        })
    auth_data = get_auth_data()
    try:
        encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
        return encode_jwt
    except Exception as e:
        raise ValueError(f"Failed to encode JWT: {str(e)}")

def verify_token(token: str) -> Dict[str, Any]:
    auth_data = get_auth_data()

    try:
        payload = jwt.decode(
            token,
            auth_data['secret_key'],
            algorithms=[auth_data["algorithm"]],
        )
        return payload
    except:
        raise JWTError("Invalid token")
