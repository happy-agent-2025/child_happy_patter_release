import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from auth.auth_utils import verify_password, get_password_hash, create_access_token


class TestAuthUtils:
    """测试认证工具函数"""
    
    def test_verify_password_success(self):
        """测试密码验证成功"""
        with patch('auth.auth_utils.pwd_context') as mock_context:
            mock_context.verify.return_value = True
            
            result = verify_password("plain_password", "hashed_password")
            assert result is True
            mock_context.verify.assert_called_once_with("plain_password", "hashed_password")
    
    def test_verify_password_failure(self):
        """测试密码验证失败"""
        with patch('auth.auth_utils.pwd_context') as mock_context:
            mock_context.verify.return_value = False
            
            result = verify_password("wrong_password", "hashed_password")
            assert result is False
    
    def test_get_password_hash(self):
        """测试获取密码哈希值"""
        with patch('auth.auth_utils.pwd_context') as mock_context:
            mock_context.hash.return_value = "hashed_password"
            
            result = get_password_hash("plain_password")
            assert result == "hashed_password"
            mock_context.hash.assert_called_once_with("plain_password")
    
    def test_create_access_token_default_expiry(self):
        """测试创建访问令牌（默认过期时间）"""
        with patch('auth.auth_utils.jwt') as mock_jwt:
            with patch('auth.auth_utils.settings') as mock_settings:
                mock_settings.secret_key = "test_secret_key"
                mock_settings.algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 30  # 添加这个属性
                
                mock_jwt.encode.return_value = "test_token"
                
                data = {"sub": "test_user"}
                result = create_access_token(data)
                
                assert result == "test_token"
                mock_jwt.encode.assert_called_once()
    
    def test_create_access_token_custom_expiry(self):
        """测试创建访问令牌（自定义过期时间）"""
        with patch('auth.auth_utils.jwt') as mock_jwt:
            with patch('auth.auth_utils.settings') as mock_settings:
                mock_settings.secret_key = "test_secret_key"
                mock_settings.algorithm = "HS256"
                
                mock_jwt.encode.return_value = "test_token"
                
                data = {"sub": "test_user"}
                expires_delta = timedelta(minutes=60)
                result = create_access_token(data, expires_delta)
                
                assert result == "test_token"
                mock_jwt.encode.assert_called_once()