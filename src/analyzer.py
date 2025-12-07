"""
股票数据分析器
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging
import hashlib

from .config import Config
from .data_fetcher import DataFetcher
from .cache import CacheManager
from .indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """股票数据分析器"""

    def __init__(self):
        self.fetcher = DataFetcher()
        self.cache = CacheManager()
        self.indicators = TechnicalIndicators()

    def _get_cache_key(self, input_data: str, mode: str) -> str:
        """生成缓存键"""
        timestamp = datetime.now().strftime("%Y%m%d")
        key_string = f"{input_data}_{mode}_{timestamp}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def parse_input(self, input_data: str) -> Tuple[str, List[str]]:
        """解析输入，返回模式和股票代码列表"""
        input_data = input_data.strip()

        # 检查是否为指数
        if input_data in Config.INDEX_MAPPING:
            return "index", [input_data]

        # 检查是否为股票代码（6位数字）
        if input_data.isdigit() and len(input_data) == 6:
            return "stock", [input_data]

        # 处理多个股票代码（逗号分隔）
        if ',' in input_data:
            codes = [code.strip() for code in input_data.split(',')]
            valid_codes = []
            for code in codes:
                if code.isdigit() and len(code) == 6:
                    valid_codes.append(code)
                else:
                    try:
                        # 尝试补全6位代码
                        clean_code = ''.join(filter(str.isdigit, code))
                        if len(clean_code) == 6:
                            valid_codes.append(clean_code.zfill(6))
                    except:
                        continue

            if valid_codes:
                return "stocks", valid_codes

        # 默认当作单个股票代码处理
        try:
            clean_code = ''.join(filter(str.isdigit, input_data))
            if len(clean_code) == 6:
                return "stock", [clean_code.zfill(6)]
        except:
            pass

        raise ValueError(f"无法识别的输入格式: {input_data}")

    def get_stock_codes(self, input_data: str) -> Dict[str, str]:
        """获取股票代码和名称映射"""
        mode, codes = self.parse_input(input_data)

        if mode == "index":
            # 指数模式，获取成分股
            index_code = Config.INDEX_MAPPING[codes[0]]

            # 先检查缓存
            cached_data = self.cache.get_index_constituents(index_code)
            if cached_data:
                return cached_data

            # 获取成分股数据
            stock_dict = self.fetcher.get_index_constituents(index_code)
            if stock_dict:
                self.cache.set_index_constituents(index_code, stock_dict)
            return stock_dict

        elif mode == "stock":
            # 单个股票，获取股票名称
            code = codes[0]
            name = self.fetcher.get_stock_name(code)
            return {code: name}

        elif mode == "stocks":
            # 多个股票，获取名称
            stock_dict = {}
            for code in codes[:Config.MAX_STOCKS]:
                name = self.fetcher.get_stock_name(code)
                stock_dict[code] = name
            return stock_dict

        return {}

    def get_time_window_data(self, df: pd.DataFrame, window_days: int) -> pd.DataFrame:
        """获取指定时间窗口的数据"""
        if df.empty:
            return pd.DataFrame()

        latest_date = df['date'].max()
        start_date = latest_date - timedelta(days=window_days)

        # 考虑交易日，多取一些数据然后筛选
        extended_start = start_date - timedelta(days=window_days // 5)  # 额外增加约20%的天数
        window_df = df[df['date'] >= extended_start].copy()

        # 如果窗口太小，返回最近的可用数据
        if window_df.empty:
            # 返回最近的数据
            window_df = df.tail(min(window_days, len(df))).copy()

        return window_df.reset_index(drop=True)

    def analyze_single_stock(self, code: str, name: str) -> Dict:
        """分析单个股票"""
        logger.info(f"开始分析股票 {code} - {name}")

        stock_analysis = {
            'code': code,
            'name': name,
            'time_windows': {},
            'valuation': {},
            'financial': {},
            'margin_trading': {},
            'risk_metrics': {},
            'company_info': {},
            'data_source': None,
            'error': None
        }

        try:
            # 获取基础历史数据
            basic_df = self.fetcher.get_stock_basic_data(code)
            if basic_df is None or basic_df.empty:
                stock_analysis['error'] = "无法获取基础交易数据"
                return stock_analysis

            # 提取数据源信息和公司信息
            if 'data_source' in basic_df.columns:
                # 获取主要数据源（最新的数据源）
                data_source = basic_df['data_source'].iloc[-1]
                stock_analysis['data_source'] = data_source
                logger.info(f"股票 {code} 数据来源: {data_source}")
            else:
                stock_analysis['data_source'] = 'unknown'

            # 提取公司信息（从最新数据行）
            if not basic_df.empty:
                latest_data = basic_df.iloc[-1]

                # 提取所有可用的公司信息字段
                company_fields = [
                    'company_name', 'company_full_name', 'industry', 'sector',
                    'market', 'inclusion_date', 'list_date', 'total_shares',
                    'float_shares', 'registered_capital', 'company_website',
                    'chairman', 'established_date'
                ]

                company_info = {}
                for field in company_fields:
                    if field in latest_data and bool(pd.notna(latest_data[field])):
                        company_info[field] = latest_data[field]

                # 如果有公司信息，添加到分析结果中
                if company_info:
                    stock_analysis['company_info'] = company_info
                    logger.info(f"股票 {code} 公司信息: {company_info.get('company_name', 'N/A')} - {company_info.get('industry', 'N/A')}")

            # 计算技术指标
            df_with_indicators = self.indicators.calculate_basic_indicators(basic_df)

            # 分析各个时间窗口
            for window_name, window_days in Config.TIME_WINDOWS.items():
                try:
                    window_df = self.get_time_window_data(df_with_indicators, window_days)
                    if not window_df.empty:
                        latest_indicators = self.indicators.get_latest_indicators(window_df)
                        stock_analysis['time_windows'][window_name] = {
                            'data_points': len(window_df),
                            'latest_indicators': latest_indicators,
                            'start_date': window_df['date'].min().strftime('%Y-%m-%d'),
                            'end_date': window_df['date'].max().strftime('%Y-%m-%d'),
                            'price_change': float(window_df['close'].iloc[-1] - window_df['close'].iloc[0]) if len(window_df) > 1 else 0,
                            'price_change_pct': float((window_df['close'].iloc[-1] / window_df['close'].iloc[0] - 1) * 100) if len(window_df) > 1 and float(window_df['close'].iloc[0]) != 0 else 0
                        }
                except Exception as e:
                    logger.error(f"分析时间窗口 {window_name} 失败: {e}")
                    stock_analysis['time_windows'][window_name] = {'error': str(e)}

            # 获取估值数据
            try:
                valuation_data = self.fetcher.get_stock_valuation_data(code)
                if valuation_data:
                    stock_analysis['valuation'] = valuation_data
            except Exception as e:
                logger.error(f"获取估值数据失败: {e}")

            # 获取财务数据
            try:
                financial_data = self.fetcher.get_stock_financial_data(code)
                if financial_data:
                    stock_analysis['financial'] = financial_data
            except Exception as e:
                logger.error(f"获取财务数据失败: {e}")

            # 获取融资融券数据
            try:
                margin_data = self.fetcher.get_margin_trading_data(code)
                if margin_data:
                    stock_analysis['margin_trading'] = margin_data
            except Exception as e:
                logger.error(f"获取融资融券数据失败: {e}")

            # 计算风险指标（使用T-180的数据）
            if 'T-180' in stock_analysis['time_windows']:
                try:
                    window_180 = self.get_time_window_data(df_with_indicators, 180)
                    if not window_180.empty:
                        risk_metrics = self.indicators.calculate_risk_metrics(window_180)
                        stock_analysis['risk_metrics'] = risk_metrics
                except Exception as e:
                    logger.error(f"计算风险指标失败: {e}")

            logger.info(f"股票 {code} 分析完成")

        except Exception as e:
            logger.error(f"分析股票 {code} 失败: {e}")
            stock_analysis['error'] = str(e)

        return stock_analysis

    def analyze(self, input_data: str) -> Dict:
        """主要分析接口"""
        start_time = datetime.now()

        # 检查缓存
        cache_key = self._get_cache_key(input_data, "full_analysis")
        cached_result = self.cache.get_analysis_result(cache_key)
        if cached_result:
            logger.info(f"使用缓存结果: {input_data}")
            return cached_result

        logger.info(f"开始分析: {input_data}")

        try:
            # 获取股票代码和名称
            stock_dict = self.get_stock_codes(input_data)
            if not stock_dict:
                raise ValueError(f"无法获取股票代码: {input_data}")

            # 判断分析模式
            mode, _ = self.parse_input(input_data)

            result = {
                'input': input_data,
                'mode': mode,
                'stock_count': len(stock_dict),
                'timestamp': start_time.isoformat(),
                'stocks': {},
                'summary': {
                    'total_stocks': len(stock_dict),
                    'successful_analysis': 0,
                    'failed_analysis': 0
                }
            }

            # 分析每只股票
            for code, name in stock_dict.items():
                try:
                    stock_analysis = self.analyze_single_stock(code, name)
                    result['stocks'][code] = stock_analysis

                    if stock_analysis.get('error'):
                        result['summary']['failed_analysis'] += 1
                    else:
                        result['summary']['successful_analysis'] += 1

                except Exception as e:
                    logger.error(f"分析股票 {code} 异常: {e}")
                    result['stocks'][code] = {
                        'code': code,
                        'name': name,
                        'error': str(e)
                    }
                    result['summary']['failed_analysis'] += 1

            # 添加成功分析的股票统计
            successful_stocks = [code for code, analysis in result['stocks'].items()
                               if not analysis.get('error')]

            if successful_stocks:
                # 计算平均指标
                result['summary']['average_metrics'] = self._calculate_average_metrics(
                    [result['stocks'][code] for code in successful_stocks]
                )

            # 生成输出文件路径
            timestamp_str = start_time.strftime("%Y%m%d_%H%M%S")
            result['json_file'] = f"static/analysis_{timestamp_str}.json"
            result['chart_file'] = f"static/charts_{timestamp_str}.html"
            result['json_url'] = f"/static/analysis_{timestamp_str}.json"
            result['chart_url'] = f"/static/charts_{timestamp_str}.html"

            # 如果是指数模式，添加热力图
            if mode == "index" and len(successful_stocks) > 0:
                result['heatmap_file'] = f"static/heatmap_{timestamp_str}.html"
                result['heatmap_url'] = f"/static/heatmap_{timestamp_str}.html"

            # 缓存结果
            self.cache.set_analysis_result(cache_key, result)

            # 清理过期缓存
            self.cache.clear_expired_cache()

            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"分析完成，耗时: {elapsed_time:.2f}秒")

            return result

        except Exception as e:
            logger.error(f"分析失败: {e}")
            return {
                'input': input_data,
                'error': str(e),
                'timestamp': start_time.isoformat()
            }

    def _calculate_average_metrics(self, successful_analyses: List[Dict]) -> Dict:
        """计算成功分析股票的平均指标"""
        try:
            metrics = {
                'avg_price_change_pct': [],
                'avg_volume_ratio': [],
                'avg_rsi': [],
                'avg_pe': [],
                'avg_pb': [],
                'avg_volatility': []
            }

            for analysis in successful_analyses:
                # T-0时间窗口的指标
                if 'T-0' in analysis.get('time_windows', {}):
                    t0_data = analysis['time_windows']['T-0']
                    indicators = t0_data.get('latest_indicators', {})

                    metrics['avg_price_change_pct'].append(indicators.get('price_change_pct', 0))
                    metrics['avg_volume_ratio'].append(indicators.get('volume_ratio', 1))
                    metrics['avg_rsi'].append(indicators.get('rsi', 50))

                # 估值指标
                valuation = analysis.get('valuation', {})
                try:
                    pe = float(valuation.get('pe', 0)) if valuation.get('pe') and str(valuation.get('pe')).replace('.', '').isdigit() else 0
                    pb = float(valuation.get('pb', 0)) if valuation.get('pb') and str(valuation.get('pb')).replace('.', '').isdigit() else 0
                    metrics['avg_pe'].append(pe)
                    metrics['avg_pb'].append(pb)
                except:
                    pass

                # 波动率
                risk_metrics = analysis.get('risk_metrics', {})
                try:
                    volatility = float(risk_metrics.get('volatility', 0))
                    metrics['avg_volatility'].append(volatility)
                except:
                    pass

            # 计算平均值
            avg_metrics = {}
            for key, values in metrics.items():
                if values:
                    avg_metrics[key] = float(np.mean(values))
                else:
                    avg_metrics[key] = 0

            return avg_metrics

        except Exception as e:
            logger.error(f"计算平均指标失败: {e}")
            return {}