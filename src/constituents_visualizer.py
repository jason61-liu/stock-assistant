#!/usr/bin/env python3
"""
指数成分股HTML可视化生成器
为指数成分股数据生成交互式HTML展示页面
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class IndexConstituentsVisualizer:
    """指数成分股可视化器"""

    def __init__(self):
        self.default_limit = 50  # 默认显示数量

    def generate_constituents_html(self,
                                 constituents_data: Dict,
                                 index_name: str,
                                 output_file: str) -> str:
        """
        生成指数成分股HTML展示页面

        Args:
            constituents_data: API返回的成分股数据
            index_name: 指数名称
            output_file: 输出HTML文件路径

        Returns:
            生成的HTML文件路径
        """

        if not constituents_data.get('success'):
            return self._generate_error_html(constituents_data, index_name, output_file)

        constituents = constituents_data.get('constituents', [])
        total_count = constituents_data.get('total_count', 0)
        returned_count = constituents_data.get('returned_count', 0)

        # 创建DataFrame
        df = pd.DataFrame(constituents)

        # 生成各种图表
        charts_html = self._generate_charts(df, index_name, total_count)

        # 生成数据表格
        table_html = self._generate_data_table(df, index_name)

        # 生成统计信息
        stats_html = self._generate_statistics(df, index_name, total_count, returned_count)

        # 生成完整HTML
        html_content = self._generate_full_html(
            index_name=index_name,
            stats_html=stats_html,
            charts_html=charts_html,
            table_html=table_html,
            total_count=total_count,
            returned_count=returned_count,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_file

    def _generate_charts(self, df: pd.DataFrame, index_name: str, total_count: int) -> str:
        """生成图表HTML"""
        charts_html = []

        if df.empty:
            return "<div class='chart-placeholder'>暂无数据</div>"

        # 1. 成分股分布概览
        overview_fig = go.Figure()
        overview_fig.add_trace(go.Indicator(
            mode = "number+gauge+delta",
            value = total_count,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{index_name} 成分股总数"},
            delta = {'reference': total_count},
            gauge = {
                'axis': {'range': [None, max(total_count, 500)]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 100], 'color': "lightgray"},
                    {'range': [100, 300], 'color': "gray"},
                    {'range': [300, 500], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': total_count
                }
            }
        ))
        overview_fig.update_layout(height=300)
        charts_html.append(overview_fig.to_html(full_html=False, include_plotlyjs=False))

        # 2. 股票代码分布
        if 'code' in df.columns:
            # 提取股票代码前缀分析市场分布
            df['market'] = df['code'].apply(lambda x: '沪市' if x.startswith('6') else '深市' if x.startswith(('0', '3')) else '其他')
            market_dist = df['market'].value_counts()

            market_fig = go.Figure(data=[
                go.Pie(
                    labels=market_dist.index,
                    values=market_dist.values,
                    hole=0.3,
                    marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1']
                )
            ])
            market_fig.update_layout(
                title=f"{index_name} 成分股市场分布",
                height=400
            )
            charts_html.append(market_fig.to_html(full_html=False, include_plotlyjs=False))

        # 3. 纳入日期分析（如果有数据）
        if '纳入日期' in df.columns and not df['纳入日期'].isna().all():
            df_temp = df[df['纳入日期'].notna()].copy()
            df_temp['纳入日期'] = pd.to_datetime(df_temp['纳入日期'])

            # 按月份统计纳入数量
            monthly_counts = df_temp.groupby(df_temp['纳入日期'].dt.to_period('M')).size()

            timeline_fig = go.Figure()
            timeline_fig.add_trace(go.Scatter(
                x=monthly_counts.index.astype(str),
                y=monthly_counts.values,
                mode='lines+markers',
                name='纳入数量',
                line=dict(color='#FF6B6B', width=2),
                marker=dict(size=8)
            ))
            timeline_fig.update_layout(
                title=f"{index_name} 成分股纳入时间分布",
                xaxis_title="时间",
                yaxis_title="纳入数量",
                height=400
            )
            charts_html.append(timeline_fig.to_html(full_html=False, include_plotlyjs=False))

        # 4. 股票名称词云图（使用柱状图替代）
        if 'name' in df.columns:
            # 分析股票名称中的高频词汇
            name_chars = []
            for name in df['name'].dropna():
                for char in name:
                    if len(char) >= 2 and char not in ['股份', '有限', '集团', '控股']:
                        name_chars.append(char)

            if name_chars:
                char_counts = pd.Series(name_chars).value_counts().head(15)

                wordcloud_fig = go.Figure(data=[
                    go.Bar(
                        x=char_counts.values,
                        y=char_counts.index,
                        orientation='h',
                        marker=dict(color='#4ECDC4', line=dict(color='#45B7D1', width=1))
                    )
                ])
                wordcloud_fig.update_layout(
                    title=f"{index_name} 成分股名称高频词汇",
                    xaxis_title="出现次数",
                    yaxis_title="关键词",
                    height=500,
                    yaxis={'categoryorder': 'total ascending'}
                )
                charts_html.append(wordcloud_fig.to_html(full_html=False, include_plotlyjs=False))

        return '\n'.join(charts_html)

    def _generate_data_table(self, df: pd.DataFrame, index_name: str) -> str:
        """生成数据表格"""
        if df.empty:
            return "<div class='no-data'>暂无成分股数据</div>"

        # 重新排序列，让重要信息在前
        columns_order = ['code', 'name']
        if '纳入日期' in df.columns:
            columns_order.append('纳入日期')
        if 'industry' in df.columns:
            columns_order.append('industry')
        if 'weight' in df.columns:
            columns_order.append('weight')

        # 添加其他列
        for col in df.columns:
            if col not in columns_order:
                columns_order.append(col)

        # 只保留存在的列
        available_columns = [col for col in columns_order if col in df.columns]
        df_table = df[available_columns].copy()

        # 重命名列名为中文显示
        column_rename_map = {
            'code': '股票代码',
            'name': '股票名称',
            'industry': '所属行业',
            'weight': '权重(%)',
            '纳入日期': '纳入日期'
        }
        df_table = df_table.rename(columns=column_rename_map)

        # 生成HTML表格
        table_html = df_table.to_html(
            classes='constituents-table table table-striped table-hover',
            table_id='constituentsTable',
            escape=False,
            index=False
        )

        # 添加搜索和排序功能的JavaScript
        search_script = """
        <script>
        $(document).ready(function() {
            $('#constituentsTable').DataTable({
                "pageLength": 25,
                "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "全部"]],
                "language": {
                    "search": "搜索股票:",
                    "lengthMenu": "显示 _MENU_ 条记录",
                    "info": "显示第 _START_ 至 _END_ 条，共 _TOTAL_ 条记录",
                    "paginate": {
                        "first": "首页",
                        "last": "末页",
                        "next": "下一页",
                        "previous": "上一页"
                    }
                },
                "order": [[ 0, "asc" ]]
            });
        });
        </script>
        """

        return f"""
        <div class="table-container">
            <h3>📋 成分股详细列表</h3>
            {table_html}
        </div>
        {search_script}
        """

    def _generate_statistics(self, df: pd.DataFrame, index_name: str, total_count: int, returned_count: int) -> str:
        """生成统计信息"""
        if df.empty:
            return "<div class='stats-container'><h3>📊 统计信息</h3><p>暂无数据</p></div>"

        stats_html = []
        stats_html.append(f"<h3>📊 {index_name} 统计信息</h3>")

        # 数据完整性提示
        if returned_count == total_count:
            stats_html.append(f"<div class='alert alert-success'>✅ 本报告包含完整的 {total_count} 只成分股数据</div>")
        else:
            stats_html.append(f"<div class='alert alert-warning'>⚠️ 本报告显示前 {returned_count} 只成分股，总计 {total_count} 只</div>")

        # 基础统计
        stats_html.append("<div class='stats-grid'>")
        stats_html.append(f"<div class='stat-item'><span class='stat-label'>成分股总数:</span><span class='stat-value'>{total_count}</span></div>")
        stats_html.append(f"<div class='stat-item'><span class='stat-label'>报告包含:</span><span class='stat-value'>{returned_count}</span></div>")

        # 市场分布统计
        if 'code' in df.columns:
            sh_count = sum(1 for code in df['code'] if str(code).startswith('6'))
            sz_count = sum(1 for code in df['code'] if str(code).startswith(('0', '3')))
            other_count = len(df) - sh_count - sz_count

            stats_html.append(f"<div class='stat-item'><span class='stat-label'>沪市股票:</span><span class='stat-value'>{sh_count}</span></div>")
            stats_html.append(f"<div class='stat-item'><span class='stat-label'>深市股票:</span><span class='stat-value'>{sz_count}</span></div>")
            if other_count > 0:
                stats_html.append(f"<div class='stat-item'><span class='stat-label'>其他市场:</span><span class='stat-value'>{other_count}</span></div>")

        stats_html.append("</div>")

        # 纳入日期统计
        if '纳入日期' in df.columns and not df['纳入日期'].isna().all():
            df_temp = df[df['纳入日期'].notna()].copy()
            if not df_temp.empty:
                recent_count = sum(1 for date in df_temp['纳入日期']
                                 if pd.to_datetime(date) >= pd.to_datetime('2024-01-01'))
                stats_html.append(f"<div class='stat-item'><span class='stat-label'>2024年新纳入:</span><span class='stat-value'>{recent_count}</span></div>")

        # 数据表格说明
        stats_html.append(f"""
        <div class="alert alert-info">
            <strong>📋 数据表格说明:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>下方表格显示全部 {returned_count} 只成分股</li>
                <li>支持搜索、排序和分页功能</li>
                <li>默认每页显示25条记录，可调整显示数量</li>
            </ul>
        </div>
        """)

        return f"<div class='stats-container'>{ ''.join(stats_html) }</div>"

    def _generate_error_html(self, error_data: Dict, index_name: str, output_file: str) -> str:
        """生成错误页面HTML"""
        error_message = error_data.get('detail', '未知错误')

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>指数成分股查询错误 - {index_name}</title>
            <meta charset="utf-8">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }}
                .error-container {{ max-width: 800px; margin: 50px auto; text-align: center; }}
                .error-icon {{ font-size: 64px; color: #dc3545; margin-bottom: 20px; }}
                .error-message {{ background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .back-link {{ color: #007bff; text-decoration: none; }}
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
                    margin-top: 20px;
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
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h1>查询失败</h1>
                <div class="error-message">
                    <h3>指数: {index_name}</h3>
                    <p>错误信息: {error_message}</p>
                </div>
                <a href="/web" class="back-button">
                    <i>←</i> 返回首页
                </a>
            </div>
        </body>
        </html>
        """

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_file

    def _generate_full_html(self, index_name: str, stats_html: str, charts_html: str,
                          table_html: str, total_count: int, returned_count: int, timestamp: str) -> str:
        """生成完整的HTML页面"""

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{index_name} 成分股分析报告</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.0/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.0/js/dataTables.bootstrap5.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.datatables.net/1.13.0/css/dataTables.bootstrap5.min.css" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }}

                .main-container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}

                .header {{
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}

                .header h1 {{
                    margin: 0;
                    font-size: 2.5rem;
                    font-weight: 300;
                }}

                .header .subtitle {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                    margin-top: 10px;
                }}

                .content {{
                    padding: 30px;
                }}

                .section {{
                    margin-bottom: 40px;
                    background: white;
                    border-radius: 10px;
                    padding: 25px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}

                .section-title {{
                    color: #2c3e50;
                    font-size: 1.5rem;
                    font-weight: 500;
                    margin-bottom: 20px;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}

                .stats-container {{
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border-radius: 10px;
                    padding: 25px;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }}

                .stat-item {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }}

                .stat-item:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                }}

                .stat-label {{
                    display: block;
                    color: #6c757d;
                    font-size: 0.9rem;
                    margin-bottom: 8px;
                }}

                .stat-value {{
                    display: block;
                    color: #2c3e50;
                    font-size: 1.8rem;
                    font-weight: 600;
                }}

                .chart-container {{
                    margin-bottom: 30px;
                    min-height: 400px;
                }}

                .table-container {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                }}

                .constituents-table {{
                    width: 100% !important;
                }}

                .constituents-table th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 500;
                }}

                .constituents-table td {{
                    vertical-align: middle;
                }}

                .footer {{
                    background: #2c3e50;
                    color: white;
                    text-align: center;
                    padding: 20px;
                    font-size: 0.9rem;
                }}

                .no-data {{
                    text-align: center;
                    padding: 40px;
                    color: #6c757d;
                    font-style: italic;
                }}

                .back-btn {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 25px;
                    text-decoration: none;
                    margin-bottom: 20px;
                    transition: transform 0.2s;
                }}

                .back-btn:hover {{
                    transform: translateY(-2px);
                    color: white;
                }}

                @media (max-width: 768px) {{
                    .header h1 {{ font-size: 2rem; }}
                    .content {{ padding: 20px; }}
                    .section {{ padding: 20px; }}
                    .stats-grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="main-container">
                <div class="header">
                    <a href="/web" class="back-btn">← 返回首页</a>
                    <h1>📊 {index_name} 成分股分析报告</h1>
                    <div class="subtitle">
                        总计 {total_count} 只成分股 | 当前显示 {returned_count} 只 | 生成时间: {timestamp}
                    </div>
                </div>

                <div class="content">
                    {stats_html}

                    <div class="section">
                        <h3 class="section-title">📈 数据可视化</h3>
                        <div class="row">
                            {charts_html}
                        </div>
                    </div>

                    {table_html}
                </div>

                <div class="footer">
                    <p>🏦 A股行情可视化服务 | 数据来源: akShare API | 专业金融数据分析平台</p>
                </div>
            </div>
        </body>
        </html>
        """