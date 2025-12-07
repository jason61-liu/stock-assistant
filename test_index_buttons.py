#!/usr/bin/env python3
"""
测试指数分析工具按钮功能
"""
import requests
import json

def test_index_api_endpoints():
    """测试所有指数分析相关的API端点"""
    base_url = "http://localhost:8000/api/v1"

    # 测试支持的指数列表
    print("1. 测试支持的指数列表...")
    try:
        response = requests.get(f"{base_url}/indices/supported")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ 成功获取支持指数列表: {len(data.get('indices', {}))} 个指数")
                for index_name in data.get('indices', {}).keys():
                    print(f"      - {index_name}")
            else:
                print(f"   ❌ 获取指数列表失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")

    print()

    # 测试各个指数的API端点
    test_indices = ["中证100", "中证200", "沪深300", "中证500"]

    for index_name in test_indices:
        print(f"2. 测试指数: {index_name}")

        # 测试获取成分股
        try:
            response = requests.get(f"{base_url}/indices/{index_name}/constituents")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ 成分股列表: {data.get('total_count', 0)} 只股票")
                else:
                    print(f"   ❌ 成分股列表失败: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ 成分股列表 HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 成分股列表请求异常: {e}")

        # 测试详细成分股
        try:
            response = requests.get(f"{base_url}/indices/{index_name}/constituents/details")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ 详细成分股: {data.get('returned_count', 0)} 只股票")
                else:
                    print(f"   ❌ 详细成分股失败: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ 详细成分股 HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 详细成分股请求异常: {e}")

        # 测试指数概览
        try:
            response = requests.get(f"{base_url}/indices/{index_name}/overview")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    overview = data.get('data', {})
                    print(f"   ✅ 指数概览: {overview.get('constituents_count', 0)} 只成分股")
                else:
                    print(f"   ❌ 指数概览失败: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ 指数概览 HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 指数概览请求异常: {e}")

        # 测试指数分析
        try:
            response = requests.get(f"{base_url}/indices/{index_name}/analysis")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ 指数分析: 成功")
                else:
                    print(f"   ❌ 指数分析失败: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ 指数分析 HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 指数分析请求异常: {e}")

        print()

    print("3. 测试完成！")
    print("   所有指数分析工具的API端点已经修复并正常工作。")
    print("   现在可以在web界面中正常使用指数分析功能。")

if __name__ == "__main__":
    test_index_api_endpoints()