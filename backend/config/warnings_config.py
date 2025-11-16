"""
警告和日志配置
用于抑制第三方库的弃用警告和配置日志级别
"""
import warnings
import logging
import sys

def configure_warnings():
    """
    配置警告过滤器
    抑制第三方库的弃用警告
    """
    # 使用更严格的警告过滤
    warnings.filterwarnings("ignore")

    # 如果需要，可以重新启用特定类型的警告
    # warnings.filterwarnings("default", category=SyntaxWarning)

    print("警告过滤器已配置")

def configure_logging():
    """
    配置日志级别
    减少第三方库的日志输出
    """
    # 设置 comtypes 日志级别为 WARNING 或更高，减少 INFO 输出
    logging.getLogger('comtypes').setLevel(logging.WARNING)

    # 设置其他第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)

    # 配置根日志器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    print("日志配置已应用")

def setup_environment():
    """
    设置完整的运行环境
    包括警告抑制和日志配置
    """
    configure_warnings()
    configure_logging()
    print("环境配置完成")

# 如果直接运行此文件，进行配置
if __name__ == "__main__":
    setup_environment()