#!/usr/bin/env python3
"""
测试akShare指数成分股功能
"""
import akshare as ak
import pandas as pd
import sys
import os

def test_akshare_functions():
    print("测试akShare指数相关函数...")

    try:
        # 检查ak.index_stock_cons函数的参数
        import inspect
        sig = inspect.signature(ak.index_stock_cons)
        print(f"\nindex_stock_cons 函数签名: {sig}")

        # 测试不传参数调用
        print("\n测试不传参数调用:")
        try:
            df = ak.index_stock_cons()
            print(f"成功获取数据，形状: {df.shape}")
            print("列名:", df.columns.tolist())
            if not df.empty:
                print("前几行数据:")
                print(df.head())
        except Exception as e:
            print(f"调用失败: {e}")

        # 测试使用symbol参数
        print("\n测试使用symbol参数:")
        try:
            df = ak.index_stock_cons(symbol="000300")
            print(f"成功获取数据，形状: {df.shape}")
            print("列名:", df.columns.tolist())
            if not df.empty:
                print("前几行数据:")
                print(df.head())
        except Exception as e:
            print(f"调用失败: {e}")

        # 测试不同的指数代码
        indices = ["000300", "000903", "000904", "000905"]
        for code in indices:
            print(f"\n测试指数代码 {code}:")
            try:
                df = ak.index_stock_cons(symbol=code)
                print(f"✅ 成功，成分股数量: {len(df) if df is not None else 0}")
            except Exception as e:
                print(f"❌ 失败: {e}")

    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_akshare_functions()