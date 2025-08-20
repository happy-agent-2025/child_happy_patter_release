from passlib.context import CryptContext # type: ignore
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import os

# 简化配置处理，避免相对导入问题
class SimpleSettings:
    secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")
    algorithm = os.environ.get("ALGORITHM", "HS256")

settings = SimpleSettings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    验证明文密码与哈希密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    获取密码的哈希值
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt