#!/usr/bin/env python3
"""
测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analyzer import StockAnalyzer
from src.visualizer import StockVisualizer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_stock():
    """测试单个股票分析"""
    print("=" * 50)
    print("测试单个股票分析")
    print("=" * 50)

    analyzer = StockAnalyzer()
    visualizer = StockVisualizer()

    try:
        # 测试平安银行
        result = analyzer.analyze("000001")
        print(f"分析结果: {result.get('mode')} - {result.get('stock_count')} 只股票")

        if 'error' not in result:
            print("✅ 单个股票分析成功")

            # 测试生成文件
            if result.get('json_file'):
                visualizer.save_json_data(result, result['json_file'])
                print(f"✅ JSON文件生成: {result['json_file']}")

            if result.get('chart_file'):
                visualizer.generate_charts_html(result, result['chart_file'])
                print(f"✅ HTML图表生成: {result['chart_file']}")
        else:
            print(f"❌ 分析失败: {result['error']}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_multiple_stocks():
    """测试多个股票分析"""
    print("\n" + "=" * 50)
    print("测试多个股票分析")
    print("=" * 50)

    analyzer = StockAnalyzer()
    visualizer = StockVisualizer()

    try:
        # 测试多个股票
        result = analyzer.analyze("000001,600000,000002")
        print(f"分析结果: {result.get('mode')} - {result.get('stock_count')} 只股票")

        if 'error' not in result:
            print("✅ 多个股票分析成功")
            successful = result.get('summary', {}).get('successful_analysis', 0)
            failed = result.get('summary', {}).get('failed_analysis', 0)
            print(f"成功: {successful}, 失败: {failed}")
        else:
            print(f"❌ 分析失败: {result['error']}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_index():
    """测试指数分析"""
    print("\n" + "=" * 50)
    print("测试指数分析")
    print("=" * 50)

    analyzer = StockAnalyzer()

    try:
        # 测试中证300指数（注意：这里可能会比较慢，因为要获取300只股票）
        print("注意：指数分析可能需要较长时间...")
        result = analyzer.analyze("CSI300")
        print(f"分析结果: {result.get('mode')} - {result.get('stock_count')} 只股票")

        if 'error' not in result:
            print("✅ 指数分析成功")
            successful = result.get('summary', {}).get('successful_analysis', 0)
            failed = result.get('summary', {}).get('failed_analysis', 0)
            print(f"成功: {successful}, 失败: {failed}")

            # 如果成功，测试生成热力图
            if successful > 0:
                visualizer = StockVisualizer()
                stocks = result.get('stocks', {})
                successful_stocks = {code: data for code, data in stocks.items() if not data.get('error')}

                if len(successful_stocks) > 0:
                    heatmap_df = visualizer.create_heatmap_data(successful_stocks)
                    print(f"✅ 热力图数据生成: {len(heatmap_df)} 行")
        else:
            print(f"❌ 分析失败: {result['error']}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_data_fetcher():
    """测试数据获取功能"""
    print("\n" + "=" * 50)
    print("测试数据获取功能")
    print("=" * 50)

    from src.data_fetcher import DataFetcher

    fetcher = DataFetcher()

    try:
        # 测试获取股票名称
        name = fetcher.get_stock_name("000001")
        print(f"✅ 股票名称获取: 000001 - {name}")

        # 测试获取基础数据（少量数据）
        basic_data = fetcher.get_stock_basic_data("000001")
        if basic_data is not None:
            print(f"✅ 基础数据获取: {len(basic_data)} 条记录")
        else:
            print("❌ 基础数据获取失败")

        # 测试获取估值数据
        valuation_data = fetcher.get_stock_valuation_data("000001")
        if valuation_data:
            print(f"✅ 估值数据获取: PE={valuation_data.get('pe')}")
        else:
            print("❌ 估值数据获取失败")

    except Exception as e:
        print(f"❌ 数据获取测试失败: {e}")

def main():
    """主测试函数"""
    print("开始测试A股行情可视化服务...")
    print()

    # 测试数据获取
    test_data_fetcher()

    # 测试单个股票
    test_single_stock()

    # 测试多个股票
    test_multiple_stocks()

    # 指数分析测试（可选，因为比较耗时）
    test_index_expensive = input("\n是否测试指数分析？（较慢，需要获取多只股票数据）[y/N]: ").lower().strip()
    if test_index_expensive == 'y':
        test_index()

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()