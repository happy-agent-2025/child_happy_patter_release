import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)


def test_register_user_success():
    """测试用户注册成功"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    with patch('api.routes.DatabaseService.get_user_by_username') as mock_get_username, \
         patch('api.routes.DatabaseService.get_user_by_email') as mock_get_email, \
         patch('api.routes.DatabaseService.create_user') as mock_create_user:
        
        mock_get_username.return_value = None
        mock_get_email.return_value = None
        from datetime import datetime
        mock_user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime(2024, 1, 1, 0, 0, 0),
            "updated_at": datetime(2024, 1, 1, 0, 0, 0)
        }
        mock_create_user.return_value = mock_user_data
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert response.json()["email"] == "test@example.com"


def test_register_user_username_exists():
    """测试用户名已存在的情况"""
    user_data = {
        "username": "existinguser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    with patch('api.routes.DatabaseService.get_user_by_username') as mock_get_username:
        mock_get_username.return_value = MagicMock()
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]


def test_register_user_email_exists():
    """测试邮箱已存在的情况"""
    user_data = {
        "username": "newuser",
        "email": "existing@example.com",
        "password": "testpassword123"
    }
    
    with patch('api.routes.DatabaseService.get_user_by_username') as mock_get_username, \
         patch('api.routes.DatabaseService.get_user_by_email') as mock_get_email:
        
        mock_get_username.return_value = None
        mock_get_email.return_value = MagicMock()
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "邮箱已存在" in response.json()["detail"]


def test_login_user_success():
    """测试用户登录成功"""
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    with patch('api.routes.DatabaseService.get_user_by_username') as mock_get_user, \
         patch('api.routes.verify_password') as mock_verify, \
         patch('api.routes.create_access_token') as mock_create_token:
        
        mock_get_user.return_value = MagicMock(
            username="testuser",
            hashed_password="hashed_password"
        )
        mock_verify.return_value = True
        mock_create_token.return_value = "test_token"
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        assert response.json()["access_token"] == "test_token"
        assert response.json()["token_type"] == "bearer"


def test_login_user_invalid_credentials():
    """测试无效凭据登录"""
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    with patch('api.routes.DatabaseService.get_user_by_username') as mock_get_user:
        mock_get_user.return_value = None
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]


def test_login_user_wrong_password():
    """测试密码错误"""
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    with patch('api.routes.DatabaseService.get_user_by_username') as mock_get_user, \
         patch('api.routes.verify_password') as mock_verify:
        
        mock_get_user.return_value = MagicMock(
            username="testuser",
            hashed_password="hashed_password"
        )
        mock_verify.return_value = False
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]


def test_get_current_user_info_unauthorized():
    """测试未授权访问用户信息"""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_current_user_info_authorized():
    """测试授权访问用户信息"""
    with patch('auth.auth_utils.verify_token') as mock_verify_token:
        from datetime import datetime
        
        # Mock token验证返回有效用户数据
        mock_verify_token.return_value = type('obj', (object,), {
            'username': 'testuser'
        })()
        
        with patch('api.routes.DatabaseService.get_user_by_username') as mock_get_user:
            mock_get_user.return_value = {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "created_at": datetime(2024, 1, 1, 0, 0, 0),
                "updated_at": datetime(2024, 1, 1, 0, 0, 0)
            }
            
            # 使用有效的token访问
            headers = {"Authorization": "Bearer test_token"}
            response = client.get("/api/auth/me", headers=headers)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            assert response.status_code == 200
            assert response.json()["username"] == "testuser"
            assert response.json()["email"] == "test@example.com"