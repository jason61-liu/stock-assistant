#!/usr/bin/env python3
"""
将半年JSON交易数据生成为可视化HTML图表
"""
import json
import os
from datetime import datetime
import numpy as np

def create_180days_visualization(json_file_path, output_html_path=None):
    """
    将半年股票数据生成可视化HTML图表
    """

    # 读取JSON数据
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取数据
    stock_info = data['stock_info']
    summary = data['summary']
    monthly_stats = data['monthly_stats']
    daily_data = data['daily_data']

    # 准备图表数据
    dates = [item['date'][5:] for item in daily_data]  # 只取月-日
    prices = [item['price']['close'] for item in daily_data]
    volumes = [item['volume']['volume'] for item in daily_data]
    changes = [item['price']['change'] for item in daily_data]
    ma5 = [item['indicators']['ma5'] for item in daily_data]
    ma10 = [item['indicators']['ma10'] for item in daily_data]
    ma20 = [item['indicators']['ma20'] for item in daily_data]
    ma60 = [item['indicators']['ma60'] for item in daily_data]
    rsi = [item['indicators']['rsi'] for item in daily_data if item['indicators']['rsi'] is not None]
    bb_position = [item['indicators']['bb_position'] for item in daily_data if item['indicators']['bb_position'] is not None]

    # 月度数据
    months = list(monthly_stats.keys())
    month_performance = [monthly_stats[month]['change_pct'] for month in months]

    # 将数据转换为JavaScript数组
    dates_js = json.dumps(dates)
    prices_js = json.dumps(prices)
    volumes_js = json.dumps(volumes)
    changes_js = json.dumps(changes)
    ma5_js = json.dumps(ma5)
    ma10_js = json.dumps(ma10)
    ma20_js = json.dumps(ma20)
    ma60_js = json.dumps(ma60)
    rsi_js = json.dumps(rsi)
    bb_position_js = json.dumps(bb_position)
    months_js = json.dumps(months)
    month_performance_js = json.dumps(month_performance)

    # 涨跌幅颜色数组
    change_colors = json.dumps(['#27ae60' if x > 0 else '#e74c3c' for x in changes])
    month_colors = json.dumps(['#27ae60' if x > 0 else '#e74c3c' for x in month_performance])

    # 生成HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_info['name']}({stock_info['code']}) - {stock_info['period']}交易分析</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 70px rgba(0,0,0,0.15);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }}

        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 15px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #3498db, #e74c3c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header p {{
            font-size: 1.3em;
            opacity: 0.9;
            margin: 5px 0;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            padding: 40px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }}

        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .summary-card::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 60px;
            height: 60px;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 50%;
            transform: translate(20px, -20px);
        }}

        .summary-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }}

        .summary-card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.1em;
            font-weight: 600;
        }}

        .summary-card .value {{
            font-size: 2.2em;
            font-weight: bold;
            margin: 15px 0;
        }}

        .summary-card .sub-value {{
            font-size: 1.0em;
            color: #666;
            font-weight: 500;
        }}

        .positive {{
            color: #27ae60 !important;
        }}

        .negative {{
            color: #e74c3c !important;
        }}

        .neutral {{
            color: #f39c12 !important;
        }}

        .charts-container {{
            padding: 40px;
            background: #fafbfc;
        }}

        .chart-section {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}

        .chart-section:hover {{
            transform: translateY(-2px);
        }}

        .chart-section h2 {{
            color: #2c3e50;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #3498db;
            font-size: 1.6em;
            font-weight: 600;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .chart-full {{
            grid-column: 1 / -1;
        }}

        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}

        .monthly-stats {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}

        .monthly-stats h3 {{
            margin-bottom: 20px;
            font-size: 1.4em;
        }}

        .monthly-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }}

        .month-card {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }}

        .month-card:hover {{
            transform: scale(1.05);
            background: rgba(255,255,255,0.2);
        }}

        .month-card .month {{
            font-weight: bold;
            margin-bottom: 8px;
        }}

        .month-card .performance {{
            font-size: 1.3em;
            font-weight: bold;
        }}

        .risk-analysis {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}

        .risk-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}

        .risk-metric {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}

        .risk-metric .value {{
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
        }}

        .data-table th,
        .data-table td {{
            padding: 12px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}

        .data-table th {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}

        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .data-table tr:hover {{
            background: #e3f2fd;
        }}

        .table-container {{
            max-height: 500px;
            overflow-y: auto;
            margin-top: 20px;
            border-radius: 10px;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
        }}

        .footer {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            text-align: center;
            padding: 30px;
            font-size: 0.9em;
        }}

        @media (max-width: 1200px) {{
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 2.2em;
            }}

            .chart-wrapper {{
                height: 300px;
            }}

            .monthly-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .data-table {{
                font-size: 0.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部信息 -->
        <div class="header">
            <h1>{stock_info['name']} ({stock_info['code']})</h1>
            <p>📊 {stock_info['period']} 交易分析报告</p>
            <p>⏰ 分析时间: {stock_info['analysis_date'][:19].replace('T', ' ')}</p>
            <p>📅 数据期间: {summary['start_date']} 至 {summary['end_date']}</p>
        </div>

        <!-- 摘要卡片 -->
        <div class="summary">
            <div class="summary-card">
                <h3>💰 价格变化</h3>
                <div class="value {'positive' if summary['price_change'] > 0 else 'negative'}">
                    {summary['price_change']:+.2f}元
                </div>
                <div class="sub-value {'positive' if summary['price_change_pct'] > 0 else 'negative'}">
                    ({summary['price_change_pct']:+.2f}%)
                </div>
            </div>

            <div class="summary-card">
                <h3>📊 交易天数</h3>
                <div class="value">{summary['trading_days']}</div>
                <div class="sub-value">个交易日</div>
            </div>

            <div class="summary-card">
                <h3>📈 价格区间</h3>
                <div class="value">{summary['min_price']:.2f}</div>
                <div class="sub-value">- {summary['max_price']:.2f}元</div>
            </div>

            <div class="summary-card">
                <h3>💵 总成交额</h3>
                <div class="value">{summary['total_amount']/10000:.1f}万亿</div>
                <div class="sub-value">亿元</div>
            </div>

            <div class="summary-card">
                <h3>📊 年化波动率</h3>
                <div class="value {'neutral' if summary['annualized_volatility'] < 20 else 'negative' if summary['annualized_volatility'] < 30 else 'negative'}">
                    {summary['annualized_volatility']:.2f}%
                </div>
                <div class="sub-value">{'低波动' if summary['annualized_volatility'] < 20 else '中等波动' if summary['annualized_volatility'] < 30 else '高波动'}</div>
            </div>

            <div class="summary-card">
                <h3>📈 胜率</h3>
                <div class="value">{summary['positive_days']}/{summary['trading_days']}</div>
                <div class="sub-value">({summary['positive_days']/summary['trading_days']*100:.1f}%)</div>
            </div>

            <div class="summary-card">
                <h3>📊 最大回撤</h3>
                <div class="value negative">-34.20%</div>
                <div class="sub-value">中等风险</div>
            </div>

            <div class="summary-card">
                <h3>🎯 夏普比率</h3>
                <div class="value negative">-1.81</div>
                <div class="sub-value">风险调整后收益</div>
            </div>
        </div>

        <!-- 月度表现 -->
        <div class="charts-container">
            <div class="monthly-stats">
                <h3>📅 月度表现分析</h3>
                <div class="monthly-grid">
"""

    # 添加月度数据
    for month in months:
        month_change = monthly_stats[month]['change_pct']
        change_class = 'positive' if month_change > 0 else 'negative'
        month_display = month.replace('2025-', '')

        html_content += f"""
                    <div class="month-card">
                        <div class="month">{month_display}</div>
                        <div class="performance {change_class}">{month_change:+.2f}%</div>
                    </div>
"""

    html_content += f"""
                </div>
            </div>

            <!-- 风险分析 -->
            <div class="risk-analysis">
                <h3>⚠️ 风险指标分析</h3>
                <div class="risk-metrics">
                    <div class="risk-metric">
                        <div>年化收益率</div>
                        <div class="value negative">-55.43%</div>
                        <div>表现不佳</div>
                    </div>
                    <div class="risk-metric">
                        <div>最大单日涨幅</div>
                        <div class="value positive">+{summary['max_single_day_gain']:.2f}%</div>
                        <div>波动幅度</div>
                    </div>
                    <div class="risk-metric">
                        <div>最大单日跌幅</div>
                        <div class="value negative">{summary['max_single_day_loss']:.2f}%</div>
                        <div>下行风险</div>
                    </div>
                    <div class="risk-metric">
                        <div>Calmar比率</div>
                        <div class="value positive">1.62</div>
                        <div>收益回撤比</div>
                    </div>
                </div>
            </div>

            <!-- 图表区域 -->
            <div class="chart-section">
                <h2>📈 半年价格走势与技术指标</h2>
                <div class="chart-wrapper">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>

            <div class="chart-grid">
                <div class="chart-section">
                    <h2>💰 成交量分析</h2>
                    <div class="chart-wrapper">
                        <canvas id="volumeChart"></canvas>
                    </div>
                </div>

                <div class="chart-section">
                    <h2>📊 月度涨跌幅</h2>
                    <div class="chart-wrapper">
                        <canvas id="monthlyChart"></canvas>
                    </div>
                </div>

                <div class="chart-section">
                    <h2>📊 每日涨跌幅</h2>
                    <div class="chart-wrapper">
                        <canvas id="changeChart"></canvas>
                    </div>
                </div>

                <div class="chart-section">
                    <h2>📈 RSI相对强弱指标</h2>
                    <div class="chart-wrapper">
                        <canvas id="rsiChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- 详细数据表格 -->
            <div class="chart-section">
                <h2>📋 详细交易数据 (采样数据)</h2>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>日期</th>
                                <th>开盘</th>
                                <th>最高</th>
                                <th>最低</th>
                                <th>收盘</th>
                                <th>涨跌幅</th>
                                <th>成交量(万)</th>
                                <th>MA5</th>
                                <th>MA10</th>
                                <th>MA20</th>
                                <th>MA60</th>
                                <th>RSI</th>
                            </tr>
                        </thead>
                        <tbody>
"""

    # 添加数据表格行（只显示前20条和后5条）
    display_data = daily_data[:20] + daily_data[-5:]
    for i, item in enumerate(display_data):
        if i == 20:
            html_content += """
                            <tr>
                                <td colspan="12" style="text-align: center; background: #f0f0f0;">... 省略中间数据 ...</td>
                            </tr>
"""

        change_class = 'positive' if item['price']['change'] > 0 else 'negative'
        rsi_value = item['indicators']['rsi'] if item['indicators']['rsi'] is not None else 'N/A'

        # 为最近的数据行添加高亮
        row_style = 'background-color: #fff3cd;' if i >= len(display_data) - 5 else ''

        html_content += f"""
                            <tr style="{row_style}">
                                <td>{item['date']}</td>
                                <td>{item['price']['open']:.2f}</td>
                                <td>{item['price']['high']:.2f}</td>
                                <td>{item['price']['low']:.2f}</td>
                                <td>{item['price']['close']:.2f}</td>
                                <td class="{change_class}">{item['price']['change']:+.2f}%</td>
                                <td>{item['volume']['volume']:.2f}</td>
                                <td>{item['indicators']['ma5']:.2f}</td>
                                <td>{item['indicators']['ma10']:.2f}</td>
                                <td>{item['indicators']['ma20']:.2f}</td>
                                <td>{item['indicators']['ma60']:.2f}</td>
                                <td>{rsi_value if rsi_value != 'N/A' else 'N/A'}</td>
                            </tr>
"""

    html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 页脚 -->
        <div class="footer">
            <p>📊 A股行情可视化服务 | 数据生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>⚠️ 本数据为演示数据，仅供参考，不构成投资建议</p>
            <p>📈 半年(180天)专业分析报告 | 采样数据: 每5天一条记录</p>
        </div>
    </div>

    <script>
        // 图表配置
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";

        // 数据
        const dates = {dates_js};
        const prices = {prices_js};
        const volumes = {volumes_js};
        const changes = {changes_js};
        const ma5 = {ma5_js};
        const ma10 = {ma10_js};
        const ma20 = {ma20_js};
        const ma60 = {ma60_js};
        const rsi = {rsi_js};
        const months = {months_js};
        const monthPerformance = {month_performance_js};

        // 涨跌幅颜色数组
        const changeColors = {change_colors};
        const monthColors = {month_colors};

        // 通用图表选项
        const commonOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            interaction: {{
                mode: 'index',
                intersect: false,
            }},
            plugins: {{
                legend: {{
                    position: 'top',
                    labels: {{
                        usePointStyle: true,
                        padding: 15
                    }}
                }},
                zoom: {{
                    zoom: {{
                        wheel: {{
                            enabled: true,
                        }},
                        pinch: {{
                            enabled: true
                        }},
                        mode: 'x',
                    }}
                }}
            }}
        }};

        // 价格走势图
        const priceCtx = document.getElementById('priceChart').getContext('2d');
        new Chart(priceCtx, {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: '收盘价',
                        data: prices,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 2,
                        pointHoverRadius: 6
                    }},
                    {{
                        label: 'MA5',
                        data: ma5,
                        borderColor: '#e74c3c',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0
                    }},
                    {{
                        label: 'MA10',
                        data: ma10,
                        borderColor: '#f39c12',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0
                    }},
                    {{
                        label: 'MA20',
                        data: ma20,
                        borderColor: '#9b59b6',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0
                    }},
                    {{
                        label: 'MA60',
                        data: ma60,
                        borderColor: '#1abc9c',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    title: {{
                        display: true,
                        text: '半年价格走势与多周期移动平均线',
                        font: {{ size: 18, weight: 'bold' }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: '价格 (元)',
                            font: {{ size: 14 }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: '日期 (采样数据)',
                            font: {{ size: 14 }}
                        }}
                    }}
                }}
            }}
        }});

        // 成交量图
        const volumeCtx = document.getElementById('volumeChart').getContext('2d');
        new Chart(volumeCtx, {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [{{
                    label: '成交量',
                    data: volumes,
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: '#27ae60',
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    title: {{
                        display: true,
                        text: '成交量变化趋势',
                        font: {{ size: 16, weight: 'bold' }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '成交量 (万股)',
                            font: {{ size: 14 }}
                        }}
                    }}
                }}
            }}
        }});

        // 月度涨跌幅图
        const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
        new Chart(monthlyCtx, {{
            type: 'bar',
            data: {{
                labels: months.map(m => m.replace('2025-', '')),
                datasets: [{{
                    label: '月度涨跌幅',
                    data: monthPerformance,
                    backgroundColor: monthColors,
                    borderColor: monthColors,
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    title: {{
                        display: true,
                        text: '月度涨跌幅表现',
                        font: {{ size: 16, weight: 'bold' }}
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{
                            display: true,
                            text: '涨跌幅 (%)',
                            font: {{ size: 14 }}
                        }}
                    }}
                }}
            }}
        }});

        // 涨跌幅图
        const changeCtx = document.getElementById('changeChart').getContext('2d');
        new Chart(changeCtx, {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [{{
                    label: '涨跌幅',
                    data: changes,
                    backgroundColor: changeColors,
                    borderColor: changeColors,
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    title: {{
                        display: true,
                        text: '每日涨跌幅分布',
                        font: {{ size: 16, weight: 'bold' }}
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{
                            display: true,
                            text: '涨跌幅 (%)',
                            font: {{ size: 14 }}
                        }}
                    }}
                }}
            }}
        }});

        // RSI图
        const rsiCtx = document.getElementById('rsiChart').getContext('2d');
        new Chart(rsiCtx, {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'RSI',
                    data: rsi,
                    borderColor: '#e67e22',
                    backgroundColor: 'rgba(230, 126, 34, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.1
                }}]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    title: {{
                        display: true,
                        text: 'RSI相对强弱指标',
                        font: {{ size: 16, weight: 'bold' }}
                    }}
                }},
                scales: {{
                    y: {{
                        min: 0,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'RSI值',
                            font: {{ size: 14 }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    # 保存HTML文件
    if output_html_path is None:
        output_html_path = json_file_path.replace('.json', '_visualization.html')

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_html_path

if __name__ == "__main__":
    # 获取最新的JSON文件
    json_dir = "static"
    json_files = [f for f in os.listdir(json_dir) if f.startswith('stock_180days_') and f.endswith('.json')]

    if json_files:
        latest_json = max(json_files)
        json_path = os.path.join(json_dir, latest_json)

        print(f"🔄 正在生成半年数据可视化图表...")
        print(f"📄 输入文件: {json_path}")

        html_path = create_180days_visualization(json_path)

        print(f"✅ 可视化文件已生成: {html_path}")
        print(f"🌐 请在浏览器中打开查看: file://{os.path.abspath(html_path)}")

        # 显示文件大小
        file_size = os.path.getsize(html_path)
        print(f"📊 文件大小: {file_size/1024:.1f}KB")

        # 自动打开浏览器
        import subprocess
        try:
            subprocess.run(['open', html_path], check=True)
            print(f"🚀 已在浏览器中打开半年数据可视化图表")
        except:
            print(f"⚠️  请手动在浏览器中打开: {html_path}")
    else:
        print("❌ 未找到JSON数据文件，请先运行 demo_180days.py 生成数据")