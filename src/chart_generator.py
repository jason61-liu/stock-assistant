"""
图表生成器 - 将JSON数据转换为可视化HTML
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional
import logging

from .config import Config

logger = logging.getLogger(__name__)

class ChartGenerator:
    """图表生成器"""

    def __init__(self):
        self.output_dir = Config.REPORT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_charts_html(self, analysis_result: Dict, output_file: str) -> bool:
        """
        生成完整的HTML图表文件

        Args:
            analysis_result: 分析结果数据
            output_file: 输出文件路径

        Returns:
            bool: 生成是否成功
        """
        try:
            if 'stocks' not in analysis_result:
                logger.error("分析结果中没有股票数据")
                return False

            stocks = analysis_result['stocks']
            successful_stocks = {code: data for code, data in stocks.items() if not data.get('error')}

            if not successful_stocks:
                logger.error("没有成功分析的股票数据")
                return False

            # 如果只有一个股票，使用详细图表
            if len(successful_stocks) == 1:
                code, data = list(successful_stocks.items())[0]
                return self._generate_single_stock_charts(data, output_file, analysis_result)
            else:
                # 多股票对比图表
                return self._generate_comparison_charts(successful_stocks, output_file, analysis_result)

        except Exception as e:
            logger.error(f"生成图表失败: {e}")
            return False

    def _generate_single_stock_charts(self, stock_data: Dict, output_file: str, analysis_result: Dict) -> bool:
        """生成单个股票的详细图表"""
        try:
            # 检查是否有时间窗口数据
            time_windows = stock_data.get('time_windows', {})
            if not time_windows:
                # 如果没有时间窗口数据，生成基本信息页面
                return self._generate_basic_info_page(stock_data, output_file, analysis_result)

            # 使用T-7时间窗口数据（如果可用）
            window_key = 'T-7'
            if window_key not in time_windows:
                window_key = list(time_windows.keys())[0] if time_windows else None

            if not window_key:
                return self._generate_basic_info_page(stock_data, output_file, analysis_result)

            # 从缓存获取原始数据或使用模拟数据
            return self._generate_charts_with_data(stock_data, output_file, analysis_result, window_key)

        except Exception as e:
            logger.error(f"生成单个股票图表失败: {e}")
            return False

    def _generate_basic_info_page(self, stock_data: Dict, output_file: str, analysis_result: Dict) -> bool:
        """生成基本信息页面（当没有详细时间窗口数据时）"""
        try:
            code = stock_data['code']
            name = stock_data['name']

            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}({code}) - 股票分析报告</title>
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
            max-width: 1000px;
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
        }}

        .content {{
            padding: 30px;
        }}

        .info-card {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }}

        .error {{
            background: #fff5f5;
            border-left-color: #e74c3c;
            color: #e74c3c;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{name} ({code})</h1>
            <p>股票分析报告</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="content">
"""

            if stock_data.get('error'):
                html_content += f"""
            <div class="info-card error">
                <h3>⚠️ 数据获取异常</h3>
                <p>{stock_data['error']}</p>
                <p>这可能是由于网络连接问题或数据源限制导致的。</p>
            </div>
"""

            # 估值信息
            if stock_data.get('valuation'):
                valuation = stock_data['valuation']
                html_content += f"""
            <div class="info-card">
                <h3>💰 估值指标</h3>
                <p>PE: {valuation.get('pe', 'N/A')}</p>
                <p>PB: {valuation.get('pb', 'N/A')}</p>
                <p>PS: {valuation.get('ps', 'N/A')}</p>
            </div>
"""

            # 风险指标
            if stock_data.get('risk_metrics'):
                risk = stock_data['risk_metrics']
                html_content += f"""
            <div class="info-card">
                <h3>📊 风险指标</h3>
                <p>年化收益率: {risk.get('annual_return', 0):.2%}</p>
                <p>波动率: {risk.get('volatility', 0):.2%}</p>
                <p>夏普比率: {risk.get('sharpe_ratio', 0):.2f}</p>
                <p>最大回撤: {risk.get('max_drawdown', 0):.2%}</p>
            </div>
"""

            # 说明信息
            html_content += f"""
            <div class="info-card">
                <h3>📖 说明</h3>
                <p>由于网络连接问题，暂时无法获取详细的交易数据。</p>
                <p>请稍后重试，或检查网络连接。</p>
                <p>您可以通过API接口 <code>/api/v1/stocks/{code}</code> 获取最新数据。</p>
            </div>
"""

            html_content += f"""
        </div>

        <div class="footer">
            <p>📊 A股行情可视化服务</p>
            <p>⚠️ 数据获取可能存在延迟，仅供参考</p>
        </div>
    </div>
</body>
</html>
"""

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"基本信息页面已生成: {output_file}")
            return True

        except Exception as e:
            logger.error(f"生成基本信息页面失败: {e}")
            return False

    def _generate_charts_with_data(self, stock_data: Dict, output_file: str, analysis_result: Dict, window_key: str) -> bool:
        """使用数据生成图表"""
        try:
            # 这里应该从缓存获取实际的数据，现在先用模拟数据演示
            # 在实际应用中，可以从analysis_result中提取更多信息

            # 检查是否有现有的详细数据文件
            code = stock_data['code']
            name = stock_data['name']

            # 查找对应的数据文件
            json_files = [f for f in os.listdir(self.output_dir)
                         if f.startswith(f'stock_7days_{code}_') and f.endswith('.json')]

            if json_files:
                # 使用现有的数据文件生成图表
                from ..create_simple_chart import create_simple_visualization
                json_path = os.path.join(self.output_dir, max(json_files))
                create_simple_visualization(json_path, output_file)
                return True
            else:
                # 生成模拟数据的图表
                return self._generate_mock_charts(stock_data, output_file, window_key)

        except Exception as e:
            logger.error(f"生成数据图表失败: {e}")
            return False

    def _generate_mock_charts(self, stock_data: Dict, output_file: str, window_key: str) -> bool:
        """生成模拟数据图表"""
        try:
            code = stock_data['code']
            name = stock_data['name']

            # 生成模拟数据
            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta

            # 生成最近7天的模拟数据
            days = 7
            dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]

            np.random.seed(int(code[-6:]) if code.isdigit() else 42)  # 使用股票代码作为随机种子

            base_price = 100.0
            prices = []
            volumes = []

            for i in range(days):
                price_change = np.random.normal(0, 0.02)
                if i == 0:
                    price = base_price
                else:
                    price = prices[-1] * (1 + price_change)
                prices.append(price)
                volumes.append(np.random.uniform(100, 500))

            # 简单的HTML图表页面
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}({code}) - 模拟数据图表</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .chart-container {{ margin: 20px 0; }}
        .chart {{ height: 400px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background: #f0f0f0; }}
        .notice {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{name} ({code}) - {window_key} 模拟数据</h1>
            <p>⚠️ 此为演示数据，非真实交易数据</p>
        </div>

        <div class="notice">
            <strong>说明:</strong> 由于网络连接问题，当前显示为模拟数据。实际数据需要通过网络API获取。
        </div>

        <div class="chart-container">
            <div class="chart">
                <canvas id="priceChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart">
                <canvas id="volumeChart"></canvas>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>收盘价</th>
                    <th>成交量</th>
                </tr>
            </thead>
            <tbody>
"""

            # 添加表格数据
            for i, (date, price, volume) in enumerate(zip(dates, prices, volumes)):
                html_content += f"""
                <tr>
                    <td>{date.strftime('%Y-%m-%d')}</td>
                    <td>{price:.2f}</td>
                    <td>{volume:.0f}</td>
                </tr>
"""

            html_content += f"""
            </tbody>
        </table>
    </div>

    <script>
        // 价格图表
        const priceCtx = document.getElementById('priceChart').getContext('2d');
        new Chart(priceCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps([d.strftime('%m-%d') for d in dates])},
                datasets: [{{
                    label: '收盘价',
                    data: {json.dumps([round(p, 2) for p in prices])},
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{ display: true, text: '价格走势' }}
                }}
            }}
        }});

        // 成交量图表
        const volumeCtx = document.getElementById('volumeChart').getContext('2d');
        new Chart(volumeCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([d.strftime('%m-%d') for d in dates])},
                datasets: [{{
                    label: '成交量',
                    data: {json.dumps([round(v, 0) for v in volumes])},
                    backgroundColor: 'rgba(46, 204, 113, 0.8)'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{ display: true, text: '成交量' }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"模拟数据图表已生成: {output_file}")
            return True

        except Exception as e:
            logger.error(f"生成模拟图表失败: {e}")
            return False

    def _generate_comparison_charts(self, stocks: Dict, output_file: str, analysis_result: Dict) -> bool:
        """生成多股票对比图表"""
        try:
            # 简化版本，只显示基本信息对比
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多股票对比分析</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .stock-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .stock-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; }}
        .stock-card h3 {{ color: #2c3e50; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>多股票对比分析</h1>
            <p>共 {len(stocks)} 只股票</p>
        </div>

        <div class="stock-grid">
"""

            for code, data in stocks.items():
                html_content += f"""
            <div class="stock-card">
                <h3>{data['name']} ({code})</h3>
                <p>状态: {'✅ 成功' if not data.get('error') else '❌ 失败'}</p>
                {f'<p>错误: {data["error"]}</p>' if data.get('error') else ''}
            </div>
"""

            html_content += f"""
        </div>
    </div>
</body>
</html>
"""

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"对比图表已生成: {output_file}")
            return True

        except Exception as e:
            logger.error(f"生成对比图表失败: {e}")
            return False