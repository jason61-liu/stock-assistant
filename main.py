#!/usr/bin/env python3
"""
A股行情可视化服务主入口
"""
import uvicorn
import json
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from datetime import datetime
import os
import logging

from src.api import router
from src.config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """递归转换numpy类型为Python原生类型"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # 处理有__dict__属性的对象
        try:
            return convert_numpy_types(vars(obj))
        except:
            return str(obj)
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        # 其他类型转换为字符串
        return str(obj)

class CustomJSONResponse(JSONResponse):
    """自定义JSON响应类，处理numpy类型"""
    def render(self, content) -> bytes:
        converted_content = convert_numpy_types(content)
        return json.dumps(
            converted_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":")
        ).encode("utf-8")

app = FastAPI(
    title="A股行情可视化服务",
    description="零配置的A股行情数据获取和可视化API服务",
    version="1.0.0",
    default_response_class=CustomJSONResponse
)

# 挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(router, prefix="/api/v1")

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Web操作界面"""
    web_interface_path = os.path.join("static", "web_interface.html")
    if os.path.exists(web_interface_path):
        with open(web_interface_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="<h1>Web界面不存在</h1><p>请检查static/web_interface.html文件</p>", status_code=404)

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": "接口不存在"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"内部服务器错误: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "内部服务器错误"}
    )

