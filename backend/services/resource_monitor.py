"""
资源监控模块 - 用于监控系统资源使用情况
支持CPU、内存、磁盘、GPU监控，并提供日志导出功能
"""

import psutil
import threading
import time
import json
import os
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import sys


class ResourceMonitor:
    def __init__(self, interval: int = 5, log_dir: str = "logs"):
        """
        初始化资源监控器

        Args:
            interval: 监控间隔（秒）
            log_dir: 日志目录
        """
        self.interval = interval
        self.log_dir = log_dir
        self.running = False
        self.thread = None
        self.monitor_data = []

        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)

        # 配置日志
        self._setup_logging()

    def _setup_logging(self):
        """配置资源监控日志"""
        # 资源监控日志文件
        self.resource_log_path = os.path.join(self.log_dir, "resource_monitor.log")
        self.resource_csv_path = os.path.join(self.log_dir, "resource_monitor.csv")

        # 添加资源监控日志处理器
        logger.add(
            self.resource_log_path,
            rotation="1 day",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            filter=lambda record: "resource_monitor" in record["extra"]
        )

        # 创建CSV文件（如果不存在）
        if not os.path.exists(self.resource_csv_path):
            self._create_csv_header()

    def _create_csv_header(self):
        """创建CSV文件头"""
        with open(self.resource_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp', 'cpu_percent', 'memory_percent',
                'memory_used', 'memory_total', 'disk_percent',
                'disk_used', 'disk_total', 'gpu_percent',
                'gpu_memory_percent', 'gpu_temperature'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def get_system_info(self) -> Dict:
        """
        获取系统资源信息

        Returns:
            Dict: 包含系统资源信息的字典
        """
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)

            # 内存信息
            memory = psutil.virtual_memory()

            # 磁盘信息
            disk = psutil.disk_usage('/')

            # 网络信息
            network = psutil.net_io_counters()

            # 进程信息
            process = psutil.Process()
            process_info = {
                'pid': process.pid,
                'memory_percent': process.memory_percent(),
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads()
            }

            # GPU信息（如果可用）
            gpu_info = self._get_gpu_info()

            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'cpu_count': cpu_count,
                    'cpu_count_logical': cpu_count_logical,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total,
                    'memory_available': memory.available,
                    'disk_percent': disk.percent,
                    'disk_used': disk.used,
                    'disk_total': disk.total,
                    'disk_free': disk.free,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv,
                    'network_packets_sent': network.packets_sent,
                    'network_packets_recv': network.packets_recv
                },
                'process': process_info,
                'gpu': gpu_info
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}

    def _get_gpu_info(self) -> Dict:
        """获取GPU信息"""
        gpu_info = {}
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_info = {
                    'gpu_percent': gpu.load * 100,
                    'gpu_memory_percent': gpu.memoryUtil * 100,
                    'gpu_memory_used': gpu.memoryUsed,
                    'gpu_memory_total': gpu.memoryTotal,
                    'gpu_temperature': gpu.temperature,
                    'gpu_name': gpu.name,
                    'gpu_id': gpu.id
                }
        except ImportError:
            logger.warning("GPUtil库未安装，无法获取GPU信息")
        except Exception as e:
            logger.warning(f"获取GPU信息失败: {e}")

        return gpu_info

    def start_monitoring(self):
        """启动资源监控"""
        if self.running:
            logger.warning("资源监控已经在运行中")
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()

        logger.bind(resource_monitor=True).info(
            f"资源监控已启动，监控间隔: {self.interval}秒"
        )

    def stop_monitoring(self):
        """停止资源监控"""
        if not self.running:
            logger.warning("资源监控未在运行")
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

        logger.bind(resource_monitor=True).info("资源监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 获取系统信息
                data = self.get_system_info()
                if data:
                    # 记录到日志
                    self._log_resource_data(data)
                    # 保存到内存（用于API查询）
                    self.monitor_data.append(data)
                    # 限制内存中的数据量
                    if len(self.monitor_data) > 1000:
                        self.monitor_data = self.monitor_data[-500:]

                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"资源监控循环错误: {e}")
                time.sleep(self.interval)

    def _log_resource_data(self, data: Dict):
        """记录资源数据到日志文件"""
        try:
            # 记录到日志文件
            logger.bind(resource_monitor=True).info(
                f"资源使用情况: {json.dumps(data, ensure_ascii=False)}"
            )

            # 记录到CSV文件
            self._append_to_csv(data)

        except Exception as e:
            logger.error(f"记录资源数据失败: {e}")

    def _append_to_csv(self, data: Dict):
        """追加数据到CSV文件"""
        try:
            with open(self.resource_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'cpu_percent', 'memory_percent',
                    'memory_used', 'memory_total', 'disk_percent',
                    'disk_used', 'disk_total', 'gpu_percent',
                    'gpu_memory_percent', 'gpu_temperature'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                csv_row = {
                    'timestamp': data['timestamp'],
                    'cpu_percent': data['system']['cpu_percent'],
                    'memory_percent': data['system']['memory_percent'],
                    'memory_used': data['system']['memory_used'],
                    'memory_total': data['system']['memory_total'],
                    'disk_percent': data['system']['disk_percent'],
                    'disk_used': data['system']['disk_used'],
                    'disk_total': data['system']['disk_total'],
                    'gpu_percent': data['gpu'].get('gpu_percent', 0) if data['gpu'] else 0,
                    'gpu_memory_percent': data['gpu'].get('gpu_memory_percent', 0) if data['gpu'] else 0,
                    'gpu_temperature': data['gpu'].get('gpu_temperature', 0) if data['gpu'] else 0
                }
                writer.writerow(csv_row)

        except Exception as e:
            logger.error(f"写入CSV文件失败: {e}")

    def get_recent_data(self, limit: int = 100) -> List[Dict]:
        """获取最近的监控数据"""
        return self.monitor_data[-limit:] if self.monitor_data else []

    def export_data(self, start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   format: str = "json") -> str:
        """
        导出监控数据

        Args:
            start_time: 开始时间 (ISO格式)
            end_time: 结束时间 (ISO格式)
            format: 导出格式 ('json' 或 'csv')

        Returns:
            str: 导出文件的路径
        """
        try:
            if format.lower() == "csv":
                return self._export_csv(start_time, end_time)
            else:
                return self._export_json(start_time, end_time)
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return ""

    def _export_json(self, start_time: Optional[str], end_time: Optional[str]) -> str:
        """导出JSON格式数据"""
        # 过滤数据
        filtered_data = self._filter_data_by_time(start_time, end_time)

        # 生成导出文件名
        filename = f"resource_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.log_dir, filename)

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'export_time': datetime.now().isoformat(),
                'data_count': len(filtered_data),
                'data': filtered_data
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"数据已导出到: {filepath}")
        return filepath

    def _export_csv(self, start_time: Optional[str], end_time: Optional[str]) -> str:
        """导出CSV格式数据"""
        # 过滤数据
        filtered_data = self._filter_data_by_time(start_time, end_time)

        # 生成导出文件名
        filename = f"resource_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.log_dir, filename)

        # 写入CSV文件
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp', 'cpu_percent', 'memory_percent',
                'memory_used', 'memory_total', 'disk_percent',
                'disk_used', 'disk_total', 'gpu_percent',
                'gpu_memory_percent', 'gpu_temperature'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for data in filtered_data:
                csv_row = {
                    'timestamp': data['timestamp'],
                    'cpu_percent': data['system']['cpu_percent'],
                    'memory_percent': data['system']['memory_percent'],
                    'memory_used': data['system']['memory_used'],
                    'memory_total': data['system']['memory_total'],
                    'disk_percent': data['system']['disk_percent'],
                    'disk_used': data['system']['disk_used'],
                    'disk_total': data['system']['disk_total'],
                    'gpu_percent': data['gpu'].get('gpu_percent', 0) if data['gpu'] else 0,
                    'gpu_memory_percent': data['gpu'].get('gpu_memory_percent', 0) if data['gpu'] else 0,
                    'gpu_temperature': data['gpu'].get('gpu_temperature', 0) if data['gpu'] else 0
                }
                writer.writerow(csv_row)

        logger.info(f"数据已导出到: {filepath}")
        return filepath

    def _filter_data_by_time(self, start_time: Optional[str],
                           end_time: Optional[str]) -> List[Dict]:
        """根据时间过滤数据"""
        if not start_time and not end_time:
            return self.monitor_data

        filtered_data = []
        for data in self.monitor_data:
            data_time = datetime.fromisoformat(data['timestamp'])

            if start_time:
                start = datetime.fromisoformat(start_time)
                if data_time < start:
                    continue

            if end_time:
                end = datetime.fromisoformat(end_time)
                if data_time > end:
                    continue

            filtered_data.append(data)

        return filtered_data

    def get_system_summary(self) -> Dict:
        """获取系统资源使用摘要"""
        if not self.monitor_data:
            return {}

        recent_data = self.monitor_data[-100:]  # 最近100个数据点

        cpu_values = [d['system']['cpu_percent'] for d in recent_data]
        memory_values = [d['system']['memory_percent'] for d in recent_data]
        disk_values = [d['system']['disk_percent'] for d in recent_data]

        return {
            'monitoring_status': 'running' if self.running else 'stopped',
            'monitoring_interval': self.interval,
            'total_data_points': len(self.monitor_data),
            'recent_stats': {
                'cpu': {
                    'average': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values)
                },
                'memory': {
                    'average': sum(memory_values) / len(memory_values),
                    'max': max(memory_values),
                    'min': min(memory_values)
                },
                'disk': {
                    'average': sum(disk_values) / len(disk_values),
                    'max': max(disk_values),
                    'min': min(disk_values)
                }
            },
            'gpu_available': len(self.monitor_data) > 0 and bool(self.monitor_data[-1]['gpu'])
        }


# 全局资源监控器实例
resource_monitor = None


def get_resource_monitor():
    """获取全局资源监控器实例"""
    global resource_monitor
    if resource_monitor is None:
        resource_monitor = ResourceMonitor()
    return resource_monitor


def start_resource_monitoring(interval: int = 5):
    """启动资源监控"""
    monitor = get_resource_monitor()
    monitor.interval = interval
    monitor.start_monitoring()


def stop_resource_monitoring():
    """停止资源监控"""
    monitor = get_resource_monitor()
    monitor.stop_monitoring()