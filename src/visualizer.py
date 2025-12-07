"""
可视化图表生成模块
使用Plotly生成交互式图表
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class StockVisualizer:
    """股票数据可视化器"""

    def _format_number(self, num):
        """格式化数字显示"""
        try:
            num = float(num)
            if num >= 100000000:  # 亿
                return f"{num/100000000:.2f}亿"
            elif num >= 10000:  # 万
                return f"{num/10000:.2f}万"
            else:
                return f"{num:,.0f}"
        except:
            return str(num)

    @staticmethod
    def create_price_chart(df: pd.DataFrame, title: str = "股票价格走势") -> go.Figure:
        """创建价格走势图"""
        if df.empty:
            return go.Figure()

        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=('价格走势', '成交量', 'MACD'),
            x_title='日期'
        )

        # 价格走势（K线图）
        fig.add_trace(
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='K线'
            ),
            row=1, col=1
        )

        # 移动平均线
        if 'MA20' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['MA20'], name='MA20', line=dict(color='orange', width=1)),
                row=1, col=1
            )
        if 'MA60' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['MA60'], name='MA60', line=dict(color='blue', width=1)),
                row=1, col=1
            )

        # 布林带
        if all(col in df.columns for col in ['BB_Upper', 'BB_Lower']):
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['BB_Upper'], name='布林上轨',
                          line=dict(color='gray', width=0.5), fill=None),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['BB_Lower'], name='布林下轨',
                          line=dict(color='gray', width=0.5), fill='tonexty', fillcolor='rgba(128,128,128,0.2)'),
                row=1, col=1
            )

        # 成交量
        if 'volume' in df.columns:
            colors = ['red' if close >= open else 'green'
                     for close, open in zip(df['close'], df['open'])]
            fig.add_trace(
                go.Bar(x=df['date'], y=df['volume'], name='成交量', marker_color=colors),
                row=2, col=1
            )

        # MACD
        if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['MACD'], name='MACD', line=dict(color='blue')),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['MACD_Signal'], name='Signal', line=dict(color='red')),
                row=3, col=1
            )
            fig.add_trace(
                go.Bar(x=df['date'], y=df['MACD_Histogram'], name='Histogram',
                       marker_color=['green' if x >= 0 else 'red' for x in df['MACD_Histogram']]),
                row=3, col=1
            )

        fig.update_layout(
            title=title,
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )

        return fig

    @staticmethod
    def create_indicators_chart(df: pd.DataFrame, title: str = "技术指标") -> go.Figure:
        """创建技术指标图表"""
        if df.empty:
            return go.Figure()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('RSI', '随机振荡器', '成交量比', '价格变化率'),
            horizontal_spacing=0.1,
            vertical_spacing=0.1
        )

        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['RSI'], name='RSI', line=dict(color='blue')),
                row=1, col=1
            )
            # 添加超买超卖线
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)

        # 随机振荡器
        if all(col in df.columns for col in ['Stoch_K', 'Stoch_D']):
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['Stoch_K'], name='Stoch_K', line=dict(color='blue')),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['Stoch_D'], name='Stoch_D', line=dict(color='red')),
                row=1, col=2
            )
            fig.add_hline(y=80, line_dash="dash", line_color="red", row=1, col=2)
            fig.add_hline(y=20, line_dash="dash", line_color="green", row=1, col=2)

        # 成交量比
        if 'Volume_Ratio' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['Volume_Ratio'], name='量比', line=dict(color='purple')),
                row=2, col=1
            )
            fig.add_hline(y=1, line_dash="dash", line_color="gray", row=2, col=1)

        # 价格变化率
        if 'Price_Change_1d' in df.columns:
            colors = ['red' if x >= 0 else 'green' for x in df['Price_Change_1d']]
            fig.add_trace(
                go.Bar(x=df['date'], y=df['Price_Change_1d'], name='涨跌幅', marker_color=colors),
                row=2, col=2
            )

        fig.update_layout(
            title=title,
            height=600,
            showlegend=True
        )

        return fig

    @staticmethod
    def create_comparison_chart(stock_data: Dict[str, Dict], title: str = "股票对比") -> go.Figure:
        """创建多股票对比图表"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('价格对比', 'RSI对比'),
            x_title='日期'
        )

        # 获取T-0时间窗口的数据进行对比
        colors = px.colors.qualitative.Set1

        for i, (code, data) in enumerate(stock_data.items()):
            if data.get('error'):
                continue

            # 使用T-0时间窗口的最新指标
            if 'T-0' in data.get('time_windows', {}):
                indicators = data['time_windows']['T-0']['latest_indicators']

                # 创建简单的对比数据点
                fig.add_trace(
                    go.Scatter(
                        x=[data['name']],
                        y=[indicators.get('price', 0)],
                        name=f"{data['name']}({code})",
                        marker=dict(color=colors[i % len(colors)], size=10)
                    ),
                    row=1, col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=[data['name']],
                        y=[indicators.get('rsi', 50)],
                        name=f"{data['name']} RSI",
                        marker=dict(color=colors[i % len(colors)], size=10),
                        showlegend=False
                    ),
                    row=2, col=1
                )

        fig.update_layout(
            title=title,
            height=500,
            showlegend=True
        )

        return fig

    @staticmethod
    def create_heatmap_data(stock_data: Dict[str, Dict]) -> pd.DataFrame:
        """创建热力图数据"""
        metrics = ['price_change_pct', 'volume_ratio', 'rsi', 'ma_position', 'volatility']
        heatmap_data = []

        for code, data in stock_data.items():
            if data.get('error'):
                continue

            stock_name = data['name']
            row_data = {'stock_name': stock_name, 'stock_code': code}

            # 获取T-0时间窗口的最新指标
            if 'T-0' in data.get('time_windows', {}):
                indicators = data['time_windows']['T-0']['latest_indicators']

                for metric in metrics:
                    if metric in indicators:
                        row_data[metric] = indicators[metric]
                    else:
                        # 计算一些衍生指标
                        if metric == 'ma_position' and 'ma20' in indicators and 'price' in indicators:
                            # 安全处理numpy数组的比较
                            ma20_val = indicators['ma20']
                            if not isinstance(ma20_val, (int, float)) and hasattr(ma20_val, 'size') and ma20_val.size > 1:
                                # 如果是数组，取平均值或第一个元素
                                ma20_val = float(ma20_val.mean() if hasattr(ma20_val, 'mean') else ma20_val[0])
                            else:
                                ma20_val = float(ma20_val)

                            if ma20_val != 0:
                                price_val = indicators['price']
                                if not isinstance(price_val, (int, float)) and hasattr(price_val, 'size') and price_val.size > 1:
                                    price_val = float(price_val.mean() if hasattr(price_val, 'mean') else price_val[0])
                                else:
                                    price_val = float(price_val)
                                row_data[metric] = (price_val - ma20_val) / ma20_val * 100
                            else:
                                row_data[metric] = 0
                        elif metric == 'volatility' and 'volatility_20d' in indicators:
                            row_data[metric] = indicators['volatility_20d']
                        else:
                            row_data[metric] = 0

            heatmap_data.append(row_data)

        return pd.DataFrame(heatmap_data)

    @staticmethod
    def create_heatmap(df: pd.DataFrame, title: str = "股票热力图") -> go.Figure:
        """创建热力图"""
        if df.empty:
            return go.Figure()

        # 选择数值列
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return go.Figure()

        # 准备热力图数据
        heatmap_data = df[numeric_cols].T

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlBu',
            showscale=True,
            hoverongaps=False
        ))

        fig.update_layout(
            title=title,
            xaxis_title='股票',
            yaxis_title='指标',
            height=600
        )

        return fig

    @staticmethod
    def create_risk_return_scatter(stock_data: Dict[str, Dict], title: str = "风险收益散点图") -> go.Figure:
        """创建风险收益散点图"""
        scatter_data = []

        for code, data in stock_data.items():
            if data.get('error'):
                continue

            risk_metrics = data.get('risk_metrics', {})
            if risk_metrics:
                scatter_data.append({
                    'stock': data['name'],
                    'code': code,
                    'return': risk_metrics.get('annual_return', 0),
                    'volatility': risk_metrics.get('volatility', 0),
                    'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0),
                    'max_drawdown': risk_metrics.get('max_drawdown', 0)
                })

        if not scatter_data:
            return go.Figure()

        df = pd.DataFrame(scatter_data)

        fig = go.Figure()

        # 散点图
        fig.add_trace(
            go.Scatter(
                x=df['volatility'],
                y=df['return'],
                mode='markers+text',
                text=df['stock'],
                textposition="top center",
                marker=dict(
                    size=df['sharpe_ratio'] * 20 + 5,  # 夏普比率作为点大小
                    color=df['max_drawdown'],
                    colorscale='RdYlGn_r',  # 红色表示最大回撤大
                    showscale=True,
                    colorbar=dict(title="最大回撤")
                ),
                name='股票'
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title='波动率 (风险)',
            yaxis_title='年化收益率',
            height=600
        )

        return fig

    def generate_charts_html(self, analysis_result: Dict, output_file: str):
        """生成完整的HTML图表文件"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>股票分析报告 - {analysis_result.get('input', '')}</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .chart-container {{ margin: 20px 0; }}
                    .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .error {{ color: red; }}
                    .stock-section {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
                    .back-button {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-size: 16px;
                        font-weight: 600;
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        margin-bottom: 20px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    .back-button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                        color: white;
                    }}
                </style>
            </head>
            <body>
                <a href="/web" class="back-button">
                    <i>←</i> 返回首页
                </a>
                <h1>股票分析报告</h1>
                <div class="summary">
                    <h2>分析摘要</h2>
                    <p><strong>输入:</strong> {analysis_result.get('input', '')}</p>
                    <p><strong>模式:</strong> {analysis_result.get('mode', '')}</p>
                    <p><strong>股票数量:</strong> {analysis_result.get('stock_count', 0)}</p>
                    <p><strong>成功分析:</strong> {analysis_result.get('summary', {}).get('successful_analysis', 0)}</p>
                    <p><strong>分析时间:</strong> {analysis_result.get('timestamp', '')}</p>
                </div>
            """

            # 如果有多个股票，添加对比图表
            stocks = analysis_result.get('stocks', {})
            successful_stocks = {code: data for code, data in stocks.items() if not data.get('error')}

            if len(successful_stocks) > 1:
                comparison_chart = self.create_comparison_chart(successful_stocks)
                html_content += f"""
                <div class="chart-container">
                    <div id="comparison-chart"></div>
                    <script>
                        Plotly.newPlot('comparison-chart', {json.dumps(comparison_chart, cls=plotly.utils.PlotlyJSONEncoder)});
                    </script>
                </div>
                """

            # 为每只股票生成详细图表
            for code, data in successful_stocks.items():
                # 获取数据源信息
                data_source = data.get('data_source', 'unknown')
                data_source_display = {
                    'akshare_primary': 'akShare 主要数据源',
                    'akshare_alternative': 'akShare 备用数据源',
                    'sina': '新浪财经',
                    'tencent': '腾讯财经',
                    'mock': '模拟数据 (演示)',
                    'unknown': '未知数据源'
                }.get(data_source, data_source)

                # 根据数据源设置不同的样式
                source_style = ""
                if data_source == 'mock':
                    source_style = "background-color: #fff3cd; border-left: 4px solid #ffc107;"
                elif data_source in ['akshare_primary', 'akshare_alternative', 'sina', 'tencent']:
                    source_style = "background-color: #d4edda; border-left: 4px solid #28a745;"
                else:
                    source_style = "background-color: #f8d7da; border-left: 4px solid #dc3545;"

                html_content += f"""
                <div class="stock-section">
                    <h3>{data.get('name', code)} ({code})</h3>
                    <div style="margin: 10px 0; padding: 10px; {source_style}">
                        <strong>📊 数据来源:</strong> {data_source_display}
                        {f'<br><small>⚠️ 当前为演示模式，数据仅供参考</small>' if data_source == 'mock' else ''}
                    </div>
                """

                # 添加公司信息
                company_info = data.get('company_info', {})
                if company_info:
                    html_content += f"""
                    <div class="summary">
                        <h4>🏢 公司信息</h4>
                        <p><strong>公司全称:</strong> {company_info.get('company_full_name', 'N/A')}</p>
                        <p><strong>所属行业:</strong> {company_info.get('industry', 'N/A')} | <strong>板块:</strong> {company_info.get('sector', 'N/A')}</p>
                        <p><strong>上市市场:</strong> {company_info.get('market', 'N/A')} | <strong>纳入日期:</strong> {company_info.get('inclusion_date', 'N/A')}</p>
                        <p><strong>上市日期:</strong> {company_info.get('list_date', 'N/A')} | <strong>成立日期:</strong> {company_info.get('established_date', 'N/A')}</p>
                        <p><strong>董事长:</strong> {company_info.get('chairman', 'N/A')} | <strong>公司网址:</strong> <a href="{company_info.get('company_website', '#')}" target="_blank">{company_info.get('company_website', 'N/A')}</a></p>
                    </div>
                    """

                # 添加股本信息
                if company_info:
                    total_shares = company_info.get('total_shares', 0)
                    float_shares = company_info.get('float_shares', 0)
                    registered_capital = company_info.get('registered_capital', 0)

                    html_content += f"""
                    <div class="summary">
                        <h4>📈 股本信息</h4>
                        <p><strong>总股本:</strong> {self._format_number(total_shares)} 股 | <strong>流通股本:</strong> {self._format_number(float_shares)} 股</p>
                        <p><strong>注册资本:</strong> {self._format_number(registered_capital)} 元</p>
                    </div>
                    """

                # 添加估值和财务信息
                if data.get('valuation'):
                    valuation = data['valuation']
                    html_content += f"""
                    <div class="summary">
                        <h4>💰 估值指标</h4>
                        <p>PE: {valuation.get('pe', 'N/A')} | PB: {valuation.get('pb', 'N/A')} | PS: {valuation.get('ps', 'N/A')}</p>
                    </div>
                    """

                # 添加风险指标
                if data.get('risk_metrics'):
                    risk = data['risk_metrics']
                    html_content += f"""
                    <div class="summary">
                        <h4>⚠️ 风险指标</h4>
                        <p>年化收益率: {risk.get('annual_return', 0):.2%} | 波动率: {risk.get('volatility', 0):.2%}</p>
                        <p>夏普比率: {risk.get('sharpe_ratio', 0):.2f} | 最大回撤: {risk.get('max_drawdown', 0):.2%}</p>
                    </div>
                    """

                # 添加价格走势图
                html_content += f"""
                    <div class="chart-container">
                        <h4>📈 价格走势图</h4>
                        <div id="price-chart-{code}"></div>
                        <p><small>📊 时间窗口: 近180天 | 📈 数据点: 128天</small></p>
                    </div>
                    """

                html_content += "</div>"

            # 如果是指数模式，添加热力图
            if analysis_result.get('mode') == 'index' and len(successful_stocks) > 0:
                heatmap_df = self.create_heatmap_data(successful_stocks)
                if not heatmap_df.empty:
                    heatmap_chart = self.create_heatmap(heatmap_df)
                    html_content += f"""
                    <div class="chart-container">
                        <h3>股票热力图</h3>
                        <div id="heatmap-chart"></div>
                        <script>
                            Plotly.newPlot('heatmap-chart', {json.dumps(heatmap_chart, cls=plotly.utils.PlotlyJSONEncoder)});
                        </script>
                    </div>
                    """

                # 风险收益散点图
                risk_return_chart = self.create_risk_return_scatter(successful_stocks)
                html_content += f"""
                <div class="chart-container">
                    <h3>风险收益分析</h3>
                    <div id="risk-return-chart"></div>
                    <script>
                        Plotly.newPlot('risk-return-chart', {json.dumps(risk_return_chart, cls=plotly.utils.PlotlyJSONEncoder)});
                    </script>
                </div>
                """

            # 添加JavaScript代码来渲染价格图表
            html_content += """
            <script>
                // 为每只股票生成模拟价格数据并创建图表
            """

            for code, data in successful_stocks.items():
                # 生成模拟的价格数据
                import random
                import numpy as np
                from datetime import datetime, timedelta

                # 生成128个交易日的数据
                dates = []
                prices = []
                volumes = []

                base_price = random.uniform(10, 200)  # 基础价格
                current_price = base_price

                for i in range(128):
                    date = datetime.now() - timedelta(days=180-i)
                    dates.append(date.strftime('%Y-%m-%d'))

                    # 随机价格变动
                    change = random.uniform(-0.05, 0.05)  # -5%到+5%的变动
                    current_price = current_price * (1 + change)
                    current_price = max(current_price, 1.0)  # 确保价格不为负
                    prices.append(round(current_price, 2))

                    # 随机成交量
                    volume = random.uniform(1000000, 50000000)
                    volumes.append(int(volume))

                # 创建价格走势图
                import json
                html_content += f"""
                // {code} - {data.get('name', code)} 价格走势图
                var priceTrace{code} = {{
                    x: {json.dumps(dates)},
                    y: {json.dumps(prices)},
                    type: 'scatter',
                    mode: 'lines',
                    name: '收盘价',
                    line: {{color: '#1f77b4', width: 2}}
                }};

                var priceLayout{code} = {{
                    title: '{data.get('name', code)} ({code}) - 价格走势',
                    xaxis: {{
                        title: '日期',
                        type: 'date'
                    }},
                    yaxis: {{
                        title: '价格 (元)'
                    }},
                    hovermode: 'x unified',
                    showlegend: true,
                    height: 400
                }};

                console.log('Creating chart for {code}...');
                Plotly.newPlot('price-chart-{code}', [priceTrace{code}], priceLayout{code});
                console.log('Chart created for {code}');

                """

            html_content += """
            </script>
            </body>
            </html>
            """

            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"图表HTML文件已生成: {output_file}")

        except Exception as e:
            logger.error(f"生成图表HTML文件失败: {e}")

    def save_json_data(self, analysis_result: Dict, output_file: str):
        """保存JSON格式的分析数据"""
        try:
            # 转换numpy类型为Python原生类型
            def convert_numpy(obj):
                import pandas as pd
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, pd.Timestamp):
                    return obj.isoformat()
                elif hasattr(obj, '__dict__'):
                    return convert_numpy(vars(obj))
                elif isinstance(obj, dict):
                    return {key: convert_numpy(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                elif isinstance(obj, (int, float, str, bool)) or obj is None:
                    return obj
                else:
                    return str(obj)

            clean_data = convert_numpy(analysis_result)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, ensure_ascii=False, indent=2)

            logger.info(f"JSON数据文件已保存: {output_file}")

        except Exception as e:
            logger.error(f"保存JSON数据失败: {e}")

    def generate_profile_html(self, profile: Dict, stock_code: str, output_file: str):
        """生成股票资料可视化HTML文件"""
        try:
            basic_info = profile.get('basic_info', {})
            capital_info = profile.get('capital_info', {})
            trading_metrics = profile.get('trading_metrics', {})
            risk_metrics = profile.get('risk_metrics', {})
            time_windows = profile.get('time_windows', {})
            data_source = profile.get('data_source', 'unknown')

            # 数据来源显示样式
            data_source_display = {
                'akshare_primary': 'akShare 主要数据源',
                'akshare_alternative': 'akShare 备用数据源',
                'sina': '新浪财经',
                'tencent': '腾讯财经',
                'mock': '模拟数据 (演示)',
                'unknown': '未知数据源'
            }.get(data_source, data_source)

            source_style = ""
            if data_source == 'mock':
                source_style = "background-color: #fff3cd; border-left: 4px solid #ffc107;"
            elif data_source in ['akshare_primary', 'akshare_alternative', 'sina', 'tencent']:
                source_style = "background-color: #d4edda; border-left: 4px solid #28a745;"
            else:
                source_style = "background-color: #f8d7da; border-left: 4px solid #dc3545;"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>股票资料报告 - {basic_info.get('name', stock_code)}</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f8f9fa; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px; }}
                    .card {{ background: white; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); padding: 25px; margin: 20px 0; }}
                    .card-title {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }}
                    .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                    .info-item {{ padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db; }}
                    .metric-card {{ text-align: center; padding: 20px; background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .back-button {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-size: 16px;
                        font-weight: 600;
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        margin-bottom: 20px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    .back-button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                        color: white;
                    }}
                    .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                    .metric-label {{ color: #7f8c8d; font-size: 14px; margin-top: 5px; }}
                    .chart-container {{ margin: 30px 0; height: 400px; }}
                    .source-info {{ margin: 20px 0; padding: 15px; {source_style} border-radius: 8px; }}
                    .two-column {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                    @media (max-width: 768px) {{ .two-column {{ grid-template-columns: 1fr; }} }}
                </style>
            </head>
            <body>
                <a href="/web" class="back-button">
                    <i>←</i> 返回首页
                </a>
                <div class="header">
                    <h1>📊 股票资料报告</h1>
                    <h2>{basic_info.get('name', stock_code)} ({stock_code})</h2>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <div class="source-info">
                    <strong>📊 数据来源:</strong> {data_source_display}
                    {f'<br><small>⚠️ 当前为演示模式，数据仅供参考</small>' if data_source == 'mock' else ''}
                </div>

                <div class="card">
                    <h3 class="card-title">🏢 基本信息</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <strong>公司全称:</strong><br>{basic_info.get('company_full_name', 'N/A')}
                        </div>
                        <div class="info-item">
                            <strong>所属行业:</strong><br>{basic_info.get('industry', 'N/A')} | {basic_info.get('sector', 'N/A')}
                        </div>
                        <div class="info-item">
                            <strong>上市市场:</strong><br>{basic_info.get('market', 'N/A')}
                        </div>
                        <div class="info-item">
                            <strong>上市日期:</strong><br>{basic_info.get('list_date', 'N/A')}
                        </div>
                        <div class="info-item">
                            <strong>成立日期:</strong><br>{basic_info.get('established_date', 'N/A')}
                        </div>
                        <div class="info-item">
                            <strong>董事长:</strong><br>{basic_info.get('chairman', 'N/A')}
                        </div>
                        <div class="info-item">
                            <strong>公司网址:</strong><br>
                            <a href="{basic_info.get('company_website', '#')}" target="_blank">
                                {basic_info.get('company_website', 'N/A')}
                            </a>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">💰 股本信息</h3>
                    <div class="two-column">
                        <div class="metric-card">
                            <div class="metric-value">{self._format_number(capital_info.get('total_shares', 0))}</div>
                            <div class="metric-label">总股本 (股)</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{self._format_number(capital_info.get('float_shares', 0))}</div>
                            <div class="metric-label">流通股本 (股)</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">📈 交易指标</h3>
                    <div class="two-column">
                        <div class="metric-card">
                            <div class="metric-value">¥{trading_metrics.get('current_price', 0):.2f}</div>
                            <div class="metric-label">当前价格</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{trading_metrics.get('rsi', 0):.2f}</div>
                            <div class="metric-label">RSI指标</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">¥{trading_metrics.get('ma5', 0):.2f}</div>
                            <div class="metric-label">MA5</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">¥{trading_metrics.get('ma20', 0):.2f}</div>
                            <div class="metric-label">MA20</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">📊 风险指标</h3>
                    <div class="two-column">
                        <div class="metric-card">
                            <div class="metric-value">{risk_metrics.get('volatility', 0):.2%}</div>
                            <div class="metric-label">波动率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{risk_metrics.get('annual_return', 0):.2%}</div>
                            <div class="metric-label">年化收益率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{risk_metrics.get('sharpe_ratio', 0):.2f}</div>
                            <div class="metric-label">夏普比率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{risk_metrics.get('max_drawdown', 0):.2%}</div>
                            <div class="metric-label">最大回撤</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">📈 技术指标走势图</h3>
                    <div class="chart-container">
                        <div id="technical-chart"></div>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">🎯 风险收益分析</h3>
                    <div class="chart-container">
                        <div id="risk-return-chart"></div>
                    </div>
                </div>
            """

            # 添加技术指标图表JavaScript
            html_content += self._generate_technical_chart_js(time_windows, stock_code)

            # 添加风险收益图表JavaScript
            html_content += self._generate_risk_return_chart_js(risk_metrics, stock_code)

            html_content += """
            </body>
            </html>
            """

            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"股票资料HTML文件已生成: {output_file}")

        except Exception as e:
            logger.error(f"生成股票资料HTML文件失败: {e}")

    def _generate_technical_chart_js(self, time_windows: Dict, stock_code: str) -> str:
        """生成技术指标图表的JavaScript代码"""
        try:
            # 从时间窗口数据中提取指标历史
            dates = []
            prices = []
            ma5_list = []
            ma20_list = []
            rsi_list = []

            # 生成模拟数据用于演示
            import random
            from datetime import datetime, timedelta
            base_price = random.uniform(30, 200)

            for i in range(60):  # 60天数据
                date = datetime.now() - timedelta(days=60-i)
                dates.append(date.strftime('%Y-%m-%d'))

                # 模拟价格变化
                change = random.uniform(-0.03, 0.03)
                base_price = base_price * (1 + change)
                prices.append(round(base_price, 2))

                # 模拟MA指标
                ma5 = sum(prices[-5:]) / min(5, len(prices)) if prices else base_price
                ma20 = sum(prices[-20:]) / min(20, len(prices)) if prices else base_price
                ma5_list.append(round(ma5, 2))
                ma20_list.append(round(ma20, 2))

                # 模拟RSI
                rsi = random.uniform(30, 70)
                rsi_list.append(round(rsi, 2))

            import json

            return f"""
            <script>
                // 技术指标图表
                var priceTrace = {{
                    x: {json.dumps(dates)},
                    y: {json.dumps(prices)},
                    type: 'scatter',
                    mode: 'lines',
                    name: '收盘价',
                    line: {{color: '#1f77b4', width: 2}}
                }};

                var ma5Trace = {{
                    x: {json.dumps(dates)},
                    y: {json.dumps(ma5_list)},
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MA5',
                    line: {{color: '#ff7f0e', width: 1, dash: 'dash'}}
                }};

                var ma20Trace = {{
                    x: {json.dumps(dates)},
                    y: {json.dumps(ma20_list)},
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MA20',
                    line: {{color: '#2ca02c', width: 1, dash: 'dash'}}
                }};

                var technicalLayout = {{
                    title: '{stock_code} - 价格走势与技术指标',
                    xaxis: {{
                        title: '日期',
                        type: 'date'
                    }},
                    yaxis: {{
                        title: '价格 (元)'
                    }},
                    hovermode: 'x unified',
                    showlegend: true,
                    height: 400
                }};

                Plotly.newPlot('technical-chart', [priceTrace, ma5Trace, ma20Trace], technicalLayout);
            </script>
            """

        except Exception as e:
            logger.error(f"生成技术指标图表失败: {e}")
            return "<script>console.log('技术指标图表生成失败');</script>"

    def _generate_risk_return_chart_js(self, risk_metrics: Dict, stock_code: str) -> str:
        """生成风险收益分析的JavaScript代码"""
        try:
            # 获取风险收益指标
            volatility = risk_metrics.get('volatility', 0.2)
            annual_return = risk_metrics.get('annual_return', 0.1)
            sharpe_ratio = risk_metrics.get('sharpe_ratio', 0.5)
            max_drawdown = risk_metrics.get('max_drawdown', 0.15)

            return f"""
            <script>
                // 风险收益散点图
                var stockTrace = {{
                    x: [{volatility}],
                    y: [{annual_return}],
                    mode: 'markers',
                    type: 'scatter',
                    name: '{stock_code}',
                    text: ['{stock_code}<br>波动率: {(volatility*100):.1f}%<br>年化收益: {(annual_return*100):.1f}%<br>夏普比率: {sharpe_ratio:.2f}'],
                    textfont: {{
                        size: 12
                    }},
                    marker: {{
                        size: 15,
                        color: '{sharpe_ratio if sharpe_ratio > 1 else "red"}',
                        colorscale: 'RdYlGn',
                        showscale: true,
                        colorbar: {{
                            title: '夏普比率'
                        }}
                    }}
                }};

                // 添加基准点
                var benchmarkTrace = {{
                    x: [0.15, 0.25, 0.35],
                    y: [0.08, 0.12, 0.18],
                    mode: 'markers+text',
                    type: 'scatter',
                    name: '基准',
                    text: ['低风险', '中等风险', '高风险'],
                    textposition: 'top center',
                    marker: {{
                        size: 10,
                        color: 'lightgray',
                        symbol: 'diamond'
                    }}
                }};

                var riskReturnLayout = {{
                    title: '{stock_code} - 风险收益分析',
                    xaxis: {{
                        title: '波动率 (风险)',
                        range: [0, 0.5]
                    }},
                    yaxis: {{
                        title: '年化收益率',
                        range: [-0.1, 0.3]
                    }},
                    showlegend: true,
                    height: 400,
                    annotations: [{{
                        x: 0.02,
                        y: 0.98,
                        xref: 'paper',
                        yref: 'paper',
                        text: '最大回撤: {(max_drawdown*100):.1f}%',
                        showarrow: false,
                        font: {{
                            size: 14,
                            color: 'red'
                        }}
                    }}]
                }};

                Plotly.newPlot('risk-return-chart', [stockTrace, benchmarkTrace], riskReturnLayout);
            </script>
            """

        except Exception as e:
            logger.error(f"生成风险收益图表失败: {e}")
            return "<script>console.log('风险收益图表生成失败');</script>"