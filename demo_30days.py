#!/usr/bin/env python3
"""
演示近1个月（30天）股票交易信息
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

def generate_mock_stock_data_30days(code: str, name: str, days: int = 30) -> pd.DataFrame:
    """生成30天模拟股票数据"""

    # 生成日期序列
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days, 0, -1)]  # 只取工作日
    dates.reverse()  # 从早到晚

    # 模拟价格数据（以宁德时代为例）
    base_price = 180.0  # 基准价格

    # 生成价格走势（带有一定趋势和随机性）
    np.random.seed(300)  # 确保可重复性

    # 模拟更复杂的价格走势
    prices = [base_price]
    trend = np.sin(np.linspace(0, 2*np.pi, days)) * 10  # 添加周期性趋势

    for i in range(1, days):
        # 结合趋势和随机波动
        random_change = np.random.normal(0, 0.03)  # 日均涨跌幅
        trend_change = (trend[i] - trend[i-1]) / base_price * 0.5
        total_change = random_change + trend_change

        new_price = prices[-1] * (1 + total_change)
        prices.append(max(new_price, 10))  # 确保价格不会过低

    data = []
    for i, date in enumerate(dates):
        price = prices[i]

        # 生成开高低收（日内波动）
        open_price = price * (1 + np.random.normal(0, 0.01))
        close_price = price
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.015)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.015)))

        # 生成成交量（百万股）
        base_volume = 15.0  # 基础成交量
        volume_change = np.random.normal(0, 0.4)
        volume = base_volume * (1 + volume_change)
        volume = max(5.0, volume)  # 确保成交量不为负

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

def analyze_30days_stock_data(code: str = "300750", name: str = "宁德时代"):
    """分析近1个月股票数据"""

    print(f"🔍 正在分析 {name}({code}) 近1个月交易数据...")
    print("=" * 60)

    # 生成模拟数据
    df = generate_mock_stock_data_30days(code, name, days=30)

    # 计算技术指标
    indicators = TechnicalIndicators()
    df_with_indicators = indicators.calculate_basic_indicators(df)

    # 获取近30天数据
    latest_date = df_with_indicators['date'].max()
    start_date = latest_date - timedelta(days=30)
    df_30days = df_with_indicators[df_with_indicators['date'] >= start_date].copy()

    print(f"📊 近1个月数据 ({df_30days['date'].min().strftime('%Y-%m-%d')} 至 {df_30days['date'].max().strftime('%Y-%m-%d')})")
    print("-" * 60)

    # 基础交易数据
    print(f"📈 价格信息 (每5天汇总):")
    for i in range(0, len(df_30days), 5):
        chunk = df_30days.iloc[i:i+5]
        if not chunk.empty:
            first_row = chunk.iloc[0]
            last_row = chunk.iloc[-1]
            period_change = (last_row['close'] - first_row['open']) / first_row['open'] * 100
            print(f"  {first_row['date'].strftime('%m-%d')} - {last_row['date'].strftime('%m-%d')}: "
                  f"从{first_row['open']:.2f}到{last_row['close']:.2f} "
                  f"({period_change:+.2f}%)")

    # 成交量信息
    print(f"\n💰 成交量统计:")
    avg_volume = df_30days['volume'].mean()
    max_volume = df_30days['volume'].max()
    min_volume = df_30days['volume'].min()
    total_amount = df_30days['amount'].sum()

    print(f"  平均成交量: {avg_volume:.2f}万股")
    print(f"  最大成交量: {max_volume:.2f}万股 ({df_30days.loc[df_30days['volume'].idxmax(), 'date'].strftime('%m-%d')})")
    print(f"  最小成交量: {min_volume:.2f}万股 ({df_30days.loc[df_30days['volume'].idxmin(), 'date'].strftime('%m-%d')})")
    print(f"  总成交额: {total_amount:.2f}亿元")

    # 技术指标
    print(f"\n📊 技术指标 (最新):")
    latest = df_30days.iloc[-1]
    print(f"  最新价格: {latest['close']:.2f}元")
    print(f"  MA5:      {latest.get('MA5', 'N/A'):.2f}")
    print(f"  MA10:     {latest.get('MA10', 'N/A'):.2f}")
    print(f"  MA20:     {latest.get('MA20', 'N/A'):.2f}")
    print(f"  RSI:      {latest.get('RSI', 'N/A'):.2f}" if pd.notna(latest.get('RSI')) else "  RSI:      N/A")
    print(f"  MACD:     {latest.get('MACD', 'N/A'):.4f}" if pd.notna(latest.get('MACD')) else "  MACD:     N/A")
    print(f"  布林带位置: {latest.get('BB_Position', 'N/A'):.1f}%" if pd.notna(latest.get('BB_Position')) else "  布林带位置: N/A")

    # 统计数据
    print(f"\n📈 近1个月统计:")
    price_change = latest['close'] - df_30days.iloc[0]['close']
    price_change_pct = (price_change / df_30days.iloc[0]['close']) * 100
    max_price = df_30days['high'].max()
    min_price = df_30days['low'].min()
    max_single_day_gain = df_30days['change_pct'].max()
    max_single_day_loss = df_30days['change_pct'].min()
    positive_days = len(df_30days[df_30days['change_pct'] > 0])
    negative_days = len(df_30days[df_30days['change_pct'] < 0])

    print(f"  价格变化: {price_change:+.2f}元 ({price_change_pct:+.2f}%)")
    print(f"  价格区间: {min_price:.2f} - {max_price:.2f}元 (振幅: {((max_price/min_price-1)*100):+.2f}%)")
    print(f"  单日最大涨幅: {max_single_day_gain:+.2f}%")
    print(f"  单日最大跌幅: {max_single_day_loss:+.2f}%")
    print(f"  上涨天数: {positive_days}天 ({positive_days/len(df_30days)*100:.1f}%)")
    print(f"  下跌天数: {negative_days}天 ({negative_days/len(df_30days)*100:.1f}%)")
    print(f"  平盘天数: {len(df_30days)-positive_days-negative_days}天")

    # 波动性分析
    print(f"\n📊 波动性分析:")
    volatility = df_30days['change_pct'].std()
    mean_change = df_30days['change_pct'].mean()
    print(f"  日均涨跌幅: {mean_change:+.2f}%")
    print(f"  涨跌幅标准差: {volatility:.2f}%")
    print(f"  年化波动率: {volatility * np.sqrt(252):.2f}%")

    # 生成详细分析结果
    analysis_result = {
        "stock_info": {
            "code": code,
            "name": name,
            "analysis_date": datetime.now().isoformat(),
            "period": "近1个月"
        },
        "summary": {
            "start_date": df_30days['date'].min().strftime('%Y-%m-%d'),
            "end_date": df_30days['date'].max().strftime('%Y-%m-%d'),
            "trading_days": len(df_30days),
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "avg_volume": round(avg_volume, 2),
            "total_amount": round(total_amount, 2),
            "max_single_day_gain": round(max_single_day_gain, 2),
            "max_single_day_loss": round(max_single_day_loss, 2),
            "positive_days": positive_days,
            "negative_days": negative_days,
            "volatility": round(volatility, 2),
            "annualized_volatility": round(volatility * np.sqrt(252), 2)
        },
        "daily_data": []
    }

    # 添加每日详细数据
    for _, row in df_30days.iterrows():
        daily_info = {
            "date": row['date'].strftime('%Y-%m-%d'),
            "price": {
                "open": round(row['open'], 2),
                "high": round(row['high'], 2),
                "low": round(row['low'], 2),
                "close": round(row['close'], 2),
                "change": round(row['change_pct'], 2),
                "amplitude": round(row['amplitude'], 2)
            },
            "volume": {
                "volume": round(row['volume'], 2),
                "amount": round(row['amount'], 2),
                "turnover": round(row['turnover'], 2)
            },
            "indicators": {
                "ma5": round(row.get('MA5', 0), 2),
                "ma10": round(row.get('MA10', 0), 2),
                "ma20": round(row.get('MA20', 0), 2),
                "rsi": round(row.get('RSI', 0), 2) if pd.notna(row.get('RSI')) else None,
                "macd": round(row.get('MACD', 0), 4) if pd.notna(row.get('MACD')) else None,
                "bb_position": round(row.get('BB_Position', 0), 1) if pd.notna(row.get('BB_Position')) else None,
                "volume_ratio": round(row.get('Volume_Ratio', 1), 2) if pd.notna(row.get('Volume_Ratio')) else None
            }
        }
        analysis_result["daily_data"].append(daily_info)

    # 保存结果
    output_file = f"static/stock_30days_{code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("static", exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 详细数据已保存至: {output_file}")

    # 返回数据供可视化使用
    return analysis_result, df_30days

if __name__ == "__main__":
    # 分析宁德时代近1个月数据
    result, df_30days = analyze_30days_stock_data("300750", "宁德时代")

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print(f"📊 数据覆盖: {result['summary']['trading_days']} 个交易日")
    print(f"📈 总体表现: {result['summary']['price_change_pct']:+.2f}%")
    print(f"📊 年化波动率: {result['summary']['annualized_volatility']:.2f}%")
    print("=" * 60)