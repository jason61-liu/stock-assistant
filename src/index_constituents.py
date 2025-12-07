"""
指数成分股查询模块
支持中证100、中证200、沪深300、中证500等指数的成分股信息查询
"""
import akshare as ak
import pandas as pd
import requests
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from .config import Config

logger = logging.getLogger(__name__)

class IndexConstituentsManager:
    """指数成分股管理器"""

    def __init__(self):
        self.cache = {}
        self.last_request_time = 0
        self.min_request_interval = 1.0

    def _rate_limit(self):
        """请求限速"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)

        self.last_request_time = time.time()

    def get_supported_indices(self) -> Dict[str, Dict]:
        """获取支持的指数列表"""
        return {
            "中证100": {
                "code": "000903",
                "name": "中证100指数",
                "description": "由沪深300指数样本股中规模最大的100只股票组成",
                "market": "沪深市场",
                "created_date": "2005-04-08"
            },
            "中证200": {
                "code": "000904",
                "name": "中证200指数",
                "description": "由沪深300指数样本股中剔除中证100指数样本股后剩余的200只股票组成",
                "market": "沪深市场",
                "created_date": "2005-04-08"
            },
            "沪深300": {
                "code": "000300",
                "name": "沪深300指数",
                "description": "由上海和深圳证券市场中市值大、流动性好的300只股票组成",
                "market": "沪深市场",
                "created_date": "2005-04-08"
            },
            "中证500": {
                "code": "000905",
                "name": "中证500指数",
                "description": "由全部A股中剔除沪深300指数成分股及总市值排名前300名的股票后，总市值排名靠前的500只股票组成",
                "market": "沪深市场",
                "created_date": "2007-01-15"
            }
        }

    def get_index_constituents_by_code(self, index_code: str) -> Optional[pd.DataFrame]:
        """根据指数代码获取成分股列表"""
        self._rate_limit()

        try:
            # 使用akShare获取指数成分股，注意参数名是symbol
            df = ak.index_stock_cons(symbol=index_code)

            if df is None or df.empty:
                logger.warning(f"获取指数 {index_code} 成分股数据为空")
                return None

            # 标准化列名 - akShare返回的列名是"品种代码"和"品种名称"
            column_mapping = {
                '品种代码': 'code',
                '品种名称': 'name',
                '权重': 'weight',
                '行业': 'industry'
            }

            # 重命名列
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})

            # 确保必要列存在
            if 'code' not in df.columns:
                # 如果没有code列，使用品种代码
                if '品种代码' in df.columns:
                    df = df.rename(columns={'品种代码': 'code'})
                else:
                    logger.error(f"指数 {index_code} 数据缺少代码列")
                    return None

            if 'name' not in df.columns:
                # 如果没有name列，使用品种名称
                if '品种名称' in df.columns:
                    df = df.rename(columns={'品种名称': 'name'})
                else:
                    logger.error(f"指数 {index_code} 数据缺少名称列")
                    return None

            # 清理数据
            df['code'] = df['code'].astype(str).str.zfill(6)
            df = df.drop_duplicates(subset=['code'])

            logger.info(f"成功获取指数 {index_code} 成分股 {len(df)} 只")
            return df

        except Exception as e:
            logger.error(f"获取指数 {index_code} 成分股失败: {e}")
            return None

    def get_index_constituents_by_name(self, index_name: str) -> Optional[pd.DataFrame]:
        """根据指数名称获取成分股列表"""
        indices = self.get_supported_indices()

        if index_name not in indices:
            logger.error(f"不支持的指数名称: {index_name}")
            return None

        index_code = indices[index_name]['code']
        return self.get_index_constituents_by_code(index_code)

    def get_stock_basic_info(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        self._rate_limit()

        try:
            # 标准化股票代码
            stock_code = stock_code.zfill(6)

            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=stock_code)

            if stock_info is None or stock_info.empty:
                logger.warning(f"获取股票 {stock_code} 基本信息为空")
                return None

            # 转换为字典
            info_dict = {}
            for _, row in stock_info.iterrows():
                item = str(row['item']).strip()
                value = str(row['value']).strip()

                # 清理数据
                if value == 'NaN' or value == '--':
                    value = None

                info_dict[item] = value

            # 获取实时价格信息
            current_price = None
            price_change = None
            price_change_pct = None

            try:
                # 使用akShare获取实时价格
                stock_price_data = ak.stock_zh_a_spot_em()
                if stock_price_data is not None and not stock_price_data.empty:
                    # 查找对应股票的行
                    stock_row = stock_price_data[stock_price_data['代码'] == stock_code]
                    if not stock_row.empty:
                        current_price = float(stock_row['最新价'].iloc[0]) if stock_row['最新价'].iloc[0] else None
                        price_change = float(stock_row['涨跌额'].iloc[0]) if stock_row['涨跌额'].iloc[0] else None
                        price_change_pct = float(stock_row['涨跌幅'].iloc[0]) if stock_row['涨跌幅'].iloc[0] else None
            except Exception as e:
                logger.warning(f"获取股票 {stock_code} 实时价格失败: {e}")

            # 标准化常用字段
            standardized_info = {
                'code': stock_code,
                'name': info_dict.get('股票简称'),
                '最新价': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'current_price': current_price,  # 兼容前端显示
                'list_date': info_dict.get('上市日期'),
                'total_shares': info_dict.get('总股本'),
                'float_shares': info_dict.get('流通股本'),
                'market_cap': info_dict.get('总市值'),
                'float_market_cap': info_dict.get('流通市值'),
                'pe': info_dict.get('市盈率-动态'),
                'pb': info_dict.get('市净率'),
                'industry': info_dict.get('所属行业'),
                'concept': info_dict.get('概念板块'),
                'main_business': info_dict.get('主营业务'),
                'company_profile': info_dict.get('公司简介'),
                'chairman': info_dict.get('董事长'),
                'employees': info_dict.get('员工人数'),
                'established_date': info_dict.get('成立日期'),
                'registered_capital': info_dict.get('注册资本'),
                'website': info_dict.get('公司网址'),
                'address': info_dict.get('公司地址'),
                'phone': info_dict.get('联系电话'),
                'email': info_dict.get('电子信箱'),
            }

            # 清理数值字段
            numeric_fields = ['total_shares', 'float_shares', 'market_cap', 'float_market_cap',
                             'pe', 'pb', 'employees', 'registered_capital', '最新价', 'price_change', 'price_change_pct']
            for field in numeric_fields:
                if standardized_info[field]:
                    try:
                        # 移除单位并转换为数字
                        value = standardized_info[field]
                        if isinstance(value, str):
                            value = value.replace('万', '').replace('亿', '').replace(',', '')
                            standardized_info[field] = float(value) if value else None
                    except:
                        standardized_info[field] = None

            logger.info(f"成功获取股票 {stock_code} 基本信息")
            return standardized_info

        except Exception as e:
            logger.error(f"获取股票 {stock_code} 基本信息失败: {e}")
            return None

    def get_constituents_with_info(self, index_name: str, limit: Optional[int] = None) -> List[Dict]:
        """获取指数成分股及其详细信息"""
        logger.info(f"开始获取 {index_name} 成分股详细信息...")

        # 获取成分股列表
        constituents_df = self.get_index_constituents_by_name(index_name)
        if constituents_df is None:
            return []

        constituents_list = []
        total_count = len(constituents_df)

        # 应用限制
        if limit:
            constituents_df = constituents_df.head(limit)
            logger.info(f"限制查询前 {limit} 只股票")

        for idx, (_, row) in enumerate(constituents_df.iterrows(), 1):
            stock_code = row['code']
            stock_name = row['name']

            logger.info(f"获取第 {idx}/{len(constituents_df)} 只股票信息: {stock_code} {stock_name}")

            # 获取详细信息
            stock_info = self.get_stock_basic_info(stock_code)

            if stock_info:
                # 合并信息
                stock_data = {
                    'code': stock_code,
                    'name': stock_name,
                    'weight': row.get('weight', None),
                    'industry': row.get('industry', None),
                    'basic_info': stock_info
                }
                constituents_list.append(stock_data)
            else:
                # 即使获取详细信息失败，也保留基本信息
                stock_data = {
                    'code': stock_code,
                    'name': stock_name,
                    'weight': row.get('weight', None),
                    'industry': row.get('industry', None),
                    'basic_info': None,
                    'error': '获取详细信息失败'
                }
                constituents_list.append(stock_data)

            # 请求间隔
            time.sleep(0.5)

        logger.info(f"完成获取 {index_name} 成分股信息，成功: {len([s for s in constituents_list if s.get('basic_info')])}只")
        return constituents_list

    def get_index_analysis(self, index_name: str) -> Dict:
        """获取指数的综合分析"""
        logger.info(f"开始分析指数 {index_name}...")

        # 获取支持的指数信息
        supported_indices = self.get_supported_indices()
        if index_name not in supported_indices:
            return {
                'error': f'不支持的指数名称: {index_name}',
                'supported_indices': list(supported_indices.keys())
            }

        # 获取成分股
        constituents_df = self.get_index_constituents_by_name(index_name)
        if constituents_df is None:
            return {
                'error': f'获取 {index_name} 成分股失败',
                'index_name': index_name
            }

        # 基础统计
        total_stocks = len(constituents_df)

        # 行业分布
        industry_distribution = {}
        if 'industry' in constituents_df.columns:
            industry_count = constituents_df['industry'].value_counts()
            industry_distribution = industry_count.to_dict()

        # 权重分析
        weight_stats = None
        if 'weight' in constituents_df.columns:
            try:
                weights = pd.to_numeric(constituents_df['weight'], errors='coerce').dropna()
                if not weights.empty:
                    weight_stats = {
                        'top10_weight_sum': weights.nlargest(10).sum(),
                        'top10_count': len(weights.nlargest(10)),
                        'average_weight': weights.mean(),
                        'max_weight': weights.max(),
                        'min_weight': weights.min()
                    }
            except Exception as e:
                logger.warning(f"权重分析失败: {e}")

        # 构建分析结果
        analysis_result = {
            'index_info': supported_indices[index_name],
            'constituents_count': total_stocks,
            'industry_distribution': industry_distribution,
            'weight_statistics': weight_stats,
            'analysis_time': datetime.now().isoformat(),
            'constituents_list': constituents_df.to_dict('records')[:50]  # 只返回前50只
        }

        logger.info(f"完成指数 {index_name} 分析，成分股数量: {total_stocks}")
        return analysis_result

    def search_stocks_by_keyword(self, keyword: str) -> List[Dict]:
        """根据关键词搜索股票"""
        try:
            # 使用akShare搜索股票
            search_result = ak.stock_info_a_code_name()
            if search_result is None or search_result.empty:
                return []

            # 模糊搜索
            search_result['name'] = search_result['name'].astype(str)
            search_result['code'] = search_result['code'].astype(str)

            # 搜索代码或名称包含关键词的股票
            mask = (search_result['name'].str.contains(keyword, case=False, na=False) |
                   search_result['code'].str.contains(keyword, case=False, na=False))

            matched_stocks = search_result[mask].head(20)  # 限制返回20条

            results = []
            for _, row in matched_stocks.iterrows():
                results.append({
                    'code': row['code'],
                    'name': row['name'],
                    'market': 'A股市场'
                })

            return results

        except Exception as e:
            logger.error(f"搜索股票关键词 {keyword} 失败: {e}")
            return []

    def get_company_profile(self, stock_code: str) -> Optional[Dict]:
        """获取公司详细信息"""
        self._rate_limit()

        try:
            stock_code = stock_code.zfill(6)

            # 获取公司概况
            company_info = ak.stock_individual_info_em(symbol=stock_code)

            if company_info is None or company_info.empty:
                return None

            # 获取财务指标
            financial_info = None
            try:
                financial_data = ak.stock_financial_analysis_indicator(symbol=stock_code)
                if not financial_data.empty:
                    # 取最新一期的财务数据
                    latest_financial = financial_data.iloc[-1]
                    financial_info = {
                        'roe': latest_financial.get('净资产收益率'),
                        'roa': latest_financial.get('总资产净利润率'),
                        'debt_ratio': latest_financial.get('负债率'),
                        'current_ratio': latest_financial.get('流动比率'),
                        'gross_margin': latest_financial.get('毛利率'),
                        'net_margin': latest_financial.get('净利率'),
                        'revenue_growth': latest_financial.get('营业收入增长率'),
                        'net_profit_growth': latest_financial.get('净利润增长率')
                    }
            except Exception as e:
                logger.warning(f"获取股票 {stock_code} 财务信息失败: {e}")

            # 获取管理层信息
            management_info = None
            try:
                # 这里可以尝试获取管理层信息，但akShare可能没有直接的接口
                pass
            except Exception as e:
                logger.warning(f"获取股票 {stock_code} 管理层信息失败: {e}")

            # 整合信息
            profile = {
                'stock_code': stock_code,
                'company_info': company_info.to_dict('records') if not company_info.empty else [],
                'financial_info': financial_info,
                'management_info': management_info,
                'update_time': datetime.now().isoformat()
            }

            return profile

        except Exception as e:
            logger.error(f"获取股票 {stock_code} 公司概况失败: {e}")
            return None