"""
配置文件
"""
import os

class Config:
    """应用配置类"""

    # 数据源配置
    CACHE_EXPIRE_HOURS = 6  # 缓存过期时间（小时）
    MAX_STOCKS = 500  # 最大股票数量
    RATE_LIMIT = 60  # 每分钟最大请求数

    # 指数映射
    INDEX_MAPPING = {
        "上证100": "SSE100",
        "SSE100": "SSE100",
        "中证300": "CSI300",
        "CSI300": "CSI300"
    }

    # 时间窗口配置（天数）
    TIME_WINDOWS = {
        "T-0": 0,
        "T-3": 3,
        "T-7": 7,
        "T-30": 30,
        "T-90": 90,
        "T-180": 180
    }

    # 缓存文件路径
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
    CACHE_DB = os.path.join(CACHE_DIR, "stock_cache.db")

    # 输出目录
    OUTPUT_DIR = "static"

    # 报告文件目录
    REPORT_DIR = "report"

    @classmethod
    def ensure_dirs(cls):
        """确保必要目录存在"""
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.REPORT_DIR, exist_ok=True)