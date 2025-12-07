#!/usr/bin/env python3
"""
测试指数成分股HTML可视化功能
"""
import requests
import json
import time
from datetime import datetime

def test_constituents_html():
    """测试指数成分股HTML可视化功能"""
    base_url = "http://localhost:8000"

    print("🧪 测试指数成分股HTML可视化功能...")
    print("=" * 50)

    # 测试1: 基础成分股查询并生成HTML
    print("\n📊 测试1: 沪深300成分股查询 + HTML生成")
    try:
        url = f"{base_url}/api/v1/indices/沪深300/constituents?limit=10&generate_html=true"
        response = requests.get(url, timeout=30)

        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"指数名称: {data.get('index_name')}")
            print(f"总成分股数: {data.get('total_count')}")
            print(f"返回数量: {data.get('returned_count')}")

            if 'html_url' in data:
                html_url = f"{base_url}{data['html_url']}"
                print(f"📄 HTML文件已生成: {html_url}")

                # 验证HTML文件是否可访问
                html_response = requests.get(html_url, timeout=10)
                if html_response.status_code == 200:
                    print("✅ HTML文件访问成功")
                    print(f"文件大小: {len(html_response.content)} 字节")
                else:
                    print(f"❌ HTML文件访问失败: {html_response.status_code}")
            else:
                print("⚠️ 未生成HTML文件")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 请求异常: {e}")

    time.sleep(2)

    # 测试2: 详细成分股查询并生成HTML
    print("\n📊 测试2: 中证100成分股详细查询 + HTML生成")
    try:
        url = f"{base_url}/api/v1/indices/中证100/constituents/details?limit=5&generate_html=true"
        response = requests.get(url, timeout=60)  # 详细查询需要更长时间

        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"指数名称: {data.get('index_name')}")
            print(f"查询总数: {data.get('total_count')}")
            print(f"成功获取: {data.get('successful_count')}")
            print(f"失败数量: {data.get('failed_count')}")

            if 'html_url' in data:
                html_url = f"{base_url}{data['html_url']}"
                print(f"📄 详细HTML文件已生成: {html_url}")

                # 验证HTML文件是否可访问
                html_response = requests.get(html_url, timeout=10)
                if html_response.status_code == 200:
                    print("✅ 详细HTML文件访问成功")
                    print(f"文件大小: {len(html_response.content)} 字节")

                    # 检查HTML内容是否包含预期的元素
                    if '统计信息' in html_response.text and '数据可视化' in html_response.text:
                        print("✅ HTML内容包含预期的可视化元素")
                    else:
                        print("⚠️ HTML内容可能缺少某些可视化元素")
                else:
                    print(f"❌ 详细HTML文件访问失败: {html_response.status_code}")
            else:
                print("⚠️ 未生成详细HTML文件")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 请求异常: {e}")

    time.sleep(2)

    # 测试3: 测试不生成HTML的普通查询
    print("\n📊 测试3: 中证500成分股普通查询（不生成HTML）")
    try:
        url = f"{base_url}/api/v1/indices/中证500/constituents?limit=5"
        response = requests.get(url, timeout=30)

        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 普通查询成功")
            print(f"指数名称: {data.get('index_name')}")
            print(f"总成分股数: {data.get('total_count')}")
            print(f"返回数量: {data.get('returned_count')}")

            if 'html_url' not in data:
                print("✅ 确认未生成HTML文件（符合预期）")
            else:
                print("⚠️ 意外生成了HTML文件")
        else:
            print(f"❌ 普通查询失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 普通查询异常: {e}")

    time.sleep(2)

    # 测试4: 错误处理测试（不存在的指数）
    print("\n📊 测试4: 错误处理测试（不存在的指数）")
    try:
        url = f"{base_url}/api/v1/indices/不存在的指数/constituents?generate_html=true"
        response = requests.get(url, timeout=30)

        print(f"状态码: {response.status_code}")
        if response.status_code == 404:
            print("✅ 正确处理了不存在的指数请求")
        else:
            print(f"⚠️ 状态码不符合预期: {response.status_code}")

    except Exception as e:
        print(f"❌ 错误处理测试异常: {e}")

    print("\n" + "=" * 50)
    print("🎉 指数成分股HTML可视化功能测试完成！")
    print("💡 提示: 你可以在浏览器中访问生成的HTML文件查看可视化效果")

if __name__ == "__main__":
    test_constituents_html()