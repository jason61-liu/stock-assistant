"""
数据获取模块
使用akShare获取股票数据
"""
import akshare as ak
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import random
import numpy as np

from .config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """数据获取器"""

    def __init__(self):
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 最小请求间隔（秒）

    def _rate_limit(self):
        """请求限速"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)

        self.last_request_time = time.time()

    def get_index_constituents(self, index_code: str) -> Dict[str, str]:
        """获取指数成分股"""
        self._rate_limit()

        try:
            if index_code == "SSE100":
                # 上证100指数成分股
                df = ak.index_stock_cons(index="000903")
            elif index_code == "CSI300":
                # 中证300指数成分股
                df = ak.index_stock_cons(index="000905")
            else:
                raise ValueError(f"不支持的指数代码: {index_code}")

            # 转换为字典格式 {股票代码: 股票名称}
            stock_dict = {}
            for _, row in df.iterrows():
                code = str(row['代码']).zfill(6)
                name = row['名称']
                stock_dict[code] = name

            logger.info(f"获取到 {index_code} 成分股 {len(stock_dict)} 只")
            return stock_dict

        except Exception as e:
            logger.error(f"获取指数成分股失败: {e}")
            return {}

    def validate_stock_code(self, code: str) -> str:
        """验证和标准化股票代码"""
        # 移除非数字字符
        clean_code = ''.join(filter(str.isdigit, code))

        if len(clean_code) != 6:
            raise ValueError(f"股票代码格式错误: {code}")

        # 补全到6位
        return clean_code.zfill(6)

    def get_stock_name(self, code: str) -> str:
        """获取股票名称"""
        self._rate_limit()

        try:
            code = self.validate_stock_code(code)
            # 使用akShare获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=code)
            name = stock_info[stock_info['item'] == '股票简称']['value'].iloc[0]
            return name
        except Exception as e:
            logger.warning(f"获取股票 {code} 名称失败: {e}")
            return f"股票{code}"

    def get_stock_basic_data(self, code: str, period: str = "daily") -> Optional[pd.DataFrame]:
        """获取股票基础数据（开高低收、成交量等）"""
        self._rate_limit()

        try:
            code = self.validate_stock_code(code)

            # 方法1: 尝试主要的akShare接口
            df = self._try_primary_akshare(code)
            if df is not None and not df.empty:
                df['data_source'] = 'akshare_primary'
                logger.info(f"成功从akShare主要接口获取股票 {code} 数据: {len(df)} 条")
                return df

            # 方法2: 尝试替代数据源
            logger.warning(f"主要数据源失败，尝试替代数据源获取股票 {code} 数据")
            alternative_df = self._try_alternative_data_sources(code)
            if alternative_df is not None and not alternative_df.empty:
                return alternative_df

            # 方法3: 生成模拟数据
            logger.warning(f"所有数据源都失败，为股票 {code} 生成模拟数据用于演示")
            return self._generate_mock_stock_data(code)

        except Exception as e:
            logger.error(f"获取股票 {code} 基础数据失败: {e}")
            logger.warning(f"为股票 {code} 生成模拟数据用于演示")
            return self._generate_mock_stock_data(code)

    def _try_primary_akshare(self, code: str) -> Optional[pd.DataFrame]:
        """尝试主要的akShare接口"""
        try:
            # 确定交易所后缀
            if code.startswith('6'):
                symbol = f"{code}.SH"
            else:
                symbol = f"{code}.SZ"

            # 尝试主要接口
            df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

            if df is None or df.empty:
                return None

            # 标准化列名
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change_amount',
                '换手率': 'turnover'
            })

            # 确保日期是datetime类型
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            return df

        except Exception as e:
            logger.warning(f"主要akShare接口失败: {e}")
            return None

    def _generate_mock_stock_data(self, code: str) -> pd.DataFrame:
        """生成模拟股票数据用于演示"""
        try:
            # 设置随机种子以确保同一只股票的数据一致
            random.seed(int(code))
            np.random.seed(int(code))

            # 生成过去180天的数据
            end_date = datetime.now()
            dates = pd.date_range(end=end_date, periods=180, freq='D')
            dates = dates[dates.weekday < 5]  # 只保留工作日

            # 基础价格（根据股票代码生成不同基准）
            base_price = 10 + (int(code) % 90)  # 10-100之间的基准价格

            # 生成公司信息
            company_info = self._generate_mock_company_info(code, base_price)

            # 生成价格数据
            data = []
            for i, date in enumerate(dates):
                # 随机游走生成价格
                price_change = np.random.normal(0, 0.02)  # 2%的日波动率

                if i == 0:
                    close_price = base_price
                    inclusion_date = date - pd.Timedelta(days=np.random.randint(365, 1000))  # 纳入日期在1-3年前
                else:
                    close_price = data[-1]['close'] * (1 + price_change)
                    close_price = max(close_price, 1.0)  # 价格不低于1

                # 生成开高低收
                high_price = close_price * (1 + abs(np.random.normal(0, 0.01)))
                low_price = close_price * (1 - abs(np.random.normal(0, 0.01)))
                open_price = close_price * (1 + np.random.normal(0, 0.005))

                # 确保价格逻辑正确
                high_price = max(high_price, open_price, close_price)
                low_price = min(low_price, open_price, close_price)

                # 生成成交量和成交额
                volume = np.random.randint(1000000, 50000000)  # 100万-5000万股
                amount = volume * close_price

                # 生成其他指标
                amplitude = (high_price - low_price) / close_price * 100
                change_pct = (close_price - open_price) / open_price * 100
                change_amount = close_price - open_price
                turnover = volume / 100000000 * np.random.uniform(0.5, 5.0)  # 换手率

                data.append({
                    'date': date,
                    'open': round(open_price, 2),
                    'close': round(close_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'volume': volume,
                    'amount': round(amount, 2),
                    'amplitude': round(amplitude, 2),
                    'change_pct': round(change_pct, 2),
                    'change_amount': round(change_amount, 2),
                    'turnover': round(turnover, 2),
                    'data_source': 'mock',  # 添加数据源标识
                    # 添加公司信息
                    'company_name': company_info['name'],
                    'company_full_name': company_info['full_name'],
                    'industry': company_info['industry'],
                    'sector': company_info['sector'],
                    'market': company_info['market'],
                    'inclusion_date': inclusion_date,
                    'list_date': inclusion_date,  # 模拟数据中，纳入日期等于上市日期
                    'total_shares': company_info['total_shares'],
                    'float_shares': company_info['float_shares'],
                    'registered_capital': company_info['registered_capital'],
                    'company_website': company_info['website'],
                    'chairman': company_info['chairman'],
                    'established_date': company_info['established_date']
                })

            df = pd.DataFrame(data)

            logger.info(f"为股票 {code} 生成了 {len(df)} 天的模拟数据和公司信息")
            return df

        except Exception as e:
            logger.error(f"生成模拟数据失败: {e}")
            return None

    def _generate_mock_company_info(self, code: str, base_price: float) -> Dict:
        """生成模拟公司信息"""
        # 根据股票代码生成不同的公司信息
        company_seeds = {
            '000001': {
                'name': '平安银行',
                'full_name': '平安银行股份有限公司',
                'industry': '银行',
                'sector': '金融',
                'market': '深交所',
                'total_shares': 1940591819804,
                'float_shares': 19405919804,
                'registered_capital': 1940591819804,
                'website': 'http://bank.pingan.com',
                'chairman': '谢永林',
                'established_date': '1987-12-22'
            },
            '600519': {
                'name': '贵州茅台',
                'full_name': '贵州茅台酒股份有限公司',
                'industry': '白酒',
                'sector': '消费品',
                'market': '上交所',
                'total_shares': 1256197800,
                'float_shares': 1256197800,
                'registered_capital': 1256197800,
                'website': 'http://www.moutaichina.com',
                'chairman': '张德芹',
                'established_date': '1999-07-26'
            },
            '000858': {
                'name': '五粮液',
                'full_name': '宜宾五粮液股份有限公司',
                'industry': '白酒',
                'sector': '消费品',
                'market': '深交所',
                'total_shares': 3868200000,
                'float_shares': 3868200000,
                'registered_capital': 3868200000,
                'website': 'http://www.wuliangye.com.cn',
                'chairman': '曾从钦',
                'established_date': '1998-04-21'
            }
        }

        # 如果有预设的股票信息，使用预设值
        if code in company_seeds:
            return company_seeds[code]

        # 否则生成随机公司信息
        company_types = [
            ('科技', ['软件服务', '互联网', '电子信息', '通信设备', '半导体']),
            ('金融', ['银行', '保险', '证券', '信托', '基金']),
            ('制造', ['机械设备', '化工', '钢铁', '有色金属', '汽车']),
            ('消费', ['白酒', '食品饮料', '纺织服装', '家电', '零售']),
            ('医药', ['化学制药', '中药', '生物制品', '医疗器械']),
            ('能源', ['石油开采', '煤炭开采', '电力', '新能源']),
            ('地产', ['房地产开发', '建筑装饰', '园林工程']),
            ('交通', ['航空', '港口', '高速公路', '铁路运输'])
        ]

        sectors = ['科技', '金融', '制造', '消费', '医药', '能源', '地产', '交通']
        industries = company_types[int(code) % len(company_types)][1]

        market = '上交所' if code.startswith('6') else '深交所'

        # 生成公司名称
        company_names = [
            '华泰科技', '东方集团', '中航资本', '招商银行', '中国平安',
            '万科集团', '中石油', '中石化', '中国移动', '中国联通',
            '中国电信', '工商银行', '建设银行', '农业银行', '中国银行',
            '民生银行', '浦发银行', '兴业银行', '平安银行', '华夏银行'
        ]

        company_index = int(code) % len(company_names)
        sector_name = sectors[int(code) % len(sectors)]

        return {
            'name': company_names[company_index],
            'full_name': f'{company_names[company_index]}股份有限公司',
            'industry': industries,
            'sector': sector_name,
            'market': market,
            'total_shares': np.random.randint(1000000000, 20000000000),
            'float_shares': np.random.randint(500000000, 15000000000),
            'registered_capital': np.random.randint(1000000000, 20000000000),
            'website': f'http://www.company{code}.com',
            'chairman': f"{['张', '李', '王', '刘', '陈', '杨', '黄', '周'][int(code) % 8]}董事长",
            'established_date': f"{1990 + int(code) % 30:02d}-{int(code) % 12 + 1:02d}-{int(code) % 28 + 1:02d}"
        }

    def _try_alternative_data_sources(self, code: str) -> Optional[pd.DataFrame]:
        """尝试从其他数据源获取股票数据"""
        logger.info(f"尝试从其他数据源获取股票 {code} 的数据")

        # 方法1: 尝试不同的akShare接口
        try:
            logger.info("尝试 ak.stock_zh_a_hist 替代方法")
            df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                    start_date="20240101",
                                    end_date="20251207",
                                    adjust="")

            if df is not None and not df.empty:
                # 添加数据源标识
                df['data_source'] = 'akshare_alternative'
                logger.info(f"成功从akShare替代方法获取股票 {code} 数据: {len(df)} 条")
                return self._standardize_stock_data(df)
        except Exception as e:
            logger.warning(f"akShare替代方法失败: {e}")

        # 方法2: 尝试新浪财经接口 (如果akShare支持)
        try:
            logger.info("尝试新浪财经接口")
            # 注意：akShare可能包含新浪财经的数据源
            df = ak.stock_zh_a_daily(symbol=code)

            if df is not None and not df.empty:
                df['data_source'] = 'sina'
                logger.info(f"成功从新浪财经获取股票 {code} 数据: {len(df)} 条")
                return self._standardize_stock_data(df)
        except Exception as e:
            logger.warning(f"新浪财经接口失败: {e}")

        # 方法3: 尝试腾讯财经接口
        try:
            logger.info("尝试腾讯财经接口")
            # 尝试腾讯的数据源
            df = ak.stock_zh_a_daily_tx(symbol=code)

            if df is not None and not df.empty:
                df['data_source'] = 'tencent'
                logger.info(f"成功从腾讯财经获取股票 {code} 数据: {len(df)} 条")
                return self._standardize_stock_data(df)
        except Exception as e:
            logger.warning(f"腾讯财经接口失败: {e}")

        return None

    def _standardize_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化股票数据格式"""
        try:
            # 根据不同的列名映射到标准格式
            column_mapping = {
                # 常见的列名映射
                '日期': 'date', 'Date': 'date', 'date': 'date',
                '开盘': 'open', 'Open': 'open', 'open': 'open',
                '收盘': 'close', 'Close': 'close', 'close': 'close',
                '最高': 'high', 'High': 'high', 'high': 'high',
                '最低': 'low', 'Low': 'low', 'low': 'low',
                '成交量': 'volume', 'Volume': 'volume', 'volume': 'volume',
                '成交额': 'amount', 'Amount': 'amount', 'amount': 'amount',
                '振幅': 'amplitude', 'Amplitude': 'amplitude',
                '涨跌幅': 'change_pct', 'Change_pct': 'change_pct',
                '涨跌额': 'change_amount', 'Change': 'change_amount',
                '换手率': 'turnover', 'Turnover': 'turnover'
            }

            # 重命名列
            df_renamed = df.rename(columns=column_mapping)

            # 确保必要的列存在
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df_renamed.columns:
                    logger.warning(f"缺少必要列: {col}")
                    return None

            # 确保日期是datetime类型
            df_renamed['date'] = pd.to_datetime(df_renamed['date'])
            df_renamed = df_renamed.sort_values('date').reset_index(drop=True)

            # 如果没有data_source列，添加默认值
            if 'data_source' not in df_renamed.columns:
                df_renamed['data_source'] = 'unknown'

            return df_renamed

        except Exception as e:
            logger.error(f"标准化股票数据失败: {e}")
            return None

    def get_stock_valuation_data(self, code: str) -> Optional[Dict]:
        """获取股票估值数据（PE、PB等）"""
        self._rate_limit()

        try:
            code = self.validate_stock_code(code)

            # 获取实时估值数据
            valuation_df = ak.stock_zh_a_spot_em()
            stock_data = valuation_df[valuation_df['代码'] == code]

            if stock_data.empty:
                return None

            stock_info = stock_data.iloc[0]
            return {
                'pe': stock_info.get('市盈率-动态', None),
                'pb': stock_info.get('市净率', None),
                'ps': stock_info.get('市销率', None),
                'market_cap': stock_info.get('总市值', None),
                'circulation_cap': stock_data.get('流通市值', None)
            }

        except Exception as e:
            logger.error(f"获取股票 {code} 估值数据失败: {e}")
            return None

    def get_stock_financial_data(self, code: str) -> Optional[Dict]:
        """获取股票财务数据"""
        self._rate_limit()

        try:
            code = self.validate_stock_code(code)

            # 获取主要财务指标
            financial_df = ak.stock_financial_analysis_indicator(symbol=code)
            if financial_df.empty:
                return None

            # 取最新的财务数据
            latest_data = financial_df.iloc[-1]

            return {
                'roe': latest_data.get('净资产收益率', None),
                'roa': latest_data.get('总资产净利润率', None),
                'debt_ratio': latest_data.get('负债率', None),
                'current_ratio': latest_data.get('流动比率', None),
                'quick_ratio': latest_data.get('速动比率', None)
            }

        except Exception as e:
            logger.error(f"获取股票 {code} 财务数据失败: {e}")
            return None

    def get_margin_trading_data(self, code: str) -> Optional[Dict]:
        """获取融资融券数据"""
        self._rate_limit()

        try:
            code = self.validate_stock_code(code)

            # 获取融资融券数据
            margin_df = ak.stock_margin_detail_em(symbol=code)
            if margin_df.empty:
                return None

            # 取最新数据
            latest_data = margin_df.iloc[-1]

            return {
                'margin_balance': latest_data.get('融资余额(元)', None),
                'short_balance': latest_data.get('融券余量(股)', None),
                'margin_buy': latest_data.get('融资买入额(元)', None),
                'short_sell': latest_data.get('融券卖出量(股)', None)
            }

        except Exception as e:
            logger.error(f"获取股票 {code} 融资融券数据失败: {e}")
            return None