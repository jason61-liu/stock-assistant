#!/usr/bin/env python3
"""
演示近7天股票交易信息
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.indicators import TechnicalIndicators
from src.visualizer import StockVisualizer

def generate_mock_stock_data(code: str, name: str, days: int = 30) -> pd.DataFrame:
    """生成模拟股票数据"""

    # 生成日期序列
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days)]
    dates.reverse()  # 从早到晚

    # 模拟价格数据（以贵州茅台为例）
    base_price = 1680.0  # 基准价格

    # 生成价格走势（带有一定趋势和随机性）
    np.random.seed(42)  # 确保可重复性

    # 模拟价格波动
    price_changes = np.random.normal(0, 0.02, days)  # 日均涨跌幅
    price_changes[::5] += np.random.normal(0, 0.01, days//5)  # 每周额外波动

    prices = [base_price]
    for change in price_changes[1:]:
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)

    data = []
    for i, date in enumerate(dates):
        price = prices[i]

        # 生成开高低收（日内波动）
        open_price = price * (1 + np.random.normal(0, 0.005))
        close_price = price
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.008)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.008)))

        # 生成成交量（百万股）
        base_volume = 2.5
        volume = base_volume * (1 + np.random.normal(0, 0.3))
        volume = max(0.5, volume)  # 确保成交量不为负

        # 计算成交额（亿元）
        amount = volume * price / 100  # 转换为亿元

        # 计算涨跌幅等指标
        price_change = close_price - open_price
        price_change_pct = (price_change / open_price) * 100
        amplitude = ((high_price - low_price) / low_price) * 100
        turnover = volume / 100  # 假设总股本为100亿股

        data.append({
            'date': date.date(),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': round(volume, 2),
            'amount': round(amount, 2),
            'change_pct': round(price_change_pct, 2),
            'amplitude': round(amplitude, 2),
            'turnover': round(turnover, 2)
        })

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    return df

def analyze_7days_stock_data(code: str = "600519", name: str = "贵州茅台"):
    """分析近7天股票数据"""

    print(f"🔍 正在分析 {name}({code}) 近7天交易数据...")
    print("=" * 60)

    # 生成模拟数据
    df = generate_mock_stock_data(code, name, days=30)

    # 计算技术指标
    indicators = TechnicalIndicators()
    df_with_indicators = indicators.calculate_basic_indicators(df)

    # 获取近7天数据
    latest_date = df_with_indicators['date'].max()
    start_date = latest_date - timedelta(days=7)
    df_7days = df_with_indicators[df_with_indicators['date'] >= start_date].copy()

    print(f"📊 近7个交易日数据 ({df_7days['date'].min().strftime('%Y-%m-%d')} 至 {df_7days['date'].max().strftime('%Y-%m-%d')})")
    print("-" * 60)

    # 基础交易数据
    print("📈 价格信息:")
    for _, row in df_7days.iterrows():
        print(f"  {row['date'].strftime('%m-%d')}: "
              f"开{row['open']:>8.2f} 高{row['high']:>8.2f} "
              f"低{row['low']:>8.2f} 收{row['close']:>8.2f} "
              f"涨跌幅{row['change_pct']:>6.2f}%")

    # 成交量信息
    print(f"\n💰 成交量信息:")
    for _, row in df_7days.iterrows():
        print(f"  {row['date'].strftime('%m-%d')}: "
              f"成交量{row['volume']:>6.2f}万股 "
              f"成交额{row['amount']:>8.2f}亿元 "
              f"换手率{row['turnover']:>5.2f}%")

    # 技术指标
    print(f"\n📊 技术指标 (最新):")
    latest = df_7days.iloc[-1]
    print(f"  最新价格: {latest['close']:.2f}元")
    print(f"  MA5:      {latest.get('MA5', 'N/A')}")
    print(f"  MA20:     {latest.get('MA20', 'N/A')}")
    print(f"  RSI:      {latest.get('RSI', 'N/A'):.2f}" if pd.notna(latest.get('RSI')) else "  RSI:      N/A")
    print(f"  MACD:     {latest.get('MACD', 'N/A'):.4f}" if pd.notna(latest.get('MACD')) else "  MACD:     N/A")

    # 统计数据
    print(f"\n📈 近7天统计:")
    price_change = latest['close'] - df_7days.iloc[0]['close']
    price_change_pct = (price_change / df_7days.iloc[0]['close']) * 100
    avg_volume = df_7days['volume'].mean()
    max_price = df_7days['high'].max()
    min_price = df_7days['low'].min()

    print(f"  价格变化: {price_change:+.2f}元 ({price_change_pct:+.2f}%)")
    print(f"  价格区间: {min_price:.2f} - {max_price:.2f}元")
    print(f"  平均成交量: {avg_volume:.2f}万股")
    print(f"  总成交额: {df_7days['amount'].sum():.2f}亿元")

    # 生成详细分析结果
    analysis_result = {
        "stock_info": {
            "code": code,
            "name": name,
            "analysis_date": datetime.now().isoformat(),
            "period": "近7个交易日"
        },
        "summary": {
            "start_date": df_7days['date'].min().strftime('%Y-%m-%d'),
            "end_date": df_7days['date'].max().strftime('%Y-%m-%d'),
            "trading_days": len(df_7days),
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "avg_volume": round(avg_volume, 2),
            "total_amount": round(df_7days['amount'].sum(), 2)
        },
        "daily_data": []
    }

    # 添加每日详细数据
    for _, row in df_7days.iterrows():
        daily_info = {
            "date": row['date'].strftime('%Y-%m-%d'),
            "price": {
                "open": round(row['open'], 2),
                "high": round(row['high'], 2),
                "low": round(row['low'], 2),
                "close": round(row['close'], 2),
                "change": round(row['change_pct'], 2)
            },
            "volume": {
                "volume": round(row['volume'], 2),
                "amount": round(row['amount'], 2),
                "turnover": round(row['turnover'], 2)
            },
            "indicators": {
                "ma5": round(row.get('MA5', 0), 2),
                "ma20": round(row.get('MA20', 0), 2),
                "rsi": round(row.get('RSI', 0), 2) if pd.notna(row.get('RSI')) else None,
                "macd": round(row.get('MACD', 0), 4) if pd.notna(row.get('MACD')) else None
            }
        }
        analysis_result["daily_data"].append(daily_info)

    # 保存结果
    output_file = f"static/stock_7days_{code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("static", exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 详细数据已保存至: {output_file}")

    # 生成可视化图表
    try:
        visualizer = StockVisualizer()
        chart_file = f"static/chart_7days_{code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        # 创建价格图表
        price_chart = visualizer.create_price_chart(df_7days, f"{name}({code}) 近7天价格走势")

        # 创建技术指标图表
        indicators_chart = visualizer.create_indicators_chart(df_7days, f"{name}({code}) 技术指标")

        # 生成HTML文件
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{name}({code}) 近7天交易分析</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart-container {{ margin: 20px 0; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; }}
            </style>
        </head>
        <body>
            <h1>{name}({code}) 近7个交易日分析报告</h1>

            <div class="summary">
                <h2>📊 交易摘要</h2>
                <p><strong>分析期间:</strong> {analysis_result['summary']['start_date']} 至 {analysis_result['summary']['end_date']}</p>
                <p><strong>价格变化:</strong> {price_change:+.2f}元 ({price_change_pct:+.2f}%)</p>
                <p><strong>价格区间:</strong> {min_price:.2f} - {max_price:.2f}元</p>
                <p><strong>平均成交量:</strong> {avg_volume:.2f}万股</p>
                <p><strong>总成交额:</strong> {analysis_result['summary']['total_amount']:.2f}亿元</p>
            </div>

            <div class="chart-container">
                <div id="price-chart"></div>
                <script>
                    Plotly.newPlot('price-chart', {json.dumps(price_chart, cls=visualizer.__class__.__bases__[0].__bases__[0].__module__.replace('pandas.io.json', 'plotly.utils').split('.')[0] if 'plotly' in str(visualizer.__class__.__bases__[0].__bases__[0].__module__) else 'plotly.utils').replace('plotly.utils', 'plotly.utils')});
                </script>
            </div>

            <div class="chart-container">
                <div id="indicators-chart"></div>
                <script>
                    Plotly.newPlot('indicators-chart', {json.dumps(indicators_chart, cls=visualizer.__class__.__bases__[0].__bases__[0].__module__.replace('pandas.io.json', 'plotly.utils').split('.')[0] if 'plotly' in str(visualizer.__class__.__bases__[0].__bases__[0].__module__) else 'plotly.utils').replace('plotly.utils', 'plotly.utils')});
                </script>
            </div>
        </body>
        </html>
        """

        with open(chart_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📈 可视化图表已生成: {chart_file}")

    except Exception as e:
        print(f"⚠️  图表生成失败: {e}")

    return analysis_result

if __name__ == "__main__":
    # 分析贵州茅台近7天数据
    result = analyze_7days_stock_data("600519", "贵州茅台")

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print(f"📊 数据覆盖: {result['summary']['trading_days']} 个交易日")
    print(f"📈 总体表现: {result['summary']['price_change_pct']:+.2f}%")
    print("=" * 60)