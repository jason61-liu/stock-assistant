#!/usr/bin/env python3
"""
完整的数据源标注功能测试
"""
import requests
import json
import sys

def test_data_source_annotations():
    """测试完整的数据源标注功能"""
    base_url = "http://localhost:8000"

    print("🧪 测试完整的数据源标注功能...")
    print("=" * 60)

    # 测试1: 检查主页数据源说明
    print("\n📄 测试1: 主页数据源说明")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            if "数据来源说明" in response.text:
                print("✅ 主页包含数据来源说明")
            else:
                print("❌ 主页缺少数据来源说明")
        else:
            print("❌ 主页访问失败")
    except Exception as e:
        print(f"❌ 主页测试异常: {e}")

    # 测试2: API响应中的数据源标注
    print("\n📡 测试2: API数据源标注")
    test_stocks = ["000001", "000888", "600519"]

    for stock_code in test_stocks:
        print(f"\n📊 测试股票 {stock_code}:")
        try:
            response = requests.get(f"{base_url}/api/v1/stocks/{stock_code}")
            if response.status_code == 200:
                data = response.json()
                stocks = data.get('data', {}).get('stocks', {})

                if stock_code in stocks:
                    stock = stocks[stock_code]
                    data_source = stock.get('data_source')
                    print(f"  ✅ 数据源: {data_source}")

                    # 验证数据源类型
                    valid_sources = ['akshare_primary', 'akshare_alternative', 'sina', 'tencent', 'mock', 'unknown']
                    if data_source in valid_sources:
                        print(f"  ✅ 数据源类型有效")
                    else:
                        print(f"  ⚠️ 未知数据源类型: {data_source}")
                else:
                    print(f"  ❌ 未找到股票 {stock_code} 数据")
            else:
                print(f"  ❌ API请求失败: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")

    # 测试3: HTML报告中的数据源标注
    print("\n📈 测试3: HTML报告数据源标注")
    try:
        response = requests.get(f"{base_url}/api/v1/stocks/000999")
        if response.status_code == 200:
            data = response.json()
            chart_url = data.get('data', {}).get('chart_url')

            if chart_url:
                html_response = requests.get(f"{base_url}{chart_url}")
                if html_response.status_code == 200:
                    html_content = html_response.text

                    annotations = []
                    if "数据来源:" in html_content:
                        annotations.append("数据来源标注")
                    if "模拟数据" in html_content:
                        annotations.append("模拟数据标注")
                    if "演示模式" in html_content:
                        annotations.append("演示模式警告")

                    if annotations:
                        print(f"  ✅ HTML包含标注: {', '.join(annotations)}")
                    else:
                        print(f"  ❌ HTML缺少数据源标注")
                else:
                    print("  ❌ HTML文件访问失败")
            else:
                print("  ❌ 未找到chart_url")
        else:
            print("  ❌ API请求失败")
    except Exception as e:
        print(f"  ❌ HTML测试异常: {e}")

    # 测试4: 数据源样式验证
    print("\n🎨 测试4: 数据源样式验证")
    try:
        response = requests.get(f"{base_url}/api/v1/stocks/000999")
        if response.status_code == 200:
            data = response.json()
            chart_url = data.get('data', {}).get('chart_url')

            if chart_url:
                html_response = requests.get(f"{base_url}{chart_url}")
                if html_response.status_code == 200:
                    html_content = html_response.text

                    # 检查模拟数据的黄色样式
                    if "background-color: #fff3cd" in html_content and "border-left: 4px solid #ffc107" in html_content:
                        print("  ✅ 模拟数据样式正确 (黄色背景)")
                    else:
                        print("  ⚠️ 模拟数据样式可能不正确")

                    # 检查真实数据的绿色样式
                    if "background-color: #d4edda" in html_content and "border-left: 4px solid #28a745" in html_content:
                        print("  ✅ 真实数据样式正确 (绿色背景)")
                    else:
                        print("  ℹ️ 未检测到真实数据样式 (可能为模拟数据)")
        else:
            print("  ❌ 无法获取chart_url")
    except Exception as e:
        print(f"  ❌ 样式测试异常: {e}")

    # 测试5: 数据源统计
    print("\n📊 测试5: 数据源统计")
    try:
        # 获取多只股票的数据源信息
        test_codes = ["000001", "000888", "000999"]
        source_stats = {}

        for code in test_codes:
            try:
                response = requests.get(f"{base_url}/api/v1/stocks/{code}")
                if response.status_code == 200:
                    data = response.json()
                    stocks = data.get('data', {}).get('stocks', {})

                    if code in stocks:
                        data_source = stocks[code].get('data_source', 'unknown')
                        source_stats[data_source] = source_stats.get(data_source, 0) + 1
            except:
                continue

        print("  数据源分布统计:")
        for source, count in source_stats.items():
            display_name = {
                'akshare_primary': 'akShare 主要数据源',
                'akshare_alternative': 'akShare 备用数据源',
                'sina': '新浪财经',
                'tencent': '腾讯财经',
                'mock': '模拟数据 (演示)',
                'unknown': '未知数据源'
            }.get(source, source)
            print(f"    {display_name}: {count} 只股票")

        total = sum(source_stats.values())
        print(f"    总计: {total} 只股票")

    except Exception as e:
        print(f"  ❌ 统计测试异常: {e}")

    print("\n" + "=" * 60)
    print("🎉 数据源标注功能测试完成！")

if __name__ == "__main__":
    test_data_source_annotations()