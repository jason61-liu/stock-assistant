#!/usr/bin/env python3
"""
测试模拟数据生成功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_fetcher import DataFetcher
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mock_data_generation():
    """测试模拟数据生成"""
    print("🧪 测试模拟数据生成功能...")

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
            print(f"📅 数据日期范围: {df['date'].min()} 到 {df['date'].max()}")
            print(f"💰 价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
            print(f"📋 列名: {list(df.columns)}")

            # 显示前几条数据
            print("\n📈 前5条数据样例:")
            print(df[['date', 'open', 'high', 'low', 'close', 'volume']].head())

            return True
        else:
            print("❌ 返回空数据")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_stocks():
    """测试多只股票的模拟数据"""
    print("\n🔄 测试多只股票...")

    fetcher = DataFetcher()
    test_codes = ["000001", "600519", "000858"]

    for code in test_codes:
        print(f"\n测试股票 {code}:")
        try:
            df = fetcher.get_stock_basic_data(code)
            if df is not None and not df.empty:
                print(f"✅ {code}: {len(df)} 条数据")
            else:
                print(f"❌ {code}: 数据为空")
        except Exception as e:
            print(f"❌ {code}: 错误 - {e}")

if __name__ == "__main__":
    success = test_mock_data_generation()

    if success:
        test_multiple_stocks()
        print("\n🎉 模拟数据生成测试完成！")
    else:
        print("\n❌ 模拟数据生成测试失败！")