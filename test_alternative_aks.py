#!/usr/bin/env python3
"""
测试其他akShare数据获取方式
"""
import akshare as ak
import pandas as pd
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_various_aks_methods():
    """测试各种akShare数据获取方法"""
    print("🧪 测试各种akShare数据获取方法...")

    test_code = "000001"
    print(f"\n📊 测试股票: {test_code}")

    methods = [
        ("标准方法", lambda: ak.stock_zh_a_hist(symbol=test_code, period="daily", adjust="qfq")),
        ("不复权", lambda: ak.stock_zh_a_hist(symbol=test_code, period="daily", adjust="")),
        ("周线数据", lambda: ak.stock_zh_a_hist(symbol=test_code, period="weekly", adjust="qfq")),
        ("月线数据", lambda: ak.stock_zh_a_hist(symbol=test_code, period="monthly", adjust="qfq")),
        ("指定日期范围", lambda: ak.stock_zh_a_hist(symbol=test_code, period="daily", start_date="20240101", end_date="20241231")),
        ("不同符号格式", lambda: ak.stock_zh_a_hist(symbol="SZ" + test_code, period="daily", adjust="qfq")),
    ]

    for name, func in methods:
        try:
            print(f"\n📡 测试 {name}:")
            df = func()
            if df is not None and not df.empty:
                print(f"✅ 成功: {len(df)} 条记录")
                print(f"📋 列名: {list(df.columns)}")
                print(f"📅 日期范围: {df.iloc[0, 0] if len(df) > 0 else 'N/A'} 到 {df.iloc[-1, 0] if len(df) > 0 else 'N/A'}")

                # 尝试标准化数据
                try:
                    df_standardized = standardize_ak_data(df)
                    if df_standardized is not None:
                        print(f"🔧 标准化成功: {len(df_standardized)} 条记录")
                        print(f"📊 价格范围: {df_standardized['close'].min():.2f} - {df_standardized['close'].max():.2f}")
                    else:
                        print("❌ 标准化失败")
                except Exception as e:
                    print(f"❌ 标准化异常: {e}")
            else:
                print("❌ 无数据")
        except Exception as e:
            print(f"❌ 失败: {str(e)}")

def standardize_ak_data(df):
    """标准化akShare数据"""
    try:
        # 常见的列名映射
        column_mapping = {
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
            '换手率': 'turnover',
            # 英文列名
            'Date': 'date',
            'Open': 'open',
            'Close': 'close',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume',
            'Amount': 'amount'
        }

        # 重命名列
        df_renamed = df.rename(columns=column_mapping)

        # 确保必要的列存在
        required_columns = ['date', 'open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in df_renamed.columns:
                logger.warning(f"缺少必要列: {col}")
                return None

        # 确保日期是datetime类型
        df_renamed['date'] = pd.to_datetime(df_renamed['date'])
        df_renamed = df_renamed.sort_values('date').reset_index(drop=True)

        return df_renamed

    except Exception as e:
        logger.error(f"标准化数据失败: {e}")
        return None

def test_other_data_interfaces():
    """测试其他数据接口"""
    print("\n🌐 测试其他数据接口...")

    test_code = "000001"
    interfaces = [
        ("A股行情", lambda: ak.stock_zh_a_spot_em()),
        ("实时行情", lambda: ak.stock_zh_a_spot()),
        ("指数数据", lambda: ak.stock_zh_index_daily(symbol="000001")),
    ]

    for name, func in interfaces:
        try:
            print(f"\n📡 测试 {name}:")
            df = func()
            if df is not None and not df.empty:
                print(f"✅ 成功: {len(df)} 条记录")
                print(f"📋 列名: {list(df.columns)[:10]}...")

                # 检查是否包含测试股票
                if '代码' in df.columns:
                    stock_data = df[df['代码'] == test_code]
                    if not stock_data.empty:
                        print(f"🎯 找到股票 {test_code}: {len(stock_data)} 条")
                    else:
                        print(f"⚠️ 未找到股票 {test_code}")
            else:
                print("❌ 无数据")
        except Exception as e:
            print(f"❌ 失败: {str(e)}")

def test_recent_data_availability():
    """测试近期数据可用性"""
    print("\n📅 测试近期数据可用性...")

    test_code = "000001"

    # 尝试获取不同时间段的数据
    time_periods = [
        ("最近3天", lambda: ak.stock_zh_a_hist(symbol=test_code, period="daily", start_date=(datetime.now() - timedelta(days=3)).strftime('%Y%m%d'))),
        ("最近7天", lambda: ak.stock_zh_a_hist(symbol=test_code, period="daily", start_date=(datetime.now() - timedelta(days=7)).strftime('%Y%m%d'))),
        ("最近30天", lambda: ak.stock_zh_a_hist(symbol=test_code, period="daily", start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'))),
    ]

    for period_name, func in time_periods:
        try:
            print(f"\n📊 测试 {period_name}:")
            df = func()
            if df is not None and not df.empty:
                print(f"✅ 成功: {len(df)} 条记录")
                if len(df) > 0:
                    print(f"📅 最新数据: {df.iloc[-1, 0] if len(df.columns) > 0 else 'N/A'}")
            else:
                print("❌ 无数据")
        except Exception as e:
            print(f"❌ 失败: {str(e)}")

if __name__ == "__main__":
    test_various_aks_methods()
    test_other_data_interfaces()
    test_recent_data_availability()
    print("\n🎉 数据获取测试完成！")