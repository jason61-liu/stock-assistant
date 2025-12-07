"""
SQLite缓存系统
"""
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import logging

from .config import Config

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器"""

    def __init__(self):
        Config.ensure_dirs()
        self.db_path = Config.CACHE_DB
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 创建股票基础数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_basic (
                        code TEXT,
                        date DATE,
                        data TEXT,
                        created_at TIMESTAMP,
                        PRIMARY KEY (code, date)
                    )
                ''')

                # 创建股票估值数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_valuation (
                        code TEXT PRIMARY KEY,
                        data TEXT,
                        created_at TIMESTAMP
                    )
                ''')

                # 创建股票财务数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_financial (
                        code TEXT PRIMARY KEY,
                        data TEXT,
                        created_at TIMESTAMP
                    )
                ''')

                # 创建融资融券数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS margin_trading (
                        code TEXT,
                        date DATE,
                        data TEXT,
                        created_at TIMESTAMP,
                        PRIMARY KEY (code, date)
                    )
                ''')

                # 创建指数成分股表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS index_constituents (
                        index_code TEXT PRIMARY KEY,
                        data TEXT,
                        created_at TIMESTAMP
                    )
                ''')

                # 创建完整结果缓存表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_result (
                        cache_key TEXT PRIMARY KEY,
                        data TEXT,
                        created_at TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("缓存数据库初始化完成")

        except Exception as e:
            logger.error(f"缓存数据库初始化失败: {e}")
            raise

    def _is_expired(self, created_at: str) -> bool:
        """检查缓存是否过期"""
        try:
            created_time = datetime.fromisoformat(created_at)
            expire_time = created_time + timedelta(hours=Config.CACHE_EXPIRE_HOURS)
            return datetime.now() > expire_time
        except:
            return True

    def set_stock_basic(self, code: str, date: str, data: Dict):
        """缓存股票基础数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_basic (code, date, data, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (code, date, json.dumps(data), datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"缓存股票基础数据失败: {e}")

    def get_stock_basic(self, code: str, date: str) -> Optional[Dict]:
        """获取股票基础数据缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data, created_at FROM stock_basic
                    WHERE code = ? AND date = ?
                ''', (code, date))

                row = cursor.fetchone()
                if row and not self._is_expired(row[1]):
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"获取股票基础数据缓存失败: {e}")

        return None

    def set_stock_valuation(self, code: str, data: Dict):
        """缓存股票估值数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_valuation (code, data, created_at)
                    VALUES (?, ?, ?)
                ''', (code, json.dumps(data), datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"缓存股票估值数据失败: {e}")

    def get_stock_valuation(self, code: str) -> Optional[Dict]:
        """获取股票估值数据缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data, created_at FROM stock_valuation
                    WHERE code = ?
                ''', (code,))

                row = cursor.fetchone()
                if row and not self._is_expired(row[1]):
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"获取股票估值数据缓存失败: {e}")

        return None

    def set_stock_financial(self, code: str, data: Dict):
        """缓存股票财务数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_financial (code, data, created_at)
                    VALUES (?, ?, ?)
                ''', (code, json.dumps(data), datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"缓存股票财务数据失败: {e}")

    def get_stock_financial(self, code: str) -> Optional[Dict]:
        """获取股票财务数据缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data, created_at FROM stock_financial
                    WHERE code = ?
                ''', (code,))

                row = cursor.fetchone()
                if row and not self._is_expired(row[1]):
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"获取股票财务数据缓存失败: {e}")

        return None

    def set_margin_trading(self, code: str, date: str, data: Dict):
        """缓存融资融券数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO margin_trading (code, date, data, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (code, date, json.dumps(data), datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"缓存融资融券数据失败: {e}")

    def get_margin_trading(self, code: str, date: str) -> Optional[Dict]:
        """获取融资融券数据缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data, created_at FROM margin_trading
                    WHERE code = ? AND date = ?
                ''', (code, date))

                row = cursor.fetchone()
                if row and not self._is_expired(row[1]):
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"获取融资融券数据缓存失败: {e}")

        return None

    def set_index_constituents(self, index_code: str, data: Dict):
        """缓存指数成分股"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO index_constituents (index_code, data, created_at)
                    VALUES (?, ?, ?)
                ''', (index_code, json.dumps(data), datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"缓存指数成分股失败: {e}")

    def get_index_constituents(self, index_code: str) -> Optional[Dict]:
        """获取指数成分股缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data, created_at FROM index_constituents
                    WHERE index_code = ?
                ''', (index_code,))

                row = cursor.fetchone()
                if row and not self._is_expired(row[1]):
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"获取指数成分股缓存失败: {e}")

        return None

    def set_analysis_result(self, cache_key: str, data: Dict):
        """缓存完整分析结果"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO analysis_result (cache_key, data, created_at)
                    VALUES (?, ?, ?)
                ''', (cache_key, json.dumps(data), datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"缓存分析结果失败: {e}")

    def get_analysis_result(self, cache_key: str) -> Optional[Dict]:
        """获取分析结果缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data, created_at FROM analysis_result
                    WHERE cache_key = ?
                ''', (cache_key,))

                row = cursor.fetchone()
                if row and not self._is_expired(row[1]):
                    return json.loads(row[0])
        except Exception as e:
            logger.error(f"获取分析结果缓存失败: {e}")

        return None

    def clear_expired_cache(self):
        """清理过期缓存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 清理各表的过期数据
                tables = ['stock_basic', 'stock_valuation', 'stock_financial',
                         'margin_trading', 'index_constituents', 'analysis_result']

                for table in tables:
                    if table in ['stock_basic', 'margin_trading']:
                        cursor.execute(f'''
                            DELETE FROM {table}
                            WHERE created_at < datetime('now', '-{Config.CACHE_EXPIRE_HOURS} hours')
                        ''')
                    else:
                        cursor.execute(f'''
                            DELETE FROM {table}
                            WHERE created_at < datetime('now', '-{Config.CACHE_EXPIRE_HOURS} hours')
                        ''')

                conn.commit()
                logger.info("过期缓存清理完成")

        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")

    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        try:
            stats = {}

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 统计各表的记录数
                tables = ['stock_basic', 'stock_valuation', 'stock_financial',
                         'margin_trading', 'index_constituents', 'analysis_result']

                total_records = 0
                table_stats = {}

                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_stats[table] = count
                    total_records += count

                # 统计过期记录数
                expired_count = 0
                for table in tables:
                    if table in ['stock_basic', 'margin_trading']:
                        cursor.execute(f'''
                            SELECT COUNT(*) FROM {table}
                            WHERE created_at < datetime('now', '-{Config.CACHE_EXPIRE_HOURS} hours')
                        ''')
                    else:
                        cursor.execute(f'''
                            SELECT COUNT(*) FROM {table}
                            WHERE created_at < datetime('now', '-{Config.CACHE_EXPIRE_HOURS} hours')
                        ''')
                    expired_count += cursor.fetchone()[0]

                # 获取最新和最旧的缓存时间
                cursor.execute('''
                    SELECT
                        MIN(created_at) as oldest,
                        MAX(created_at) as newest,
                        COUNT(*) as total_count
                    FROM (
                        SELECT created_at FROM stock_basic
                        UNION ALL SELECT created_at FROM stock_valuation
                        UNION ALL SELECT created_at FROM stock_financial
                        UNION ALL SELECT created_at FROM margin_trading
                        UNION ALL SELECT created_at FROM index_constituents
                        UNION ALL SELECT created_at FROM analysis_result
                    )
                ''')

                oldest, newest, db_total = cursor.fetchone()

                # 获取数据库文件大小
                db_size = 0
                if os.path.exists(self.db_path):
                    db_size = os.path.getsize(self.db_path)

                stats = {
                    'total_records': total_records,
                    'expired_records': expired_count,
                    'valid_records': total_records - expired_count,
                    'oldest_cache': oldest,
                    'newest_cache': newest,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'table_stats': table_stats,
                    'cache_expire_hours': Config.CACHE_EXPIRE_HOURS,
                    'cache_status': 'active' if total_records > 0 else 'empty'
                }

                return stats

        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {
                'cache_status': 'error',
                'error': str(e),
                'total_records': 0,
                'expired_records': 0,
                'valid_records': 0
            }