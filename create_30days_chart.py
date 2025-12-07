#!/usr/bin/env python3
"""
将1个月JSON交易数据生成为可视化HTML图表
"""
import json
import os
from datetime import datetime
import numpy as np

def create_30days_visualization(json_file_path, output_html_path=None):
    """
    将1个月股票数据生成可视化HTML图表
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
    amplitudes = [item['price']['amplitude'] for item in daily_data]
    ma5 = [item['indicators']['ma5'] for item in daily_data]
    ma10 = [item['indicators']['ma10'] for item in daily_data]
    ma20 = [item['indicators']['ma20'] for item in daily_data]
    rsi = [item['indicators']['rsi'] for item in daily_data if item['indicators']['rsi'] is not None]
    bb_position = [item['indicators']['bb_position'] for item in daily_data if item['indicators']['bb_position'] is not None]

    # 将数据转换为JavaScript数组
    dates_js = json.dumps(dates)
    prices_js = json.dumps(prices)
    volumes_js = json.dumps(volumes)
    changes_js = json.dumps(changes)
    amplitudes_js = json.dumps(amplitudes)
    ma5_js = json.dumps(ma5)
    ma10_js = json.dumps(ma10)
    ma20_js = json.dumps(ma20)
    rsi_js = json.dumps(rsi)
    bb_position_js = json.dumps(bb_position)

    # 涨跌幅颜色数组
    change_colors = json.dumps(['#27ae60' if x > 0 else '#e74c3c' for x in changes])

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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1600px;
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
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
            font-size: 1.0em;
        }}

        .summary-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .summary-card .sub-value {{
            font-size: 1.0em;
            color: #666;
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

        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .chart-full {{
            grid-column: 1 / -1;
        }}

        .chart-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
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
            height: 350px;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.85em;
        }}

        .data-table th,
        .data-table td {{
            padding: 8px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}

        .data-table th {{
            background: #3498db;
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
            max-height: 400px;
            overflow-y: auto;
            margin-top: 20px;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}

        .analysis-insights {{
            background: #e8f4fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 20px 30px;
            border-radius: 8px;
        }}

        .analysis-insights h3 {{
            color: #1976d2;
            margin-bottom: 15px;
        }}

        .insight-item {{
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid #e1f5fe;
        }}

        .insight-item:last-child {{
            border-bottom: none;
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
                font-size: 2em;
            }}

            .chart-wrapper {{
                height: 300px;
            }}

            .data-table {{
                font-size: 0.75em;
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
                <div class="value">{summary['total_amount']:.0f}</div>
                <div class="sub-value">亿元</div>
            </div>

            <div class="summary-card">
                <h3>📊 年化波动率</h3>
                <div class="value">{summary['annualized_volatility']:.2f}%</div>
                <div class="sub-value">{'较高' if summary['annualized_volatility'] > 20 else '中等' if summary['annualized_volatility'] > 15 else '较低'}</div>
            </div>

            <div class="summary-card">
                <h3>📈 胜率</h3>
                <div class="value">{summary['positive_days']}/{summary['trading_days']}</div>
                <div class="sub-value">({summary['positive_days']/summary['trading_days']*100:.1f}%)</div>
            </div>
        </div>

        <!-- 分析洞察 -->
        <div class="analysis-insights">
            <h3>🔍 投资分析洞察</h3>
            <div class="insight-item">
                <strong>趋势表现:</strong>
                {('呈现上升趋势' if summary['price_change_pct'] > 2 else '横盘整理' if abs(summary['price_change_pct']) <= 2 else '呈现下跌趋势')}，
                月度收益率为 {summary['price_change_pct']:+.2f}%
            </div>
            <div class="insight-item">
                <strong>波动特征:</strong>
                年化波动率为 {summary['annualized_volatility']:.2f}%，
                属于{('高波动' if summary['annualized_volatility'] > 20 else '中等波动' if summary['annualized_volatility'] > 15 else '低波动')}股票
            </div>
            <div class="insight-item">
                <strong>风险收益:</strong>
                上涨天数 {summary['positive_days']} 天，下跌天数 {summary['negative_days']} 天，
                {'多头占优' if summary['positive_days'] > summary['negative_days'] else '空头占优' if summary['positive_days'] < summary['negative_days'] else '多空均衡'}
            </div>
            <div class="insight-item">
                <strong>极值分析:</strong>
                单日最大涨幅 {summary['max_single_day_gain']:+.2f}%，
                单日最大跌幅 {summary['max_single_day_loss']:+.2f}%，
                价格振幅 {((summary['max_price']/summary['min_price']-1)*100):+.2f}%
            </div>
        </div>

        <!-- 图表区域 -->
        <div class="charts-container">
            <!-- 价格走势图 -->
            <div class="chart-grid">
                <div class="chart-section chart-full">
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

                <!-- 振幅分析 -->
                <div class="chart-section">
                    <h2>📈 日内振幅</h2>
                    <div class="chart-wrapper">
                        <canvas id="amplitudeChart"></canvas>
                    </div>
                </div>

                <!-- RSI指标图 -->
                <div class="chart-section">
                    <h2>📈 RSI相对强弱指标</h2>
                    <div class="chart-wrapper">
                        <canvas id="rsiChart"></canvas>
                    </div>
                </div>

                <!-- 布林带位置图 -->
                <div class="chart-section">
                    <h2>📊 布林带位置</h2>
                    <div class="chart-wrapper">
                        <canvas id="bbChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- 详细数据表格 -->
            <div class="chart-section">
                <h2>📋 详细交易数据 (30天)</h2>
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
                                <th>振幅</th>
                                <th>成交量(万)</th>
                                <th>MA5</th>
                                <th>MA10</th>
                                <th>MA20</th>
                                <th>RSI</th>
                            </tr>
                        </thead>
                        <tbody>
"""

    # 添加数据表格行
    for i, item in enumerate(daily_data):
        change_class = 'positive' if item['price']['change'] > 0 else 'negative'
        rsi_value = item['indicators']['rsi'] if item['indicators']['rsi'] is not None else 'N/A'

        # 为最近的数据行添加高亮
        row_style = 'background-color: #fff3cd;' if i >= len(daily_data) - 5 else ''

        html_content += f"""
                            <tr style="{row_style}">
                                <td>{item['date']}</td>
                                <td>{item['price']['open']:.2f}</td>
                                <td>{item['price']['high']:.2f}</td>
                                <td>{item['price']['low']:.2f}</td>
                                <td>{item['price']['close']:.2f}</td>
                                <td class="{change_class}">{item['price']['change']:+.2f}%</td>
                                <td>{item['price']['amplitude']:.2f}%</td>
                                <td>{item['volume']['volume']:.2f}</td>
                                <td>{item['indicators']['ma5']:.2f}</td>
                                <td>{item['indicators']['ma10']:.2f}</td>
                                <td>{item['indicators']['ma20']:.2f}</td>
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
        const amplitudes = {amplitudes_js};
        const ma5 = {ma5_js};
        const ma10 = {ma10_js};
        const ma20 = {ma20_js};
        const rsi = {rsi_js};
        const bbPosition = {bb_position_js};

        // 涨跌幅颜色数组
        const changeColors = {change_colors};

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
                        pointRadius: 1,
                        pointHoverRadius: 5
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
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    title: {{
                        display: true,
                        text: '价格走势与移动平均线',
                        font: {{ size: 16 }}
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
                        text: '每日成交量',
                        font: {{ size: 16 }}
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
                        text: '每日涨跌幅',
                        font: {{ size: 16 }}
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

        // 振幅图
        const amplitudeCtx = document.getElementById('amplitudeChart').getContext('2d');
        new Chart(amplitudeCtx, {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: '日内振幅',
                    data: amplitudes,
                    borderColor: '#e67e22',
                    backgroundColor: 'rgba(230, 126, 34, 0.1)',
                    borderWidth: 2,
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
                        text: '日内振幅分析',
                        font: {{ size: 16 }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '振幅 (%)'
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
                    borderColor: '#8e44ad',
                    backgroundColor: 'rgba(142, 68, 173, 0.1)',
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
                        font: {{ size: 16 }}
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
                                    enabled: true,
                                    position: 'end'
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
                                    enabled: true,
                                    position: 'end'
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

        // 布林带位置图
        const bbCtx = document.getElementById('bbChart').getContext('2d');
        new Chart(bbCtx, {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: '布林带位置',
                    data: bbPosition,
                    borderColor: '#16a085',
                    backgroundColor: 'rgba(22, 160, 133, 0.1)',
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
                        text: '布林带位置 (0-100%)',
                        font: {{ size: 16 }}
                    }},
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: 80,
                                yMax: 80,
                                borderColor: '#e74c3c',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {{
                                    content: '上轨 (80)',
                                    enabled: true
                                }}
                            }},
                            line2: {{
                                type: 'line',
                                yMin: 50,
                                yMax: 50,
                                borderColor: '#95a5a6',
                                borderWidth: 1,
                                borderDash: [3, 3],
                                label: {{
                                    content: '中轨 (50)',
                                    enabled: true
                                }}
                            }},
                            line3: {{
                                type: 'line',
                                yMin: 20,
                                yMax: 20,
                                borderColor: '#27ae60',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {{
                                    content: '下轨 (20)',
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
                            text: '布林带位置 %'
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
    json_files = [f for f in os.listdir(json_dir) if f.startswith('stock_30days_') and f.endswith('.json')]

    if json_files:
        latest_json = max(json_files)
        json_path = os.path.join(json_dir, latest_json)

        print(f"🔄 正在生成1个月数据可视化图表...")
        print(f"📄 输入文件: {json_path}")

        html_path = create_30days_visualization(json_path)

        print(f"✅ 可视化文件已生成: {html_path}")
        print(f"🌐 请在浏览器中打开查看: file://{os.path.abspath(html_path)}")

        # 显示文件大小
        file_size = os.path.getsize(html_path)
        print(f"📊 文件大小: {file_size/1024:.1f}KB")

        # 自动打开浏览器
        import subprocess
        try:
            subprocess.run(['open', html_path], check=True)
            print(f"🚀 已在浏览器中打开可视化图表")
        except:
            print(f"⚠️  请手动在浏览器中打开: {html_path}")
    else:
        print("❌ 未找到JSON数据文件，请先运行 demo_30days.py 生成数据")