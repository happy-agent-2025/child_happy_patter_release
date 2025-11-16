from passlib.context import CryptContext # type: ignore
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.settings import settings
from utils.db.database import get_db
from utils.db.database_service import DatabaseService
from schemas.auth import TokenData

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码持有者流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """
    验证JWT令牌
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except jwt.InvalidTokenError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前认证用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token, credentials_exception)
    user = DatabaseService.get_user_by_username(db, username=token_data.username) # type: ignore
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user = Depends(get_current_user)):
    """
    获取当前活跃用户（预留功能，可用于用户状态检查）
    """
    # 这里可以添加用户状态检查逻辑
    return current_user