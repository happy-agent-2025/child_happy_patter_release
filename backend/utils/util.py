import argparse
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import yaml

_config_cache = None

class Util:
    
    # 判断是否是json消息
    @staticmethod
    def is_valid_iot_json(json_string) -> bool:
        """判断字符串是否为有效的 JSON 格式"""
        try:
            data = json.loads(json_string)
            # 检查是否是列表/数组
            if not isinstance(data, list):
                return False
            required_fields = {'intent', 'device', 'action', 'position', 'params'}
            for item in data:
                # 检查每个元素是否是字典
                if not isinstance(item, dict):
                    return False
                # 检查是否包含所有必需字段， set集合具有唯一性
                missing_fields = required_fields - set(item.keys())
                if missing_fields:
                    return False
                # 检查params是否是字典
                if not isinstance(item.get('params'), dict):
                    return False

                # 检查intent字段
                intent = item.get('intent')
                if not intent or intent.strip() == "":
                    return False
                if intent.lower() == "unknown":
                    return False
            return True
        except json.JSONDecodeError as e:
            return False
    @staticmethod
    def get_project_dir():
        """获取项目根目录并确保末尾有路径分隔符"""
        current_path = Path(__file__).resolve()
        for parent in current_path.parents:
            if (parent / "pyproject.toml").exists():
                return str(parent) + os.sep
            if (parent / ".git").exists():
                return str(parent) + os.sep
            if (parent / "requirements.txt").exists():
                return str(parent) + os.sep
        # 未找到标志性文件时，使用当前文件的父目录
        return str(current_path.parent.parent) + os.sep
    @staticmethod
    def get_config_file_path():
        default_config_file = "config.yaml"
        project_dir = str(Util.get_project_dir())  # 转换为字符串
        # 构建隐藏配置文件路径（使用 os.path.join 实现跨平台）
        hidden_config_path = os.path.join(project_dir, "data", f"{default_config_file}")
        print(os.path.exists(hidden_config_path))
        if os.path.exists(hidden_config_path):
            return hidden_config_path  # 返回绝对路径
        # 构建默认配置文件路径
        default_config_path = os.path.join(project_dir, default_config_file)
        return default_config_path  # 返回绝对路径（无论是否存在）

    @staticmethod
    def get_config():
        """加载配置文件"""
        global _config_cache # 使用全局变量缓存
        if _config_cache is not None:
            return _config_cache
        
        parser = argparse.ArgumentParser(description="Server configuration")
        config_file = Util.get_config_file_path()
        parser.add_argument("--config_path", type=str, default=config_file)
        args = parser.parse_args()
        print(f"Loading configuration from {args.config_path}")
        with open(args.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        # 初始化目录
        Util.init_output_dirs(config)
        _config_cache = config
        return config

    @staticmethod
    def init_output_dirs(config):
        """自动扫描所有层级的 output_dir 配置"""
        results = set()
        def _traverse(data):
            """递归遍历函数"""
            if isinstance(data, dict):
                # 先检查当前层级是否有 output_dir
                if "output_dir" in data:
                    results.add(data["output_dir"])
                # 继续深入遍历所有值
                for value in data.values():
                    _traverse(value)

            elif isinstance(data, list):
                # 遍历列表中的每个元素
                for item in data:
                    _traverse(item)

        _traverse(config)
        # 统一创建目录（保留原data目录创建）
        for dir_path in results:
            try:
                os.makedirs(Util.get_project_dir() + dir_path, exist_ok=True)
            except PermissionError:
                print(f"警告：无法创建目录 {dir_path}")

    @staticmethod
    def get_random_file_path(dir: str, ex_name: str):
        """获取随机文件保存路径"""
        file_name = f"{datetime.now().date()}_{uuid.uuid4().hex}.{ex_name}"
        file_path = os.path.join(dir, file_name)
        return file_path


if __name__ == "__main__":
    print(Util.get_project_dir())
    print(Util.get_random_file_path(Util.get_project_dir(), "mp3"))