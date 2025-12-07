#!/usr/bin/env python3
"""
测试单个股票价格获取
"""
import akshare as ak
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from index_constituents import IndexConstituentsManager

def test_single_stock():
    """测试单个股票价格获取"""
    manager = IndexConstituentsManager()

    # 测试几个不同的股票
    test_stocks = ["000001", "002028", "600000", "000002"]

    for stock_code in test_stocks:
        print(f"\n=== 测试股票: {stock_code} ===")

        try:
            # 测试基本信息获取
            info = manager.get_stock_basic_info(stock_code)
            if info:
                print(f"股票名称: {info.get('name')}")
                print(f"最新价: {info.get('最新价')}")
                print(f"current_price: {info.get('current_price')}")
                print(f"涨跌额: {info.get('price_change')}")
                print(f"涨跌幅: {info.get('price_change_pct')}")
            else:
                print("获取基本信息失败")

        except Exception as e:
            print(f"异常: {e}")

        # 测试直接获取价格数据
        try:
            print("\n--- 直接获取价格数据 ---")
            stock_price_data = ak.stock_zh_a_spot_em()
            if stock_price_data is not None and not stock_price_data.empty:
                stock_row = stock_price_data[stock_price_data['代码'] == stock_code]
                if not stock_row.empty:
                    print(f"最新价: {stock_row['最新价'].iloc[0]}")
                    print(f"涨跌额: {stock_row['涨跌额'].iloc[0]}")
                    print(f"涨跌幅: {stock_row['涨跌幅'].iloc[0]}")
                    print(f"成交量: {stock_row['成交量'].iloc[0]}")
                else:
                    print("未找到该股票价格数据")
            else:
                print("获取行情数据失败")

        except Exception as e:
            print(f"价格数据异常: {e}")

if __name__ == "__main__":
    test_single_stock()