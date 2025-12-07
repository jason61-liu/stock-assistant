#!/usr/bin/env python3
"""
测试完整成分股HTML可视化功能
"""
import requests
import json
import time
from datetime import datetime

def test_full_constituents_html():
    """测试完整成分股HTML可视化功能"""
    base_url = "http://localhost:8000"

    print("🧪 测试完整成分股HTML可视化功能...")
    print("=" * 60)

    # 测试1: 沪深300完整成分股HTML生成
    print("\n📊 测试1: 沪深300完整成分股HTML生成")
    try:
        url = f"{base_url}/api/v1/indices/沪深300/constituents?generate_html=true"
        response = requests.get(url, timeout=60)

        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"指数名称: {data.get('index_name')}")
            print(f"总成分股数: {data.get('total_count')}")
            print(f"JSON返回数量: {data.get('returned_count')}")
            print(f"HTML包含数量: {data.get('html_generated_count')}")

            if 'html_url' in data:
                html_url = f"{base_url}{data['html_url']}"
                print(f"📄 完整HTML文件: {html_url}")

                # 验证HTML文件
                html_response = requests.get(html_url, timeout=10)
                if html_response.status_code == 200:
                    file_size = len(html_response.content)
                    print(f"✅ HTML文件访问成功，大小: {file_size:,} 字节")

                    # 检查HTML中是否包含所有数据
                    html_content = html_response.text
                    total_count_str = str(data.get('total_count', 0))
                    occurrences = html_content.count(total_count_str)
                    print(f"📊 HTML中包含成分股数量 {total_count_str} 的次数: {occurrences}")

                    if occurrences >= 3:  # 应该在多个地方显示这个数字
                        print("✅ HTML正确显示了完整成分股数据")
                    else:
                        print("⚠️ HTML可能没有显示完整数据")

                else:
                    print(f"❌ HTML文件访问失败: {html_response.status_code}")
            else:
                print("❌ 未生成HTML文件")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 请求异常: {e}")

    time.sleep(3)

    # 测试2: 中证500完整成分股HTML生成
    print("\n📊 测试2: 中证500完整成分股HTML生成")
    try:
        url = f"{base_url}/api/v1/indices/中证500/constituents?generate_html=true"
        response = requests.get(url, timeout=60)

        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"指数名称: {data.get('index_name')}")
            print(f"总成分股数: {data.get('total_count')}")
            print(f"HTML包含数量: {data.get('html_generated_count')}")

            if 'html_url' in data:
                html_url = f"{base_url}{data['html_url']}"
                html_response = requests.get(html_url, timeout=10)
                if html_response.status_code == 200:
                    file_size = len(html_response.content)
                    print(f"✅ HTML文件大小: {file_size:,} 字节")
                else:
                    print(f"❌ HTML文件访问失败: {html_response.status_code}")
        else:
            print(f"❌ 请求失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")

    time.sleep(3)

    # 测试3: 对比有限制和无限制的请求
    print("\n📊 测试3: 对比有限制和无限制的请求")
    try:
        # 有限制的请求
        url_limited = f"{base_url}/api/v1/indices/沪深300/constituents?limit=10"
        response_limited = requests.get(url_limited, timeout=30)

        # 无限制的请求
        url_unlimited = f"{base_url}/api/v1/indices/沪深300/constituents"
        response_unlimited = requests.get(url_unlimited, timeout=30)

        if response_limited.status_code == 200 and response_unlimited.status_code == 200:
            data_limited = response_limited.json()
            data_unlimited = response_unlimited.json()

            print(f"📋 限制10只的请求:")
            print(f"   总数: {data_limited.get('total_count')}, 返回: {data_limited.get('returned_count')}")

            print(f"📋 无限制的请求:")
            print(f"   总数: {data_unlimited.get('total_count')}, 返回: {data_unlimited.get('returned_count')}")

            if (data_limited.get('returned_count') == 10 and
                data_unlimited.get('returned_count') == data_unlimited.get('total_count')):
                print("✅ 限制功能正常工作")
            else:
                print("❌ 限制功能可能有问题")

    except Exception as e:
        print(f"❌ 对比测试异常: {e}")

    time.sleep(3)

    # 测试4: 验证HTML生成的完整数据
    print("\n📊 测试4: 验证HTML生成的完整数据")
    try:
        url = f"{base_url}/api/v1/indices/中证100/constituents?generate_html=true"
        response = requests.get(url, timeout=45)

        if response.status_code == 200:
            data = response.json()
            total_count = data.get('total_count', 0)
            html_generated_count = data.get('html_generated_count', 0)

            print(f"📈 指数: {data.get('index_name')}")
            print(f"📊 总成分股数: {total_count}")
            print(f"📄 HTML包含数: {html_generated_count}")

            # 验证HTML文件内容
            if 'html_url' in data:
                html_url = f"{base_url}{data['html_url']}"
                html_response = requests.get(html_url, timeout=10)

                if html_response.status_code == 200:
                    html_content = html_response.text

                    # 检查是否包含完整数据统计
                    if f"总计 {total_count} 只成分股" in html_content:
                        print("✅ HTML正确显示总成分股数量")

                    # 检查数据表格是否完整
                    table_rows = html_content.count('<tr>')
                    print(f"📋 HTML表格行数: {table_rows} (包含表头)")

                    if table_rows > total_count + 10:  # 应该大于股票数量加上表头和分页
                        print("✅ 数据表格包含完整数据")
                    else:
                        print("⚠️ 数据表格可能不完整")

        else:
            print(f"❌ 请求失败: {response.status_code}")

    except Exception as e:
        print(f"❌ HTML验证异常: {e}")

    print("\n" + "=" * 60)
    print("🎉 完整成分股HTML可视化功能测试完成！")
    print("💡 主要改进:")
    print("   - HTML生成时使用完整数据集，不受limit参数限制")
    print("   - JSON响应仍支持limit参数，保持灵活性")
    print("   - Web界面生成完整报告，包含所有成分股")

if __name__ == "__main__":
    test_full_constituents_html()