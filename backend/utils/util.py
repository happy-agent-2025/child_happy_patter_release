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

        # 在测试环境中避免解析命令行参数
        import sys
        if 'pytest' in sys.modules or 'unittest' in sys.modules:
            # 测试环境中直接使用默认配置路径
            config_file = Util.get_config_file_path()
        else:
            # 生产环境中解析命令行参数
            parser = argparse.ArgumentParser(description="Server configuration")
            config_file = Util.get_config_file_path()
            parser.add_argument("--config_path", type=str, default=config_file)
            args = parser.parse_args()
            config_file = args.config_path

        print(f"Loading configuration from {config_file}")
        with open(config_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        config = Util.apply_env_overrides(config)
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
    def _cast_type(value, target):
        if isinstance(target, bool):
            return str(value).lower() in {"1", "true", "yes", "on"}
        if isinstance(target, int):
            try:
                return int(value)
            except Exception:
                return target
        if isinstance(target, float):
            try:
                return float(value)
            except Exception:
                return target
        return value

    @staticmethod
    def apply_env_overrides(config):
        sep = "::"
        def _flatten(prefix, node):
            items = []
            if isinstance(node, dict):
                for k, v in node.items():
                    key = f"{prefix}{sep}{k}" if prefix else str(k)
                    items.extend(_flatten(key, v))
            else:
                items.append((prefix, node))
            return items

        def _set_by_path(d, path, value):
            parts = path.split(sep)
            cur = d
            for i, p in enumerate(parts):
                if i == len(parts) - 1:
                    cur[p] = value
                else:
                    if p not in cur or not isinstance(cur[p], dict):
                        cur[p] = {}
                    cur = cur[p]

        flattened = _flatten("", config)
        for path, current in flattened:
            env_key = path.upper().replace("-", "_").replace(sep, "_")
            pref_key = f"APP_{env_key}"
            raw = os.environ.get(env_key)
            if raw is None:
                raw = os.environ.get(pref_key)
            if raw is None:
                continue
            new_val = raw
            if isinstance(current, (dict, list)):
                try:
                    parsed = json.loads(raw)
                    new_val = parsed
                except Exception:
                    continue
            else:
                new_val = Util._cast_type(raw, current)
            _set_by_path(config, path, new_val)
        return config

    @staticmethod
    def validate_config(config):
        errors = []
        warnings = []
        server = config.get("server", {})
        if not isinstance(server.get("port"), int):
            errors.append("server.port 缺失或非整数")
        if not server.get("host"):
            warnings.append("server.host 缺失，使用默认 0.0.0.0")

        select = config.get("select_model", {})
        llm_sel = select.get("LLM")
        if llm_sel == "openai":
            openai = config.get("LLM", {}).get("openai", {})
            if not openai.get("api_key"):
                errors.append("LLM.openai.api_key 未配置")
            if not openai.get("base_url"):
                warnings.append("LLM.openai.base_url 未配置，使用默认 OpenAI")
        elif llm_sel == "ollama":
            ollama = config.get("LLM", {}).get("ollama", {})
            if not ollama.get("base_url"):
                errors.append("LLM.ollama.base_url 未配置")

        asr_sel = select.get("ASR")
        if asr_sel == "FunASR":
            funasr = config.get("ASR", {}).get("FunASR", {})
            if not funasr.get("model_dir"):
                errors.append("ASR.FunASR.model_dir 未配置")
            elif not os.path.exists(os.path.join(Util.get_project_dir(), funasr.get("model_dir"))):
                warnings.append("ASR.FunASR.model_dir 路径不存在")

        vad_sel = select.get("VAD")
        if vad_sel == "Silero":
            silero = config.get("VAD", {}).get("Silero", {})
            if not silero.get("model_dir"):
                errors.append("VAD.Silero.model_dir 未配置")
            elif not os.path.exists(os.path.join(Util.get_project_dir(), silero.get("model_dir"))):
                warnings.append("VAD.Silero.model_dir 路径不存在")

        if errors:
            raise ValueError("配置错误: " + "; ".join(errors))
        for w in warnings:
            print("配置警告：" + w)
        return True

    @staticmethod
    def get_random_file_path(dir: str, ex_name: str):
        """获取随机文件保存路径"""
        file_name = f"{datetime.now().date()}_{uuid.uuid4().hex}.{ex_name}"
        file_path = os.path.join(dir, file_name)
        return file_path


if __name__ == "__main__":
    print(Util.get_project_dir())
    print(Util.get_random_file_path(Util.get_project_dir(), "mp3"))
