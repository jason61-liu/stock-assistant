#!/usr/bin/env python3

import sys
import traceback
from src.analyzer import StockAnalyzer
from src.data_fetcher import DataFetcher

def test_numpy_error():
    """Test to trigger numpy error and get full traceback"""
    print("Testing numpy error...")

    analyzer = StockAnalyzer()
    data_fetcher = DataFetcher()

    # Test with problematic stock code
    test_code = "600041"
    print(f"Analyzing stock {test_code}...")

    # Get raw data fetcher to trigger error directly
    df = data_fetcher.get_stock_basic_data(test_code)
    print(f"Got data: {len(df)} rows")

    # Now try to analyze - this should trigger the error
    result = analyzer.analyze_single_stock(test_code, f"股票{test_code}")
    print("Success! No error occurred.")

    return True

if __name__ == "__main__":
    success = test_numpy_error()
    sys.exit(0 if success else 1)