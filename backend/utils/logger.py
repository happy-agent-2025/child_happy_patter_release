import os
import sys
from loguru import logger

from utils.util import Util


TAG=__name__

class Logger:
    def log_init(self,name="default"):
        config =  Util.get_config()
        log_config = config["log"]
        log_format = log_config.get(
            "log_format",
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> - [<light-blue>{extra[name]}</light-blue>] - <level>{level}</level>-<light-green>{message}</light-green>",
        )
        log_format_file = log_config.get(
            "log_format_file",
            "{time:YYYY-MM-DD HH:mm:ss} - {extra[name]} - {level} - {message}",
        )

        log_level = log_config.get("level")
        log_dir = log_config.get("output_dir")
        log_file = "server.log"

        # 配置日志输出
        logger.remove()

        # 输出到控制台（绑定 name 到 extra 上下文）
        logger.add(
            sys.stdout,
            format=log_format,
            level=log_level,
        )

        # 输出到文件（绑定 name 到 extra 上下文）
        logger.add(
            os.path.join(str(Util.get_project_dir()), log_dir, log_file),
            format=log_format_file,
            level=log_level,
        )
        return logger.bind(name=name)  # 返回绑定了 name 的 logger


if  __name__ == "__main__":
    logger = Logger().log_init(TAG)
    logger.info("start")
    logger.warning("warning")
    logger.error("error")