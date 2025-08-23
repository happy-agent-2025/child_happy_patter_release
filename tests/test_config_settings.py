import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings


class TestConfigSettings:
    """测试配置设置模块"""

    def test_settings_default_values(self):
        """测试配置默认值"""
        settings = Settings()
        
        # 验证默认值
        assert settings.database_url == "sqlite:///./happy_partner.db"
        assert settings.secret_key == "your-secret-key-here"
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
        assert settings.audio_sample_rate == 16000

    def test_settings_custom_values(self):
        """测试自定义配置值"""
        # 保存原始环境变量
        original_env = dict(os.environ)
        
        try:
            # 设置环境变量
            os.environ["DATABASE_URL"] = "postgresql://user:password@localhost/testdb"
            os.environ["SECRET_KEY"] = "test-secret-key"
            os.environ["ALGORITHM"] = "HS512"
            os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
            os.environ["AUDIO_SAMPLE_RATE"] = "44100"
            
            # 重新导入模块以应用环境变量
            import importlib
            import config.settings
            importlib.reload(config.settings)
            
            settings = config.settings.Settings()
            
            # 验证环境变量值
            assert settings.database_url == "postgresql://user:password@localhost/testdb"
            assert settings.secret_key == "test-secret-key"
            assert settings.algorithm == "HS512"
            assert settings.access_token_expire_minutes == 60
            assert settings.audio_sample_rate == 44100
        finally:
            # 恢复原始环境变量
            os.environ.clear()
            os.environ.update(original_env)
            # 重新导入模块以恢复默认值
            import config.settings
            importlib.reload(config.settings) # type: ignore