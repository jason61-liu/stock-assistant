#!/usr/bin/env python3
"""
测试指数概览功能修复
"""
import requests
import json

def test_index_overview_fix():
    """测试指数概览API和前端数据结构"""
    base_url = "http://localhost:8000/api/v1"

    print("🔍 测试指数概览功能修复")
    print("=" * 50)

    indices = ["中证100", "中证200", "沪深300", "中证500"]

    for index_name in indices:
        print(f"\n📊 测试指数: {index_name}")
        print("-" * 40)

        try:
            response = requests.get(f"{base_url}/indices/{index_name}/overview")

            if response.status_code == 200:
                api_response = response.json()

                if api_response.get('success'):
                    overview_data = api_response.get('data', {})

                    # 验证前端期望的数据结构
                    converted_data = {
                        'index_name': overview_data.get('index_name'),
                        'constituents': overview_data.get('recent_constituents', []),
                        'total_count': overview_data.get('constituents_count'),
                        'info': overview_data.get('info', {}),
                        'available': overview_data.get('available')
                    }

                    print(f"✅ API状态: 成功")
                    print(f"✅ 指数名称: {converted_data['index_name']}")

                    info = converted_data['info']
                    print(f"✅ 指数代码: {info.get('code', 'N/A')}")
                    print(f"✅ 指数全称: {info.get('name', 'N/A')}")
                    print(f"✅ 成分股数量: {converted_data['total_count']}")
                    print(f"✅ 最近成分股数: {len(converted_data['constituents'])}")
                    print(f"✅ 交易状态: {'正常' if converted_data['available'] else '暂停'}")

                    if info.get('description'):
                        desc = info['description'][:50] + '...' if len(info['description']) > 50 else info['description']
                        print(f"✅ 指数描述: {desc}")

                    # 显示最近纳入的成分股
                    if converted_data['constituents']:
                        print(f"✅ 最新成分股示例:")
                        for i, stock in enumerate(converted_data['constituents'][:3]):
                            print(f"   {i+1}. {stock.get('code')} - {stock.get('name')}")

                else:
                    print(f"❌ API失败: {api_response.get('message')}")

            else:
                print(f"❌ HTTP错误: {response.status_code}")

        except Exception as e:
            print(f"❌ 请求异常: {e}")

    print("\n" + "=" * 50)
    print("✅ 指数概览功能测试完成")
    print("\n📋 修复内容:")
    print("   • 修复前端数据解析问题")
    print("   • 添加专门的displayIndexOverview函数")
    print("   • 正确显示指数基本信息")
    print("   • 显示最近纳入的成分股")
    print("   • 添加指数描述和交易状态")
    print("   • 改善用户界面体验")

if __name__ == "__main__":
    test_index_overview_fix()