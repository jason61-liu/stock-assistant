#!/usr/bin/env python3
"""
将JSON交易数据生成为可视化HTML图表
"""
import json
import os
from datetime import datetime

def create_visualization_html(json_file_path, output_html_path=None):
    """
    将JSON股票数据生成可视化HTML图表
    """

    # 读取JSON数据
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取数据
    stock_info = data['stock_info']
    summary = data['summary']
    daily_data = data['daily_data']

    # 准备图表数据
    dates = [item['date'][5:] for item in daily_data]  # 只取月-日
    prices = [item['price']['close'] for item in daily_data]
    volumes = [item['volume']['volume'] for item in daily_data]
    changes = [item['price']['change'] for item in daily_data]
    ma5 = [item['indicators']['ma5'] for item in daily_data]
    ma20 = [item['indicators']['ma20'] for item in daily_data]
    rsi = [item['indicators']['rsi'] for item in daily_data if item['indicators']['rsi'] is not None]

    # 生成HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_info['name']}({stock_info['code']}) - {stock_info['period']}交易分析</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
            transition: transform 0.3s ease;
        }}

        .summary-card:hover {{
            transform: translateY(-5px);
        }}

        .summary-card h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .summary-card .change {{
            font-size: 1.2em;
        }}

        .positive {{
            color: #27ae60;
        }}

        .negative {{
            color: #e74c3c;
        }}

        .charts-container {{
            padding: 30px;
        }}

        .chart-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}

        .chart-section h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}

        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .data-table th,
        .data-table td {{
            padding: 12px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}

        .data-table th {{
            background: #3498db;
            color: white;
            font-weight: 600;
        }}

        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .data-table tr:hover {{
            background: #e3f2fd;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .chart-wrapper {{
                height: 300px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部信息 -->
        <div class="header">
            <h1>{stock_info['name']} ({stock_info['code']})</h1>
            <p>{stock_info['period']} 交易分析报告</p>
            <p>分析时间: {stock_info['analysis_date'][:19].replace('T', ' ')}</p>
        </div>

        <!-- 摘要卡片 -->
        <div class="summary">
            <div class="summary-card">
                <h3>💰 价格变化</h3>
                <div class="value {'positive' if summary['price_change'] > 0 else 'negative'}">
                    {summary['price_change']:+.2f}元
                </div>
                <div class="change {'positive' if summary['price_change_pct'] > 0 else 'negative'}">
                    ({summary['price_change_pct']:+.2f}%)
                </div>
            </div>

            <div class="summary-card">
                <h3>📊 交易天数</h3>
                <div class="value">{summary['trading_days']}</div>
                <div>个交易日</div>
            </div>

            <div class="summary-card">
                <h3>📈 价格区间</h3>
                <div class="value">{summary['min_price']:.2f} - {summary['max_price']:.2f}</div>
                <div>元</div>
            </div>

            <div class="summary-card">
                <h3>💵 总成交额</h3>
                <div class="value">{summary['total_amount']:.2f}</div>
                <div>亿元</div>
            </div>
        </div>

        <!-- 图表区域 -->
        <div class="charts-container">
            <!-- 价格走势图 -->
            <div class="chart-section">
                <h2>📈 价格走势与技术指标</h2>
                <div class="chart-wrapper">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>

            <!-- 成交量图 -->
            <div class="chart-section">
                <h2>💰 成交量分析</h2>
                <div class="chart-wrapper">
                    <canvas id="volumeChart"></canvas>
                </div>
            </div>

            <!-- 涨跌幅图 -->
            <div class="chart-section">
                <h2>📊 每日涨跌幅</h2>
                <div class="chart-wrapper">
                    <canvas id="changeChart"></canvas>
                </div>
            </div>

            <!-- RSI指标图 -->
            <div class="chart-section">
                <h2>📈 RSI技术指标</h2>
                <div class="chart-wrapper">
                    <canvas id="rsiChart"></canvas>
                </div>
            </div>

            <!-- 详细数据表格 -->
            <div class="chart-section">
                <h2>📋 详细交易数据</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>开盘价</th>
                            <th>最高价</th>
                            <th>最低价</th>
                            <th>收盘价</th>
                            <th>涨跌幅</th>
                            <th>成交量(万)</th>
                            <th>成交额(亿)</th>
                            <th>MA5</th>
                            <th>MA20</th>
                            <th>RSI</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    # 添加数据表格行
    for item in daily_data:
        change_class = 'positive' if item['price']['change'] > 0 else 'negative'
        rsi_value = item['indicators']['rsi'] if item['indicators']['rsi'] is not None else 'N/A'

        html_content += f"""
                        <tr>
                            <td>{item['date']}</td>
                            <td>{item['price']['open']:.2f}</td>
                            <td>{item['price']['high']:.2f}</td>
                            <td>{item['price']['low']:.2f}</td>
                            <td>{item['price']['close']:.2f}</td>
                            <td class="{change_class}">{item['price']['change']:+.2f}%</td>
                            <td>{item['volume']['volume']:.2f}</td>
                            <td>{item['volume']['amount']:.2f}</td>
                            <td>{item['indicators']['ma5']:.2f}</td>
                            <td>{item['indicators']['ma20']:.2f}</td>
                            <td>{rsi_value if rsi_value != 'N/A' else 'N/A'}</td>
                        </tr>
"""

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 页脚 -->
        <div class="footer">
            <p>📊 A股行情可视化服务 | 数据生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>⚠️ 本数据为演示数据，仅供参考，不构成投资建议</p>
        </div>
    </div>

    <script>
        // 图表配置
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";

        // 价格走势图
        const priceCtx = document.getElementById('priceChart').getContext('2d');
        new Chart(priceCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [
                    {{
                        label: '收盘价',
                        data: {json.dumps(prices)},
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.1
                    }},
                    {{
                        label: 'MA5',
                        data: {json.dumps(ma5)},
                        borderColor: '#e74c3c',
                        borderWidth: 2,
                        fill: false
                    }},
                    {{
                        label: 'MA20',
                        data: {json.dumps(ma20)},
                        borderColor: '#f39c12',
                        borderWidth: 2,
                        fill: false
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '价格走势与移动平均线',
                        font: {{
                            size: 16
                        }}
                    }},
                    legend: {{
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: '价格 (元)'
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
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: '成交量',
                    data: {json.dumps(volumes)},
                    backgroundColor: 'rgba(46, 204, 113, 0.8)',
                    borderColor: '#27ae60',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '每日成交量',
                        font: {{
                            size: 16
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '成交量 (万股)'
                        }}
                    }}
                }}
            }}
        }});

        // 涨跌幅图
        const changeCtx = document.getElementById('changeChart').getContext('2d');
        const changeColors = {json.dumps(['#27ae60' if x > 0 else '#e74c3c' for x in changes])};
        new Chart(changeCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{
                    label: '涨跌幅',
                    data: {json.dumps(changes)},
                    backgroundColor: changeColors,
                    borderColor: changeColors,
                    borderWidth: 1
                }]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '每日涨跌幅',
                        font: {{
                            size: 16
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{
                            display: true,
                            text: '涨跌幅 (%)'
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
                labels: {json.dumps(dates)},
                datasets: [{
                    label: 'RSI',
                    data: {json.dumps(rsi)},
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.1
                }]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'RSI相对强弱指标',
                        font: {{
                            size: 16
                        }}
                    }},
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: 70,
                                yMax: 70,
                                borderColor: '#e74c3c',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {{
                                    content: '超卖线 (70)',
                                    enabled: true
                                }}
                            }},
                            line2: {{
                                type: 'line',
                                yMin: 30,
                                yMax: 30,
                                borderColor: '#27ae60',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {{
                                    content: '超买线 (30)',
                                    enabled: true
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        min: 0,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'RSI值'
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
    json_files = [f for f in os.listdir(json_dir) if f.startswith('stock_7days_') and f.endswith('.json')]

    if json_files:
        latest_json = max(json_files)
        json_path = os.path.join(json_dir, latest_json)

        print(f"🔄 正在生成可视化图表...")
        print(f"📄 输入文件: {json_path}")

        html_path = create_visualization_html(json_path)

        print(f"✅ 可视化文件已生成: {html_path}")
        print(f"🌐 请在浏览器中打开查看: file://{os.path.abspath(html_path)}")
    else:
        print("❌ 未找到JSON数据文件，请先运行 demo_7days.py 生成数据")