# 中间件
@app.middleware("http")
async def add_logging_middleware(request: Request, call_next):
    """添加请求日志"""
    start_time = datetime.now()

    response = await call_next(request)

    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页 - 重定向到Web界面"""
    # 检查Web界面文件是否存在
    web_interface_path = os.path.join("static", "web_interface.html")
    if os.path.exists(web_interface_path):
        # 返回Web界面
        with open(web_interface_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        # 如果Web界面文件不存在，返回简单的重定向页面
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>A股行情可视化服务</title>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="0; url=/static/web_interface.html">
            <style>
                body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; text-align: center; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
                .input-group { margin: 20px 0; }
                input, button { padding: 10px; margin: 5px; border-radius: 5px; border: 1px solid #ddd; }
                button { background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
                .btn-secondary { background: #6c757d; }
                .btn-secondary:hover { background: #5a6268; }
            .btn-success { background: #28a745; }
            .btn-success:hover { background: #218838; }
            .result { margin-top: 20px; }
            .api-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .api-item { padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .api-item h4 { color: #007bff; margin-bottom: 10px; }
            .api-item code { background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 A股行情可视化服务</h1>
            <p>零配置的A股行情数据获取和可视化API服务</p>
            <p>支持股票分析、指数成分股查询、技术指标分析等</p>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 10px; margin-top: 10px; border-radius: 5px;">
                <strong>💡 数据来源说明:</strong> 本服务优先使用真实市场数据，如遇网络问题会自动切换为模拟数据以保持演示功能
            </div>
        </div>

        <!-- 股票分析 -->
        <div class="section">
            <h2>🔍 股票行情分析</h2>
            <div class="input-group">
                <h3>输入股票代码或指数名称</h3>
                <input type="text" id="stockInput" placeholder="例如: 上证100, SSE100, 000001, 600000" style="width: 300px;">
                <button onclick="fetchStockData()">获取行情数据</button>
            </div>
            <div id="result" class="result"></div>
        </div>

        <!-- 指数成分股查询 -->
        <div class="section">
            <h2>📈 指数成分股查询</h2>
            <div class="input-group">
                <h3>选择指数</h3>
                <select id="indexSelect">
                    <option value="中证100">中证100</option>
                    <option value="中证200">中证200</option>
                    <option value="沪深300" selected>沪深300</option>
                    <option value="中证500">中证500</option>
                </select>
                <input type="number" id="limitInput" placeholder="显示数量" value="20" min="1" max="100" style="width: 100px;">
                <button onclick="fetchIndexConstituents()">查询成分股</button>
                <button onclick="fetchIndexDetails()" class="btn-success">获取详细信息</button>
                <button onclick="generateIndexHtml()" class="btn-primary">📊 生成可视化报告</button>
                <button onclick="fetchIndexOverview()" class="btn-secondary">指数概览</button>
            </div>
            <div id="indexResult" class="result"></div>
        </div>

        <!-- 股票信息查询 -->
        <div class="section">
            <h2>🏢 股票公司信息</h2>
            <div class="input-group">
                <h3>查询股票详情</h3>
                <input type="text" id="stockCodeInput" placeholder="输入股票代码，如: 000001" style="width: 200px;">
                <button onclick="fetchStockProfile()">获取公司信息</button>
                <button onclick="searchStocks()" class="btn-success">搜索股票</button>
            </div>
            <div id="profileResult" class="result"></div>
        </div>

        <!-- API文档 -->
        <div class="section">
            <h2>🔧 API接口文档</h2>
            <div class="api-list">
                <div class="api-item">
                    <h4>股票分析</h4>
                    <p><code>GET /api/v1/stocks/{input}</code></p>
                    <p>分析股票或指数的行情数据</p>
                </div>
                <div class="api-item">
                    <h4>指数成分股</h4>
                    <p><code>GET /api/v1/indices/{index_name}/constituents</code></p>
                    <p>获取指数成分股列表</p>
                </div>
                <div class="api-item">
                    <h4>指数分析</h4>
                    <p><code>GET /api/v1/indices/{index_name}/analysis</code></p>
                    <p>获取指数详细分析报告</p>
                </div>
                <div class="api-item">
                    <h4>股票详情</h4>
                    <p><code>GET /api/v1/stocks/{stock_code}/profile</code></p>
                    <p>获取股票公司详细信息</p>
                </div>
                <div class="api-item">
                    <h4>股票搜索</h4>
                    <p><code>GET /api/v1/stocks/search/{keyword}</code></p>
                    <p>根据关键词搜索股票</p>
                </div>
                <div class="api-item">
                    <h4>支持指标</h4>
                    <p><code>GET /api/v1/indicators</code></p>
                    <p>获取支持的技术指标列表</p>
                </div>
            </div>
        </div>

        <script>
            async function fetchStockData() {
                const input = document.getElementById('stockInput').value;
                if (!input) {
                    alert('请输入股票代码或指数名称');
                    return;
                }

                try {
                    const response = await fetch(`/api/v1/stocks/${encodeURIComponent(input)}`);
                    const data = await response.json();

                    const resultDiv = document.getElementById('result');
                    if (response.ok) {
                        // 获取数据源信息
                        let dataSources = [];
                        if (data.data && data.data.stocks) {
                            Object.values(data.data.stocks).forEach(stock => {
                                if (stock.data_source) {
                                    dataSources.push(stock.data_source);
                                }
                            });
                        }

                        // 去重数据源
                        const uniqueSources = [...new Set(dataSources)];

                        // 构建数据源显示
                        let dataSourceHtml = '';
                        if (uniqueSources.length > 0) {
                            const sourceDisplay = {
                                'akshare_primary': 'akShare 主要数据源',
                                'akshare_alternative': 'akShare 备用数据源',
                                'sina': '新浪财经',
                                'tencent': '腾讯财经',
                                'mock': '模拟数据 (演示模式)',
                                'unknown': '未知数据源'
                            };

                            uniqueSources.forEach(source => {
                                const displayText = sourceDisplay[source] || source;
                                const isMock = source === 'mock';
                                const style = isMock ? 'background-color: #fff3cd; border-left: 3px solid #ffc107; padding: 5px; margin: 5px 0;' :
                                              'background-color: #d4edda; border-left: 3px solid #28a745; padding: 5px; margin: 5px 0;';
                                dataSourceHtml += `<div style="${style}"><strong>📊 数据来源:</strong> ${displayText}${isMock ? '<br><small>⚠️ 当前为演示模式，数据仅供参考</small>' : ''}</div>`;
                            });
                        }

                        resultDiv.innerHTML = `
                            <h3>✅ 查询成功</h3>
                            <p>📊 股票数量: ${data.stock_count}</p>
                            <p>📈 查询模式: ${data.mode}</p>
                            ${dataSourceHtml}
                            <p>📄 <a href="${data.json_url}" target="_blank">查看JSON数据</a></p>
                            <p>📊 <a href="${data.chart_url}" target="_blank">查看图表</a></p>
                        `;
                    } else {
                        resultDiv.innerHTML = `<p style="color: red;">❌ 错误: ${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `<p style="color: red;">❌ 请求失败: ${error.message}</p>`;
                }
            }

            async function fetchIndexConstituents() {
                const indexName = document.getElementById('indexSelect').value;
                const limit = document.getElementById('limitInput').value || 20;

                try {
                    const response = await fetch(`/api/v1/indices/${encodeURIComponent(indexName)}/constituents?limit=${limit}`);
                    const data = await response.json();

                    const resultDiv = document.getElementById('indexResult');
                    if (response.ok) {
                        let constituents = data.constituents.slice(0, 15).map(c => `${c.code} ${c.name}`).join(', ');
                        if (data.constituents.length > 15) {
                            constituents += ` ... 等${data.total_count}只股票`;
                        }

                        resultDiv.innerHTML = `
                            <h3>✅ ${indexName} 成分股</h3>
                            <p>📊 总成分股数量: <strong>${data.total_count}</strong></p>
                            <p>📈 返回数量: <strong>${data.returned_count}</strong></p>
                            <p>🏢 成分股: ${constituents}</p>
                            <div style="margin-top: 15px;">
                                <button onclick="fetchIndexDetails('${indexName}')" class="btn-success">获取详细信息</button>
                                <button onclick="generateIndexHtml()" class="btn-primary">📊 生成可视化报告</button>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<p style="color: red;">❌ 错误: ${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('indexResult').innerHTML = `<p style="color: red;">❌ 请求失败: ${error.message}</p>`;
                }
            }

            async function fetchIndexDetails() {
                const indexName = document.getElementById('indexSelect').value;
                const limit = Math.min(parseInt(document.getElementById('limitInput').value) || 20, 10); // 详细查询限制为10只

                try {
                    const response = await fetch(`/api/v1/indices/${encodeURIComponent(indexName)}/constituents/details?limit=${limit}`);
                    const data = await response.json();

                    const resultDiv = document.getElementById('indexResult');
                    if (response.ok) {
                        let details = data.constituents.map(c => `
                            <div style="margin: 10px 0; padding: 10px; border: 1px solid #eee; border-radius: 5px;">
                                <strong>${c.code} ${c.name}</strong><br>
                                ${c.basic_info ? `
                                    上市日期: ${c.basic_info.list_date || 'N/A'}<br>
                                    行业: ${c.basic_info.industry || 'N/A'}<br>
                                    PE: ${c.basic_info.pe || 'N/A'}
                                ` : '信息获取失败'}
                            </div>
                        `).join('');

                        resultDiv.innerHTML = `
                            <h3>📊 ${indexName} 详细信息</h3>
                            <p>✅ 成功获取: ${data.successful_count}/${data.total_count}</p>
                            ${details}
                        `;
                    } else {
                        resultDiv.innerHTML = `<p style="color: red;">❌ 错误: ${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('indexResult').innerHTML = `<p style="color: red;">❌ 请求失败: ${error.message}</p>`;
                }
            }

            async function fetchStockProfile() {
                const stockCode = document.getElementById('stockCodeInput').value;
                if (!stockCode) {
                    alert('请输入股票代码');
                    return;
                }

                try {
                    const response = await fetch(`/api/v1/stocks/${encodeURIComponent(stockCode)}/profile`);
                    const data = await response.json();

                    const resultDiv = document.getElementById('profileResult');
                    if (response.ok) {
                        const profile = data.profile;
                        const basicInfo = profile.company_info || [];

                        resultDiv.innerHTML = `
                            <h3>🏢 ${data.stock_code} 公司信息</h3>
                            <div style="margin: 15px 0;">
                                ${basicInfo.slice(0, 10).map(info => `
                                    <div><strong>${info.item}:</strong> ${info.value}</div>
                                `).join('')}
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<p style="color: red;">❌ 错误: ${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('profileResult').innerHTML = `<p style="color: red;">❌ 请求失败: ${error.message}</p>`;
                }
            }

            async function searchStocks() {
                const keyword = prompt('请输入搜索关键词（股票名称或代码）:');
                if (!keyword) return;

                try {
                    const response = await fetch(`/api/v1/stocks/search/${encodeURIComponent(keyword)}?limit=10`);
                    const data = await response.json();

                    const resultDiv = document.getElementById('profileResult');
                    if (response.ok) {
                        const stocks = data.stocks.map(s => `<div style="margin: 5px 0;">📊 ${s.code} ${s.name}</div>`).join('');

                        resultDiv.innerHTML = `
                            <h3>🔍 搜索结果: ${keyword}</h3>
                            <p>📊 找到 ${data.total_found} 只股票，显示前 ${data.returned_count} 只</p>
                            ${stocks}
                        `;
                    } else {
                        resultDiv.innerHTML = `<p style="color: red;">❌ 错误: ${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('profileResult').innerHTML = `<p style="color: red;">❌ 搜索失败: ${error.message}</p>`;
                }
            }

            async function fetchIndexOverview() {
                try {
                    const response = await fetch('/api/v1/indices/overview');
                    const data = await response.json();

                    const resultDiv = document.getElementById('indexResult');
                    if (response.ok) {
                        let overview = Object.entries(data.indices).map(([name, info]) => `
                            <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                                <strong>${name}</strong> - ${info.info.name}<br>
                                成分股数量: ${info.constituents_count}<br>
                                状态: ${info.available ? '✅ 可用' : '❌ 不可用'}
                            </div>
                        `).join('');

                        resultDiv.innerHTML = `
                            <h3>📊 指数概览</h3>
                            <p>📈 总指数数量: ${data.total_indices}</p>
                            <p>✅ 可用指数: ${data.available_indices}</p>
                            ${overview}
                        `;
                    } else {
                        resultDiv.innerHTML = `<p style="color: red;">❌ 错误: ${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('indexResult').innerHTML = `<p style="color: red;">❌ 请求失败: ${error.message}</p>`;
                }
            }

            async function generateIndexHtml() {
                const indexName = document.getElementById('indexSelect').value;

                const resultDiv = document.getElementById('indexResult');
                resultDiv.innerHTML = `
                    <h3>🔄 正在生成 ${indexName} 完整可视化报告...</h3>
                    <p>⏳ 请稍候，正在获取所有成分股数据并生成报告，这可能需要几秒钟...</p>
                `;

                try {
                    // 不限制数量，获取所有成分股数据
                    const response = await fetch(`/api/v1/indices/${encodeURIComponent(indexName)}/constituents?generate_html=true`);
                    const data = await response.json();

                    if (response.ok && data.html_url) {
                        const htmlUrl = data.html_url;
                        resultDiv.innerHTML = `
                            <h3>✅ ${indexName} 完整可视化报告生成成功！</h3>
                            <p>📊 总成分股数量: <strong>${data.total_count}</strong></p>
                            <p>📈 报告包含数量: <strong>${data.html_generated_count || data.total_count}</strong>（全部成分股）</p>
                            <p>📋 JSON返回数量: <strong>${data.returned_count}</strong></p>
                            <div style="margin: 20px 0;">
                                <a href="${htmlUrl}" target="_blank" class="btn-primary" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 25px; font-weight: 500;">
                                    📊 查看完整可视化报告
                                </a>
                            </div>
                            <p style="color: #666; font-size: 0.9em;">
                                💡 报告包含：所有${data.html_generated_count || data.total_count}只成分股的统计图表、市场分布、数据表格等详细分析
                            </p>
                        `;
                    } else {
                        throw new Error(data.detail || '生成HTML文件失败');
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <h3>❌ 生成可视化报告失败</h3>
                        <p style="color: red;">错误信息: ${error.message}</p>
                        <button onclick="generateIndexHtml()" class="btn-primary">🔄 重试</button>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )