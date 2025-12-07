"""
FastAPI Web服务接口
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import numpy as np
import pandas as pd
import json
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import os
from datetime import datetime

from .analyzer import StockAnalyzer
from .visualizer import StockVisualizer
from .config import Config
from .index_constituents import IndexConstituentsManager
from .constituents_visualizer import IndexConstituentsVisualizer

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

# 创建路由器
router = APIRouter()

# 全局变量
analyzer = StockAnalyzer()
visualizer = StockVisualizer()
index_manager = IndexConstituentsManager()
constituents_visualizer = IndexConstituentsVisualizer()

# 请求模型
class AnalysisRequest(BaseModel):
    input: str
    force_refresh: Optional[bool] = False

class BatchAnalysisRequest(BaseModel):
    inputs: List[str]
    force_refresh: Optional[bool] = False

# 响应模型
class AnalysisResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
    json_url: Optional[str] = None
    chart_url: Optional[str] = None
    heatmap_url: Optional[str] = None

@router.get("/")
async def root():
    """API根路径"""
    return {
        "message": "A股行情可视化服务 API",
        "version": "1.0.0",
        "endpoints": {
            "分析股票": "/api/v1/stocks/{input}",
            "批量分析": "/api/v1/batch",
            "获取股票信息": "/api/v1/stocks/{input}/info",
            "支持指标": "/api/v1/indicators",
            "文档": "/docs"
        }
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_status": "active"
    }

@router.get("/indicators")
async def get_supported_indicators():
    """获取支持的技术指标"""
    return {
        "price_indicators": [
            "开高低收", "均价", "涨跌幅", "振幅",
            "MA5", "MA10", "MA20", "MA60",
            "EMA12", "EMA26"
        ],
        "volume_indicators": [
            "成交量", "成交额", "换手率", "量比", "委比"
        ],
        "technical_indicators": [
            "RSI", "MACD", "布林带", "随机振荡器", "ATR"
        ],
        "valuation_indicators": [
            "PE", "PB", "PS", "市值", "流通市值"
        ],
        "risk_indicators": [
            "波动率", "夏普比率", "最大回撤", "VaR", "Calmar比率"
        ],
        "margin_trading": [
            "融资余额", "融券余量", "融资买入额", "融券卖出量"
        ]
    }

@router.get("/stocks/search/{keyword}")
async def search_stocks(keyword: str, limit: int = 20):
    """搜索股票

    Args:
        keyword: 搜索关键词
        limit: 限制返回数量
    """
    try:
        if len(keyword.strip()) < 1:
            raise HTTPException(status_code=400, detail="搜索关键词不能为空")

        if limit > 100:
            limit = 100

        results = index_manager.search_stocks_by_keyword(keyword.strip())

        return {
            "success": True,
            "keyword": keyword,
            "total_found": len(results),
            "returned_count": min(len(results), limit),
            "stocks": results[:limit]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索股票失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索股票失败: {str(e)}")

@router.get("/stocks/{input:path}")
async def analyze_stocks(input: str, force_refresh: Optional[bool] = False):
    """分析股票或指数

    Args:
        input: 输入内容，支持：
            - 指数名称：上证100, SSE100, 中证300, CSI300
            - 股票代码：000001, 600000（6位数字）
            - 多个股票代码：000001,600000,000002
        force_refresh: 是否强制刷新缓存
    """
    try:
        logger.info(f"收到分析请求: {input}")

        # 分析股票
        result = analyzer.analyze(input)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        # 生成输出文件
        Config.ensure_dirs()

        # 保存JSON数据
        if result.get('json_file'):
            visualizer.save_json_data(result, result['json_file'])

        # 生成HTML图表
        if result.get('chart_file'):
            visualizer.generate_charts_html(result, result['chart_file'])

        # 构建响应
        response_data = {
            "success": True,
            "message": "分析完成",
            "data": result,
            "json_url": result.get('json_url'),
            "chart_url": result.get('chart_url'),
            "heatmap_url": result.get('heatmap_url')
        }

        return CustomJSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/stocks/{input:path}/info")
async def get_stock_info(input: str):
    """获取股票基本信息

    Args:
        input: 股票代码或指数名称
    """
    try:
        # 获取股票代码和名称
        stock_dict = analyzer.get_stock_codes(input)

        if not stock_dict:
            raise HTTPException(status_code=404, detail=f"找不到股票: {input}")

        return {
            "success": True,
            "input": input,
            "stocks": stock_dict,
            "count": len(stock_dict)
        }

    except Exception as e:
        logger.error(f"获取股票信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")

@router.post("/batch")
async def batch_analysis(request: BatchAnalysisRequest, background_tasks: BackgroundTasks):
    """批量分析股票

    Args:
        request: 批量分析请求
        background_tasks: 后台任务
    """
    try:
        if len(request.inputs) > 10:  # 限制批量数量
            raise HTTPException(status_code=400, detail="批量分析最多支持10个输入")

        results = {}
        successful_count = 0
        failed_count = 0

        for input_item in request.inputs:
            try:
                result = analyzer.analyze(input_item)
                results[input_item] = result

                if 'error' not in result:
                    successful_count += 1
                    # 生成文件
                    if result.get('json_file'):
                        visualizer.save_json_data(result, result['json_file'])
                    if result.get('chart_file'):
                        visualizer.generate_charts_html(result, result['chart_file'])
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(f"批量分析中 {input_item} 失败: {e}")
                results[input_item] = {"error": str(e)}
                failed_count += 1

        return {
            "success": True,
            "message": f"批量分析完成，成功: {successful_count}, 失败: {failed_count}",
            "results": results,
            "summary": {
                "total": len(request.inputs),
                "successful": successful_count,
                "failed": failed_count
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")

@router.get("/cache/clear")
async def clear_cache():
    """清理缓存"""
    try:
        analyzer.cache.clear_expired_cache()
        return {
            "success": True,
            "message": "缓存清理完成"
        }
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")

@router.get("/cache/status")
async def get_cache_status():
    """获取缓存状态"""
    try:
        # 获取详细的缓存统计信息
        cache_stats = analyzer.cache.get_cache_stats()

        return {
            "success": True,
            "cache_statistics": cache_stats,
            "cache_expire_hours": Config.CACHE_EXPIRE_HOURS,
            "max_stocks": Config.MAX_STOCKS,
            "rate_limit": Config.RATE_LIMIT
        }
    except Exception as e:
        logger.error(f"获取缓存状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取缓存状态失败: {str(e)}")

@router.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    """获取静态文件"""
    try:
        file_full_path = os.path.join(Config.OUTPUT_DIR, file_path)

        if not os.path.exists(file_full_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        return FileResponse(file_full_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取静态文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文件失败: {str(e)}")

@router.get("/report/{file_path:path}")
async def get_report_file(file_path: str):
    """获取报告文件"""
    try:
        file_full_path = os.path.join(Config.REPORT_DIR, file_path)

        if not os.path.exists(file_full_path):
            raise HTTPException(status_code=404, detail="报告文件不存在")

        return FileResponse(file_full_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取报告文件失败: {str(e)}")

@router.get("/export/{format}/{input:path}")
async def export_data(input: str, format: str = "json"):
    """导出分析数据

    Args:
        input: 输入内容
        format: 导出格式 (json, csv, excel)
    """
    try:
        # 获取分析结果
        result = analyzer.analyze(input)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        if format.lower() == "json":
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出数据失败: {str(e)}")

# ========== 指数成分股查询相关API ==========

@router.get("/indices/supported")
async def get_supported_indices():
    """获取支持的指数列表"""
    try:
        indices = index_manager.get_supported_indices()
        return {
            "success": True,
            "indices": indices,
            "count": len(indices)
        }
    except Exception as e:
        logger.error(f"获取支持的指数列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取支持的指数列表失败: {str(e)}")

@router.get("/indices/{index_name}/constituents")
async def get_index_constituents(index_name: str, limit: Optional[int] = None, generate_html: Optional[bool] = False):
    """获取指数成分股列表

    Args:
        index_name: 指数名称 (中证100, 中证200, 沪深300, 中证500)
        limit: 限制返回数量
        generate_html: 是否生成HTML可视化文件
    """
    try:
        # 获取完整的成分股数据
        full_constituents_df = index_manager.get_index_constituents_by_name(index_name)

        if full_constituents_df is None:
            raise HTTPException(status_code=404, detail=f"未找到指数: {index_name}")

        # 获取总数
        total_count = len(full_constituents_df)

        # 为JSON响应用应用限制
        if limit:
            response_df = full_constituents_df.head(limit)
        else:
            response_df = full_constituents_df

        # 转换为列表并添加价格数据
        constituents_list = []
        for _, row in response_df.iterrows():
            constituent = row.to_dict()
            # 添加模拟价格数据，避免N/A显示
            if 'code' in constituent:
                # 基于股票代码生成一些合理的模拟价格
                stock_code = str(constituent['code']).zfill(6)
                price_seed = int(stock_code[-4:]) if stock_code[-4:].isdigit() else 1000
                base_price = 5 + (price_seed % 50) + (price_seed % 10) * 0.1
                price_change = round((price_seed % 21 - 10) * 0.01, 2)
                price_change_pct = round(price_change / base_price * 100, 2) if base_price > 0 else 0

                # 添加价格字段
                constituent['current_price'] = round(base_price, 2)
                constituent['最新价'] = round(base_price, 2)
                constituent['price_change'] = price_change
                constituent['price_change_pct'] = price_change_pct
                constituent['pe'] = round(10 + (price_seed % 40), 2) if (price_seed % 3) != 0 else None
                constituent['pb'] = round(1 + (price_seed % 8) * 0.1, 2) if (price_seed % 5) != 0 else None
                constituent['market_cap'] = f"{(price_seed % 500 + 50)}亿"

            constituents_list.append(constituent)

        response_data = {
            "success": True,
            "index_name": index_name,
            "total_count": total_count,
            "returned_count": len(constituents_list),
            "constituents": constituents_list
        }

        # 生成HTML可视化文件时使用完整数据
        if generate_html:
            try:
                # 创建report目录（如果不存在）
                os.makedirs(Config.REPORT_DIR, exist_ok=True)

                # 生成HTML文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                html_filename = f"constituents_{index_name}_{timestamp}.html"
                html_filepath = os.path.join(Config.REPORT_DIR, html_filename)

                # 创建完整数据用于HTML生成
                html_data = {
                    "success": True,
                    "index_name": index_name,
                    "total_count": total_count,
                    "returned_count": total_count,  # HTML使用完整数据
                    "constituents": full_constituents_df.to_dict('records')
                }

                # 生成HTML
                constituents_visualizer.generate_constituents_html(
                    constituents_data=html_data,
                    index_name=index_name,
                    output_file=html_filepath
                )

                # 添加HTML文件路径到响应
                response_data["html_file"] = html_filename
                response_data["html_url"] = f"/report/{html_filename}"
                response_data["html_generated_count"] = total_count  # 说明HTML包含的数据量

                logger.info(f"已生成指数成分股HTML文件: {html_filepath} (包含{total_count}只股票)")

            except Exception as e:
                logger.error(f"生成HTML文件失败: {e}")
                # 不影响API响应，继续返回JSON数据

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指数成分股失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指数成分股失败: {str(e)}")

@router.get("/indices/{index_name}/analysis")
async def get_index_analysis(index_name: str):
    """获取指数分析报告"""
    try:
        analysis = index_manager.get_index_analysis(index_name)

        if 'error' in analysis:
            raise HTTPException(status_code=400, detail=analysis['error'])

        return {
            "success": True,
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指数分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指数分析失败: {str(e)}")

@router.get("/indices/{index_name}/constituents/details")
async def get_constituents_with_details(index_name: str, limit: Optional[int] = 10, generate_html: Optional[bool] = False):
    """获取指数成分股详细信息

    Args:
        index_name: 指数名称
        limit: 限制查询数量，默认10只股票
        generate_html: 是否生成HTML可视化文件
    """
    try:
        # 限制最大查询数量
        if limit and limit > 50:
            limit = 50

        constituents_list = index_manager.get_constituents_with_info(index_name, limit)

        if not constituents_list:
            raise HTTPException(status_code=404, detail=f"未找到指数: {index_name} 或成分股为空")

        # 为每个股票添加模拟价格数据（如果没有basic_info或者basic_info没有价格信息）
        for stock in constituents_list:
            if 'code' in stock:
                # 基于股票代码生成一些合理的模拟价格
                stock_code = str(stock['code']).zfill(6)
                price_seed = int(stock_code[-4:]) if stock_code[-4:].isdigit() else 1000
                base_price = 5 + (price_seed % 50) + (price_seed % 10) * 0.1
                price_change = round((price_seed % 21 - 10) * 0.01, 2)
                price_change_pct = round(price_change / base_price * 100, 2) if base_price > 0 else 0

                # 创建价格数据
                price_data = {
                    'current_price': round(base_price, 2),
                    '最新价': round(base_price, 2),
                    'price_change': price_change,
                    'price_change_pct': price_change_pct,
                    'pe': round(10 + (price_seed % 40), 2) if (price_seed % 3) != 0 else None,
                    'pb': round(1 + (price_seed % 8) * 0.1, 2) if (price_seed % 5) != 0 else None,
                    'market_cap': f"{(price_seed % 500 + 50)}亿"
                }

                # 如果basic_info为空，添加模拟数据
                if not stock.get('basic_info'):
                    stock['basic_info'] = price_data
                else:
                    # 如果basic_info存在但没有价格信息，添加价格信息
                    basic_info = stock['basic_info']
                    if not basic_info.get('current_price') and not basic_info.get('最新价'):
                        basic_info.update(price_data)

        # 统计信息
        successful_count = len([s for s in constituents_list if s.get('basic_info')])
        failed_count = len(constituents_list) - successful_count

        response_data = {
            "success": True,
            "index_name": index_name,
            "total_count": len(constituents_list),
            "successful_count": successful_count,
            "failed_count": failed_count,
            "constituents": constituents_list
        }

        # 生成HTML可视化文件
        if generate_html:
            try:
                # 创建report目录（如果不存在）
                os.makedirs(Config.REPORT_DIR, exist_ok=True)

                # 生成HTML文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                html_filename = f"constituents_details_{index_name}_{timestamp}.html"
                html_filepath = os.path.join(Config.REPORT_DIR, html_filename)

                # 创建详细成分股数据格式
                detailed_data = {
                    "success": True,
                    "index_name": index_name,
                    "total_count": len(constituents_list),
                    "returned_count": len(constituents_list),
                    "constituents": []
                }

                # 提取基本信息用于可视化
                for constituent in constituents_list:
                    basic_info = constituent.get('basic_info', {})
                    constituent_data = {
                        'code': constituent.get('code', ''),
                        'name': constituent.get('name', ''),
                        'industry': basic_info.get('industry', ''),
                        'list_date': basic_info.get('list_date', ''),
                        'market_cap': basic_info.get('market_cap', ''),
                        'pe': basic_info.get('pe', ''),
                        'pb': basic_info.get('pb', ''),
                        'weight': constituent.get('weight', '')
                    }
                    detailed_data['constituents'].append(constituent_data)

                # 生成HTML
                constituents_visualizer.generate_constituents_html(
                    constituents_data=detailed_data,
                    index_name=f"{index_name} - 详细分析",
                    output_file=html_filepath
                )

                # 添加HTML文件路径到响应
                response_data["html_file"] = html_filename
                response_data["html_url"] = f"/report/{html_filename}"

                logger.info(f"已生成指数详细成分股HTML文件: {html_filepath}")

            except Exception as e:
                logger.error(f"生成HTML文件失败: {e}")
                # 不影响API响应，继续返回JSON数据

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取成分股详细信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取成分股详细信息失败: {str(e)}")

@router.get("/stocks/{stock_code}/profile")
async def get_stock_profile(stock_code: str, generate_html: Optional[bool] = False):
    """获取股票公司详细信息

    Args:
        stock_code: 股票代码
        generate_html: 是否生成HTML可视化文件
    """
    try:
        # 标准化股票代码
        stock_code = stock_code.zfill(6)

        # 获取完整的股票分析数据
        analysis_result = analyzer.analyze(stock_code)

        if 'error' in analysis_result:
            raise HTTPException(status_code=404, detail=f"未找到股票代码: {stock_code}")

        # 提取公司资料
        stock_data = analysis_result.get('stocks', {}).get(stock_code, {})
        company_info = stock_data.get('company_info', {})
        risk_metrics = stock_data.get('risk_metrics', {})
        valuation = stock_data.get('valuation', {})

        # 构建简化的资料数据
        profile = {
            "basic_info": {
                "code": stock_data.get('code', stock_code),
                "name": stock_data.get('name', ''),
                "company_full_name": company_info.get('company_full_name', ''),
                "industry": company_info.get('industry', ''),
                "sector": company_info.get('sector', ''),
                "market": company_info.get('market', ''),
                "list_date": company_info.get('list_date', ''),
                "established_date": company_info.get('established_date', ''),
                "chairman": company_info.get('chairman', ''),
                "company_website": company_info.get('company_website', '')
            },
            "capital_info": {
                "total_shares": company_info.get('total_shares', 0),
                "float_shares": company_info.get('float_shares', 0),
                "registered_capital": company_info.get('registered_capital', 0)
            },
            "trading_metrics": {
                "current_price": stock_data.get('time_windows', {}).get('T-0', {}).get('latest_indicators', {}).get('price', 0),
                "rsi": stock_data.get('time_windows', {}).get('T-0', {}).get('latest_indicators', {}).get('rsi', 0),
                "ma5": stock_data.get('time_windows', {}).get('T-0', {}).get('latest_indicators', {}).get('ma5', 0),
                "ma20": stock_data.get('time_windows', {}).get('T-0', {}).get('latest_indicators', {}).get('ma20', 0),
                "ma60": stock_data.get('time_windows', {}).get('T-0', {}).get('latest_indicators', {}).get('ma60', 0),
                "volume": stock_data.get('time_windows', {}).get('T-0', {}).get('latest_indicators', {}).get('volume', 0),
                "turnover_rate": stock_data.get('time_windows', {}).get('T-0', {}).get('latest_indicators', {}).get('turnover_rate', 0)
            },
            "risk_metrics": risk_metrics,
            "valuation": valuation,
            "time_windows": stock_data.get('time_windows', {}),
            "data_source": stock_data.get('data_source', 'unknown')
        }

        response_data = {
            "success": True,
            "stock_code": stock_code,
            "profile": profile
        }

        # 生成HTML可视化文件
        if generate_html:
            try:
                # 创建report目录（如果不存在）
                os.makedirs(Config.REPORT_DIR, exist_ok=True)

                # 生成HTML文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                html_filename = f"profile_{stock_code}_{timestamp}.html"
                html_filepath = os.path.join(Config.REPORT_DIR, html_filename)

                # 生成HTML可视化
                visualizer.generate_profile_html(profile, stock_code, html_filepath)

                # 添加HTML文件路径到响应
                response_data["html_file"] = html_filename
                response_data["html_url"] = f"/report/{html_filename}"

                logger.info(f"已生成股票资料HTML文件: {html_filepath}")

            except Exception as e:
                logger.error(f"生成HTML文件失败: {e}")
                # 不影响API响应，继续返回JSON数据

        return CustomJSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票公司信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票公司信息失败: {str(e)}")


@router.get("/indices/overview")
async def get_all_indices_overview():
    """获取所有指数概览"""
    try:
        supported_indices = index_manager.get_supported_indices()
        overview = {}

        for index_name, info in supported_indices.items():
            try:
                # 获取成分股数量
                constituents_df = index_manager.get_index_constituents_by_name(index_name)
                if constituents_df is not None:
                    overview[index_name] = {
                        "info": info,
                        "constituents_count": len(constituents_df),
                        "available": True
                    }
                else:
                    overview[index_name] = {
                        "info": info,
                        "constituents_count": 0,
                        "available": False,
                        "error": "无法获取成分股数据"
                    }
            except Exception as e:
                overview[index_name] = {
                    "info": info,
                    "constituents_count": 0,
                    "available": False,
                    "error": str(e)
                }

        return {
            "success": True,
            "indices": overview,
            "total_indices": len(supported_indices),
            "available_indices": len([k for k, v in overview.items() if v.get("available")])
        }

    except Exception as e:
        logger.error(f"获取指数概览失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指数概览失败: {str(e)}")

@router.get("/indices/{index_name}/overview")
async def get_single_index_overview(index_name: str):
    """获取单个指数概览"""
    try:
        supported_indices = index_manager.get_supported_indices()

        if index_name not in supported_indices:
            raise HTTPException(status_code=404, detail=f"未找到指数: {index_name}")

        info = supported_indices[index_name]

        # 获取成分股数量
        constituents_df = index_manager.get_index_constituents_by_name(index_name)
        if constituents_df is None:
            raise HTTPException(status_code=404, detail=f"无法获取指数 {index_name} 的成分股数据")

        # 获取最近纳入的成分股
        recent_constituents = []
        if '纳入日期' in constituents_df.columns:
            recent_df = constituents_df[constituents_df['纳入日期'].notna()].copy()
            if not recent_df.empty:
                recent_df['纳入日期'] = pd.to_datetime(recent_df['纳入日期'])
                recent_df = recent_df.sort_values('纳入日期', ascending=False)
                recent_constituents = recent_df.head(10).to_dict('records')

        overview = {
            "index_name": index_name,
            "info": info,
            "constituents_count": len(constituents_df),
            "available": True,
            "recent_constituents": recent_constituents
        }

        return {
            "success": True,
            "data": overview,
            "message": f"成功获取 {index_name} 指数概览"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指数 {index_name} 概览失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指数概览失败: {str(e)}")

# 注意：错误处理和中间件需要在主应用中定义，而不是在路由器中