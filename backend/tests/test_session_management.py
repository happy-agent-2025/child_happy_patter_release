import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from auth.auth_utils import get_current_user

client = TestClient(app)


def test_update_session_title_success():
    """测试更新会话标题成功"""
    # 直接patch整个函数而不是逐个patch方法
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session, \
         patch('api.routes.get_db') as mock_get_db, \
         patch('sqlalchemy.orm.session.Session.refresh') as mock_refresh:
        
        # 创建一个简单的session对象
        class SimpleSession:
            def __init__(self):
                self.id = 1
                self.user_id = 1
                self.title = "Old Title"
                self.is_active = 1
        
        session = SimpleSession()
        
        mock_get_session.return_value = session
        
        # Mock数据库会话
        mock_db = MagicMock()
        mock_db.commit = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock db.refresh 方法
        mock_refresh.return_value = None
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.put(
                "/api/sessions/1/title?title=New%20Title"
            )
            
            assert response.status_code == 200
            assert response.json()["session_id"] == 1
            assert response.json()["title"] == "New Title"
            assert response.json()["message"] == "会话标题更新成功"
            
            # 验证会话标题被更新
            assert session.title == "New Title"
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()


def test_update_session_title_not_found():
    """测试更新不存在的会话标题"""
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session:
        
        mock_get_session.return_value = None
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.put(
                "/api/sessions/999/title?title=New%20Title"
            )
            
            assert response.status_code == 404
            assert "会话未找到" in response.json()["detail"]
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()


def test_update_session_title_unauthorized():
    """测试无权限更新会话标题"""
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session:
        
        # 创建一个session对象，user_id与当前用户不匹配
        class SimpleSession:
            def __init__(self):
                self.id = 1
                self.user_id = 2  # 不同的用户ID
                self.title = "Old Title"
                self.is_active = 1
        
        session = SimpleSession()
        mock_get_session.return_value = session
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.put(
                "/api/sessions/1/title?title=New%20Title"
            )
            
            assert response.status_code == 403
            assert "无权修改此会话" in response.json()["detail"]
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()


def test_activate_session_success():
    """测试激活会话成功"""
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session, \
         patch('api.routes.get_db') as mock_get_db, \
         patch('sqlalchemy.orm.session.Session.refresh') as mock_refresh:
        
        # 创建一个session对象
        class SimpleSession:
            def __init__(self):
                self.id = 1
                self.user_id = 1
                self.title = "Test Session"
                self.is_active = 0  # 初始为非活跃状态
        
        session = SimpleSession()
        
        mock_get_session.return_value = session
        
        # Mock数据库会话
        mock_db = MagicMock()
        mock_db.commit = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock db.refresh 方法
        mock_refresh.return_value = None
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.post(
                "/api/sessions/1/activate"
            )
            
            assert response.status_code == 200
            assert response.json()["session_id"] == 1
            assert response.json()["is_active"] is True
            assert response.json()["message"] == "会话已激活"
            
            # 验证会话被激活
            assert session.is_active == 1
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()


def test_activate_session_not_found():
    """测试激活不存在的会话"""
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session:
        
        mock_get_session.return_value = None
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.post(
                "/api/sessions/999/activate"
            )
            
            assert response.status_code == 404
            assert "会话未找到" in response.json()["detail"]
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()


def test_deactivate_session_success():
    """测试停用会话成功"""
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session, \
         patch('api.routes.get_db') as mock_get_db, \
         patch('sqlalchemy.orm.session.Session.refresh') as mock_refresh:
        
        # 创建一个session对象
        class SimpleSession:
            def __init__(self):
                self.id = 1
                self.user_id = 1
                self.title = "Test Session"
                self.is_active = 1  # 初始为活跃状态
        
        session = SimpleSession()
        
        mock_get_session.return_value = session
        
        # Mock数据库会话
        mock_db = MagicMock()
        mock_db.commit = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock db.refresh 方法
        mock_refresh.return_value = None
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.post(
                "/api/sessions/1/deactivate"
            )
            
            assert response.status_code == 200
            assert response.json()["session_id"] == 1
            assert response.json()["is_active"] is False
            assert response.json()["message"] == "会话已停用"
            
            # 验证会话被停用
            assert session.is_active == 0
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()


def test_deactivate_session_not_found():
    """测试停用不存在的会话"""
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session:
        
        mock_get_session.return_value = None
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.post(
                "/api/sessions/999/deactivate"
            )
            
            assert response.status_code == 404
            assert "会话未找到" in response.json()["detail"]
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()


def test_deactivate_session_unauthorized():
    """测试无权限停用会话"""
    with patch('api.routes.DatabaseService.get_session_by_id') as mock_get_session:
        
        # 创建一个session对象，user_id与当前用户不匹配
        class SimpleSession:
            def __init__(self):
                self.id = 1
                self.user_id = 2  # 不同的用户ID
                self.title = "Test Session"
                self.is_active = 1
        
        session = SimpleSession()
        mock_get_session.return_value = session
        
        # 创建依赖项覆盖来模拟认证
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        try:
            response = client.post(
                "/api/sessions/1/deactivate"
            )
            
            assert response.status_code == 403
            assert "无权操作此会话" in response.json()["detail"]
        finally:
            # 清除依赖项覆盖
            app.dependency_overrides.clear()