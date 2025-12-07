#!/usr/bin/env python3
"""
测试多数据源功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_fetcher import DataFetcher
import logging
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_sources():
    """测试多种数据源获取"""
    print("🧪 测试多数据源功能...")

    fetcher = DataFetcher()

    # 测试股票代码
    test_code = "000001"

    print(f"\n📊 测试股票: {test_code}")

    # 直接测试get_stock_basic_data方法
    print("调用 get_stock_basic_data...")
    try:
        df = fetcher.get_stock_basic_data(test_code)

        if df is not None and not df.empty:
            print(f"✅ 成功获取数据: {len(df)} 条记录")

            # 检查数据源
            if 'data_source' in df.columns:
                data_sources = df['data_source'].unique()
                print(f"📡 数据来源: {data_sources}")

                # 显示数据源分布
                source_counts = df['data_source'].value_counts()
                print("📈 数据源分布:")
                for source, count in source_counts.items():
                    print(f"  {source}: {count} 条记录")
            else:
                print("❌ 未找到数据源信息")

            # 显示数据样例
            print(f"\n📅 数据日期范围: {df['date'].min()} 到 {df['date'].max()}")
            print(f"💰 价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")

            return True
        else:
            print("❌ 返回空数据")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_primary_vs_alternative():
    """测试主要数据源 vs 替代数据源"""
    print("\n🔄 测试主要和替代数据源...")

    fetcher = DataFetcher()
    test_code = "000001"

    print(f"\n📊 测试股票: {test_code}")

    # 测试主要数据源
    print("1. 测试主要akShare数据源:")
    try:
        primary_df = fetcher._try_primary_akshare(test_code)
        if primary_df is not None and not primary_df.empty:
            primary_df['data_source'] = 'akshare_primary'
            print(f"✅ 主要数据源成功: {len(primary_df)} 条记录")
        else:
            print("❌ 主要数据源失败")
    except Exception as e:
        print(f"❌ 主要数据源异常: {e}")

    # 测试替代数据源
    print("2. 测试替代数据源:")
    try:
        alternative_df = fetcher._try_alternative_data_sources(test_code)
        if alternative_df is not None and not alternative_df.empty:
            print(f"✅ 替代数据源成功: {len(alternative_df)} 条记录")
            print(f"📡 数据源类型: {alternative_df['data_source'].iloc[0] if 'data_source' in alternative_df.columns else 'unknown'}")
        else:
            print("❌ 替代数据源失败")
    except Exception as e:
        print(f"❌ 替代数据源异常: {e}")

    # 测试模拟数据
    print("3. 测试模拟数据:")
    try:
        mock_df = fetcher._generate_mock_stock_data(test_code)
        if mock_df is not None and not mock_df.empty:
            print(f"✅ 模拟数据成功: {len(mock_df)} 条记录")
            print(f"📡 数据源类型: {mock_df['data_source'].iloc[0] if 'data_source' in mock_df.columns else 'unknown'}")
        else:
            print("❌ 模拟数据失败")
    except Exception as e:
        print(f"❌ 模拟数据异常: {e}")

def test_real_data_attempt():
    """尝试获取真实数据"""
    print("\n🌐 尝试获取真实数据...")

    # 尝试不同的akShare接口
    import akshare as ak

    test_codes = ["000001", "600519", "000858"]

    for code in test_codes:
        print(f"\n📊 测试股票: {code}")

        # 尝试不同的接口
        interfaces = [
            ("标准接口", lambda: ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")),
            ("新浪接口", lambda: ak.stock_zh_a_daily(symbol=code)),
            ("腾讯接口", lambda: ak.stock_zh_a_daily_tx(symbol=code))
        ]

        for name, func in interfaces:
            try:
                print(f"  尝试 {name}:")
                df = func()
                if df is not None and not df.empty:
                    print(f"    ✅ 成功: {len(df)} 条记录")
                    print(f"    📋 列名: {list(df.columns)[:5]}...")
                    break
                else:
                    print(f"    ❌ 无数据")
            except Exception as e:
                print(f"    ❌ 失败: {str(e)[:50]}...")

if __name__ == "__main__":
    print("🚀 开始测试数据源功能...")

    success1 = test_data_sources()
    test_primary_vs_alternative()
    test_real_data_attempt()

    if success1:
        print("\n🎉 数据源测试完成！")
    else:
        print("\n❌ 数据源测试失败！")