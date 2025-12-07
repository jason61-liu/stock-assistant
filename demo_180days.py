#!/usr/bin/env python3
"""
演示近半年（180天）股票交易信息
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.indicators import TechnicalIndicators

def generate_mock_stock_data_180days(code: str, name: str, days: int = 180) -> pd.DataFrame:
    """生成180天模拟股票数据"""

    # 生成日期序列（只包含工作日）
    end_date = datetime.now()
    dates = []
    current_date = end_date - timedelta(days=days)

    while current_date <= end_date:
        # 只添加工作日（排除周末）
        if current_date.weekday() < 5:  # 0-4 是周一到周五
            dates.append(current_date)
        current_date += timedelta(days=1)

    dates.reverse()  # 从早到晚

    # 模拟价格数据（以比亚迪为例）
    base_price = 250.0  # 基准价格

    # 设置随机种子确保可重复性
    np.random.seed(int(code[-6:]) if code.isdigit() else 180)

    # 生成复杂的价格走势模型
    prices = []

    # 模拟多个周期和趋势的组合
    trend1 = np.linspace(0, 0.3, len(dates))  # 长期上升趋势
    trend2 = np.sin(np.linspace(0, 4*np.pi, len(dates))) * 0.15  # 季度周期
    trend3 = np.sin(np.linspace(0, 12*np.pi, len(dates))) * 0.05  # 月度周期

    # 添加一些随机事件
    events = np.zeros(len(dates))
    for i in range(5):  # 5个随机事件
        event_day = np.random.randint(20, len(dates)-20)
        events[event_day:event_day+10] = np.random.normal(0, 0.1, 10)

    for i in range(len(dates)):
        # 组合所有趋势和随机性，减小波动幅度
        trend_change = (trend1[i] * 0.002) + (trend2[i] * 0.001) + (trend3[i] * 0.0005) + (events[i] * 0.001)
        random_change = np.random.normal(0, 0.02)  # 日随机波动

        total_change = trend_change + random_change

        if i == 0:
            price = base_price
        else:
            price = prices[-1] * (1 + total_change)
            price = max(price, 50)  # 设置最低价格
            price = min(price, 1000)  # 设置最高价格限制

        prices.append(price)

    data = []
    for i, date in enumerate(dates):
        price = prices[i]

        # 生成开高低收（日内波动）
        open_price = price * (1 + np.random.normal(0, 0.015))
        close_price = price
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.02)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.02)))

        # 生成成交量（考虑价格变化影响）
        base_volume = 20.0  # 基础成交量
        price_volatility = abs(total_change) * 500  # 价格波动影响成交量
        volume = base_volume + price_volatility + np.random.normal(0, 8)
        volume = max(5.0, volume)  # 确保成交量不为负

        # 计算成交额（亿元）
        amount = volume * price / 100

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

def analyze_180days_stock_data(code: str = "002594", name: str = "比亚迪"):
    """分析近半年股票数据"""

    print(f"🔍 正在分析 {name}({code}) 近半年交易数据...")
    print("=" * 60)

    # 生成模拟数据
    df = generate_mock_stock_data_180days(code, name, days=180)

    # 计算技术指标
    indicators = TechnicalIndicators()
    df_with_indicators = indicators.calculate_basic_indicators(df)

    # 获取近180天数据
    latest_date = df_with_indicators['date'].max()
    start_date = latest_date - timedelta(days=180)
    df_180days = df_with_indicators[df_with_indicators['date'] >= start_date].copy()

    print(f"📊 近半年数据 ({df_180days['date'].min().strftime('%Y-%m-%d')} 至 {df_180days['date'].max().strftime('%Y-%m-%d')})")
    print("-" * 60)

    # 基础交易数据（按月汇总）
    print(f"📈 价格信息 (按月汇总):")

    # 按月份分组统计
    df_180days['month'] = df_180days['date'].dt.to_period('M')
    monthly_stats = df_180days.groupby('month').agg({
        'open': 'first',
        'close': 'last',
        'high': 'max',
        'low': 'min',
        'volume': 'sum',
        'change_pct': lambda x: (x.iloc[-1] if len(x) > 1 else 0)
    })

    for month, stats in monthly_stats.iterrows():
        month_change = (stats['close'] - stats['open']) / stats['open'] * 100
        print(f"  {month}: {stats['open']:.2f} → {stats['close']:.2f} ({month_change:+.2f}%) "
              f"最高{stats['high']:.2f} 最低{stats['low']:.2f}")

    # 成交量信息
    print(f"\n💰 成交量统计:")
    avg_volume = df_180days['volume'].mean()
    max_volume = df_180days['volume'].max()
    min_volume = df_180days['volume'].min()
    total_amount = df_180days['amount'].sum()
    volume_std = df_180days['volume'].std()

    print(f"  平均成交量: {avg_volume:.2f}万股/日")
    print(f"  成交量标准差: {volume_std:.2f}万股")
    print(f"  最大成交量: {max_volume:.2f}万股 ({df_180days.loc[df_180days['volume'].idxmax(), 'date'].strftime('%m-%d')})")
    print(f"  最小成交量: {min_volume:.2f}万股 ({df_180days.loc[df_180days['volume'].idxmin(), 'date'].strftime('%m-%d')})")
    print(f"  总成交额: {total_amount:.0f}亿元")

    # 技术指标
    print(f"\n📊 技术指标 (最新):")
    latest = df_180days.iloc[-1]
    print(f"  最新价格: {latest['close']:.2f}元")
    print(f"  MA5:      {latest.get('MA5', 'N/A'):.2f}")
    print(f"  MA10:     {latest.get('MA10', 'N/A'):.2f}")
    print(f"  MA20:     {latest.get('MA20', 'N/A'):.2f}")
    print(f"  MA60:     {latest.get('MA60', 'N/A'):.2f}")
    print(f"  RSI:      {latest.get('RSI', 'N/A'):.2f}" if pd.notna(latest.get('RSI')) else "  RSI:      N/A")
    print(f"  MACD:     {latest.get('MACD', 'N/A'):.4f}" if pd.notna(latest.get('MACD')) else "  MACD:     N/A")
    print(f"  布林带位置: {latest.get('BB_Position', 'N/A'):.1f}%" if pd.notna(latest.get('BB_Position')) else "  布林带位置: N/A")

    # 统计数据
    print(f"\n📈 近半年统计:")
    price_change = latest['close'] - df_180days.iloc[0]['close']
    price_change_pct = (price_change / df_180days.iloc[0]['close']) * 100
    max_price = df_180days['high'].max()
    min_price = df_180days['low'].min()
    max_single_day_gain = df_180days['change_pct'].max()
    max_single_day_loss = df_180days['change_pct'].min()
    positive_days = len(df_180days[df_180days['change_pct'] > 0])
    negative_days = len(df_180days[df_180days['change_pct'] < 0])

    print(f"  价格变化: {price_change:+.2f}元 ({price_change_pct:+.2f}%)")
    print(f"  价格区间: {min_price:.2f} - {max_price:.2f}元 (振幅: {((max_price/min_price-1)*100):+.2f}%)")
    print(f"  单日最大涨幅: {max_single_day_gain:+.2f}%")
    print(f"  单日最大跌幅: {max_single_day_loss:+.2f}%")
    print(f"  上涨天数: {positive_days}天 ({positive_days/len(df_180days)*100:.1f}%)")
    print(f"  下跌天数: {negative_days}天 ({negative_days/len(df_180days)*100:.1f}%)")
    print(f"  平盘天数: {len(df_180days)-positive_days-negative_days}天")

    # 波动性分析
    print(f"\n📊 波动性分析:")
    volatility = df_180days['change_pct'].std()
    mean_change = df_180days['change_pct'].mean()
    annualized_volatility = volatility * np.sqrt(252)

    print(f"  日均涨跌幅: {mean_change:+.2f}%")
    print(f"  涨跌幅标准差: {volatility:.2f}%")
    print(f"  年化波动率: {annualized_volatility:.2f}%")

    # 季度表现
    print(f"\n📊 季度表现分析:")
    quarters = []
    for i in range(0, len(df_180days), 60):  # 大约每季度60天
        quarter_data = df_180days.iloc[i:i+60]
        if len(quarter_data) > 30:  # 至少要有30天数据
            quarter_start = quarter_data.iloc[0]['close']
            quarter_end = quarter_data.iloc[-1]['close']
            quarter_change = (quarter_end - quarter_start) / quarter_start * 100
            quarter_num = i // 60 + 1
            quarters.append(f"  Q{quarter_num}: {quarter_change:+.2f}%")

    print("  " + "\n  ".join(quarters))

    # 计算风险指标
    print(f"\n📊 风险指标:")
    risk_metrics = indicators.calculate_risk_metrics(df_180days)
    if risk_metrics:
        print(f"  年化收益率: {risk_metrics.get('annual_return', 0):.2%}")
        print(f"  夏普比率: {risk_metrics.get('sharpe_ratio', 0):.2f}")
        print(f"  最大回撤: {risk_metrics.get('max_drawdown', 0):.2%}")
        print(f"  Calmar比率: {risk_metrics.get('calmar_ratio', 0):.2f}")

    # 生成详细分析结果
    analysis_result = {
        "stock_info": {
            "code": code,
            "name": name,
            "analysis_date": datetime.now().isoformat(),
            "period": "近半年"
        },
        "summary": {
            "start_date": df_180days['date'].min().strftime('%Y-%m-%d'),
            "end_date": df_180days['date'].max().strftime('%Y-%m-%d'),
            "trading_days": len(df_180days),
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "avg_volume": round(avg_volume, 2),
            "volume_std": round(volume_std, 2),
            "total_amount": round(total_amount, 2),
            "max_single_day_gain": round(max_single_day_gain, 2),
            "max_single_day_loss": round(max_single_day_loss, 2),
            "positive_days": positive_days,
            "negative_days": negative_days,
            "volatility": round(volatility, 2),
            "annualized_volatility": round(annualized_volatility, 2),
            "quarterly_performance": quarters
        },
        "monthly_stats": {},
        "daily_data": []
    }

    # 添加月度统计
    for month, stats in monthly_stats.iterrows():
        month_change = (stats['close'] - stats['open']) / stats['open'] * 100
        analysis_result["monthly_stats"][str(month)] = {
            "open": round(stats['open'], 2),
            "close": round(stats['close'], 2),
            "high": round(stats['high'], 2),
            "low": round(stats['low'], 2),
            "change_pct": round(month_change, 2),
            "volume": round(stats['volume'], 2)
        }

    # 添加每周数据（减少数据量）
    weekly_data = df_180days.groupby(pd.Grouper(key='date', freq='W')).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'change_pct': lambda x: (x.iloc[-1] if len(x) > 1 else 0)
    }).dropna()

    # 添加每日详细数据（采样，每5天一条）
    for i in range(0, len(df_180days), 5):
        row = df_180days.iloc[i]
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
                "ma60": round(row.get('MA60', 0), 2),
                "rsi": round(row.get('RSI', 0), 2) if pd.notna(row.get('RSI')) else None,
                "macd": round(row.get('MACD', 0), 4) if pd.notna(row.get('MACD')) else None,
                "bb_position": round(row.get('BB_Position', 0), 1) if pd.notna(row.get('BB_Position')) else None,
                "volume_ratio": round(row.get('Volume_Ratio', 1), 2) if pd.notna(row.get('Volume_Ratio')) else None
            }
        }
        analysis_result["daily_data"].append(daily_info)

    # 保存结果
    output_file = f"static/stock_180days_{code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("static", exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 详细数据已保存至: {output_file}")
    print(f"📊 采样数据: {len(analysis_result['daily_data'])}条 (每5天采样)")

    # 返回数据供可视化使用
    return analysis_result, df_180days

if __name__ == "__main__":
    # 分析比亚迪近半年数据
    result, df_180days = analyze_180days_stock_data("002594", "比亚迪")

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print(f"📊 数据覆盖: {result['summary']['trading_days']} 个交易日")
    print(f"📈 总体表现: {result['summary']['price_change_pct']:+.2f}%")
    print(f"📊 年化波动率: {result['summary']['annualized_volatility']:.2f}%")
    print(f"📊 夏普比率: {result.get('risk_metrics', {}).get('sharpe_ratio', 0):.2f}")
    print("=" * 60)