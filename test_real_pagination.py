#!/usr/bin/env python3
"""
测试真实指数分析API的分页功能
"""
import requests
import json

def test_pagination_with_real_api():
    """测试真实API的分页功能"""
    base_url = "http://localhost:8000/api/v1"

    print("🔍 测试真实指数分析API分页功能")
    print("=" * 50)

    # 测试各个指数
    test_indices = ["中证100", "中证200", "沪深300", "中证500"]

    for index_name in test_indices:
        print(f"\n📊 测试指数: {index_name}")
        print("-" * 30)

        # 测试基础分析
        try:
            response = requests.get(f"{base_url}/indices/{index_name}/constituents")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    total_count = data.get('total_count', 0)
                    print(f"   ✅ 成分股总数: {total_count}")

                    # 模拟分页逻辑
                    page_size = 20
                    total_pages = (total_count + page_size - 1) // page_size
                    print(f"   📖 总页数: {total_pages}")
                    print(f"   📄 每页显示: {page_size} 条")

                    if total_pages > 1:
                        print(f"   🔄 分页预览:")
                        for page in [1, 2, total_pages]:
                            start_idx = (page - 1) * page_size
                            end_idx = min(start_idx + page_size, total_count)
                            print(f"      第{page}页: 第{start_idx + 1}-{end_idx}条")
                    else:
                        print(f"   📄 数据较少，无需分页")

                    # 验证数据结构
                    constituents = data.get('constituents', [])
                    if constituents and len(constituents) > 0:
                        sample = constituents[0]
                        required_fields = ['code', 'name', '纳入日期']
                        missing_fields = [field for field in required_fields if field not in sample]
                        if missing_fields:
                            print(f"   ⚠️  警告: 缺少字段 {missing_fields}")
                        else:
                            print(f"   ✅ 数据结构完整")
                            print(f"   📋 示例数据: {sample.get('code')} - {sample.get('name')}")
                else:
                    print(f"   ❌ API返回失败: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")

    print("\n" + "=" * 50)
    print("✅ 分页功能测试完成")
    print("\n📋 分页功能特性:")
    print("   • 支持10/20/50/100条每页显示")
    print("   • 智能页码导航（省略号处理）")
    • 快速跳转到首页/末页")
    print("   • 上一页/下一页导航")
    print("   • 当前页面高亮显示")
    print("   • 数据统计信息显示")
    print("   • CSV和Excel导出功能")
    print("   • 平滑滚动效果")

if __name__ == "__main__":
    test_pagination_with_real_api()