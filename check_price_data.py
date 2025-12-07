#!/usr/bin/env python3
"""
检查指数成分股价格数据
"""
import requests
import json

def test_index_price_data():
    """测试指数成分股价格数据"""
    base_url = 'http://localhost:8000/api/v1'
    index_name = '中证100'

    try:
        response = requests.get(f'{base_url}/indices/{index_name}/constituents/details')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                constituents = data.get('constituents', [])
                for i, stock in enumerate(constituents[:3]):  # 只看前3个
                    print(f'\n--- 股票 {i+1}: {stock.get("name")} ---')
                    print(f'代码: {stock.get("code")}')
                    basic_info = stock.get('basic_info', {})
                    if basic_info:
                        print(f'basic_info字段: {list(basic_info.keys())}')
                        print(f'最新价字段: {basic_info.get("最新价", "无")}')
                        print(f'当前价格字段: {basic_info.get("当前价格", "无")}')
                        print(f'价格相关字段: {[k for k in basic_info.keys() if "价" in k]}')
                    else:
                        print('basic_info为空')

                    error = stock.get('error')
                    if error:
                        print(f'错误信息: {error}')
    except Exception as e:
        print(f'请求异常: {e}')

if __name__ == "__main__":
    test_index_price_data()