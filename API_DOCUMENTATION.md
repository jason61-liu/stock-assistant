# A股行情可视化服务 API 文档

## 概述

这是一个零配置的A股股票分析可视化服务，提供全面的股票数据获取、技术指标计算、公司信息展示和交互式图表生成功能。

**服务地址**: `http://localhost:8000`
**API版本**: v1.0.0
**文档地址**: `http://localhost:8000/docs`

---

## 核心功能特性

### 📊 数据分析能力
- **多时间窗口分析**: 支持 T-0, T-3, T-7, T-30, T-90, T-180 共6个时间维度
- **30+技术指标**: 价格、成交量、估值、风险等全方位指标
- **智能数据源**: 自动切换 akShare、新浪财经、腾讯财经等多个数据源
- **模拟数据**: 网络故障时自动生成高质量演示数据

### 🏢 公司信息展示
- **基本信息**: 公司名称、全称、行业分类、所属板块
- **上市信息**: 上市市场、纳入日期、上市日期、成立日期
- **股本结构**: 总股本、流通股本、注册资本
- **管理层**: 董事长信息、公司官网

### 📈 可视化功能
- **交互式图表**: 基于Plotly的动态图表展示
- **HTML报告**: 完整的分析报告生成
- **热力图**: 多股票指标对比分析
- **风险收益散点图**: 投资组合可视化

### 🚀 高级功能
- **指数成分股**: 支持中证100、中证200、沪深300、中证500
- **批量分析**: 同时处理多只股票
- **智能缓存**: 6小时缓存机制，提升响应速度
- **数据源标注**: 明确标注数据来源和可信度

---

## API 接口详情

### 基础信息接口

#### 1. 服务信息
```http
GET /
```
获取API基本信息和可用端点列表

**响应示例**:
```json
{
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
```

#### 2. 健康检查
```http
GET /health
```
检查服务运行状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-07T00:36:00.000Z",
  "cache_status": "active"
}
```

#### 3. 支持的指标
```http
GET /indicators
```
获取所有支持的技术指标分类

**响应示例**:
```json
{
  "price_indicators": [
    "开高低收", "均价", "涨跌幅", "振幅",
    "MA5", "MA10", "MA20", "MA60", "EMA12", "EMA26"
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
```

---

### 核心分析接口

#### 4. 股票分析（核心接口）
```http
GET /api/v1/stocks/{input}
```
分析单只股票或指数

**路径参数**:
- `input`: 输入内容，支持：
  - **指数名称**: `上证100`, `SSE100`, `中证300`, `CSI300`
  - **股票代码**: `000001`, `600519` (6位数字)
  - **多个股票**: `000001,600519,000858` (逗号分隔)

**查询参数**:
- `force_refresh` (可选): 是否强制刷新缓存，默认`false`

**请求示例**:
```bash
# 分析单只股票
curl "http://localhost:8000/api/v1/stocks/000001"

# 分析指数成分股
curl "http://localhost:8000/api/v1/stocks/CSI300"

# 分析多只股票
curl "http://localhost:8000/api/v1/stocks/000001,600519"
```

**响应示例**:
```json
{
  "success": true,
  "message": "分析完成",
  "data": {
    "input": "000001",
    "mode": "stock",
    "stock_count": 1,
    "timestamp": "2025-12-07T00:36:00.000Z",
    "stocks": {
      "000001": {
        "code": "000001",
        "name": "平安银行",
        "data_source": "mock",
        "company_info": {
          "company_full_name": "平安银行股份有限公司",
          "industry": "银行",
          "sector": "金融",
          "market": "深交所",
          "inclusion_date": "2024-01-19",
          "list_date": "2024-01-19",
          "established_date": "1987-12-22",
          "chairman": "谢永林",
          "company_website": "http://bank.pingan.com",
          "total_shares": 1940591819804,
          "float_shares": 19405919804,
          "registered_capital": 1940591819804
        },
        "time_windows": {
          "T-0": {
            "data_points": 128,
            "latest_indicators": {
              "price": 15.23,
              "change_pct": 2.15,
              "volume": 25000000,
              "rsi": 65.4,
              "ma20": 14.89
            }
          }
        },
        "risk_metrics": {
          "annual_return": 0.1637,
          "volatility": 0.3574,
          "sharpe_ratio": 0.40,
          "max_drawdown": -0.2574
        }
      }
    }
  },
  "json_url": "/static/analysis_20251207_003426.json",
  "chart_url": "/static/charts_20251207_003426.html"
}
```

#### 5. 股票基本信息
```http
GET /api/v1/stocks/{input}/info
```
获取股票或指数的基本信息（不含详细分析）

**响应示例**:
```json
{
  "success": true,
  "input": "000001",
  "stocks": {
    "000001": "平安银行"
  },
  "count": 1
}
```

#### 6. 批量分析
```http
POST /api/v1/batch
```
批量分析多个股票或指数

**请求体**:
```json
{
  "inputs": ["000001", "600519", "CSI300"],
  "force_refresh": false
}
```

**限制**: 最多支持10个输入项

---

### 指数相关接口

#### 7. 支持的指数
```http
GET /api/v1/indices/supported
```
获取所有支持的指数列表

**响应示例**:
```json
{
  "indices": [
    {
      "code": "000903",
      "name": "中证100",
      "sector": "大盘蓝筹",
      "description": "沪深300中规模最大的100只股票"
    },
    {
      "code": "000905",
      "name": "中证300",
      "sector": "核心指数",
      "description": "沪深两市流动性最好的300只股票"
    }
  ]
}
```

#### 8. 指数成分股
```http
GET /api/v1/indices/{index_name}/constituents
```
获取指定指数的成分股信息

**路径参数**:
- `index_name`: 指数名称，如 `CSI300`, `SSE100`

**查询参数**:
- `limit` (可选): 返回数量限制，默认50
- `generate_html` (可选): 是否生成HTML报告，默认false

**响应示例**:
```json
{
  "success": true,
  "index_name": "CSI300",
  "index_code": "000905",
  "total_constituents": 300,
  "returned_count": 50,
  "data_source": "akshare",
  "generation_time": "2025-12-07T00:36:00.000Z",
  "constituents": [
    {
      "code": "000001",
      "name": "平安银行",
      "weight": 0.85,
      "industry": "银行",
      "market": "深交所"
    }
  ],
  "statistics": {
    "industry_distribution": {...},
    "market_distribution": {...}
  }
}
```

#### 9. 指数成分股HTML报告
```http
GET /api/v1/indices/{index_name}/constituents?generate_html=true
```
生成指数成分股的可视化HTML报告

**返回**: 包含图表、表格、统计信息的完整HTML页面

#### 10. 指数分析
```http
GET /api/v1/indices/{index_name}/analysis
```
对整个指数进行综合分析

**响应**: 包含所有成分股的分析结果、行业分布、风险指标等

#### 11. 指数概览
```http
GET /api/v1/indices/overview
```
获取所有支持指数的概览信息

---

### 股票搜索和详情接口

#### 12. 股票搜索
```http
GET /api/v1/stocks/search/{keyword}
```
根据关键词搜索股票

**路径参数**:
- `keyword`: 搜索关键词（股票名称或代码）

**响应示例**:
```json
{
  "success": true,
  "keyword": "平安",
  "results": [
    {
      "code": "000001",
      "name": "平安银行",
      "market": "深交所",
      "industry": "银行"
    }
  ]
}
```

#### 13. 股票资料
```http
GET /api/v1/stocks/{stock_code}/profile
```
获取单只股票的详细资料

---

### 缓存管理接口

#### 14. 清理缓存
```http
GET /api/v1/cache/clear
```
清理所有缓存数据

#### 15. 缓存状态
```http
GET /api/v1/cache/status
```
获取缓存使用状态

---

### 文件导出接口

#### 16. 文件访问
```http
GET /api/v1/static/{file_path:path}
```
访问生成的JSON或HTML文件

#### 17. 数据导出
```http
GET /api/v1/export/{format}/{input:path}
```
导出指定格式的分析数据

**路径参数**:
- `format`: 导出格式 (`json`, `csv`, `excel`)
- `input`: 分析目标

---

## 数据格式说明

### 时间窗口定义

| 窗口代码 | 时间范围 | 用途 |
|---------|---------|------|
| T-0 | 当日数据 | 最新价格和指标 |
| T-3 | 近3个交易日 | 短期趋势分析 |
| T-7 | 近7个交易日 | 周级别分析 |
| T-30 | 近30个交易日 | 月度分析 |
| T-90 | 近90个交易日 | 季度分析 |
| T-180 | 近180个交易日 | 半年分析 |

### 数据源标识

| 数据源代码 | 说明 | 可信度 |
|-----------|------|--------|
| `akshare_primary` | akShare主要数据源 | 高 |
| `akshare_alternative` | akShare备用数据源 | 高 |
| `sina` | 新浪财经 | 中 |
| `tencent` | 腾讯财经 | 中 |
| `mock` | 模拟数据（演示） | 低 |
| `unknown` | 未知数据源 | 低 |

### 行业分类

| 一级分类 | 包含行业 |
|---------|---------|
| 科技 | 软件服务、互联网、电子信息、通信设备、半导体 |
| 金融 | 银行、保险、证券、信托、基金 |
| 制造 | 机械设备、化工、钢铁、有色金属、汽车 |
| 消费 | 白酒、食品饮料、纺织服装、家电、零售 |
| 医药 | 化学制药、中药、生物制品、医疗器械 |
| 能源 | 石油开采、煤炭开采、电力、新能源 |
| 地产 | 房地产开发、建筑装饰、园林工程 |
| 交通 | 航空、港口、高速公路、铁路运输 |

---

## 使用示例

### 1. 基础股票分析
```bash
# 分析平安银行
curl "http://localhost:8000/api/v1/stocks/000001"

# 访问生成的HTML报告
curl "http://localhost:8000/static/charts_20251207_003426.html"
```

### 2. 指数成分股分析
```bash
# 获取沪深300成分股
curl "http://localhost:8000/api/v1/indices/CSI300/constituents?limit=100"

# 生成成分股HTML报告
curl "http://localhost:8000/api/v1/indices/CSI300/constituents?generate_html=true"
```

### 3. 批量分析
```bash
# 批量分析多只股票
curl -X POST "http://localhost:8000/api/v1/batch" \
  -H "Content-Type: application/json" \
  -d '{"inputs": ["000001", "600519", "000858"]}'
```

### 4. 搜索功能
```bash
# 搜索银行相关股票
curl "http://localhost:8000/api/v1/stocks/search/银行"
```

---

## 技术指标说明

### 价格指标
- **MA (移动平均线)**: 5日、10日、20日、60日移动平均
- **EMA (指数移动平均)**: 12日、26日指数移动平均
- **涨跌幅**: 当日价格变动的百分比
- **振幅**: 当日最高价与最低价的波动幅度

### 技术指标
- **RSI (相对强弱指数)**: 衡量价格变动的速度和变化幅度
- **MACD (异同移动平均线)**: 趋势跟踪动量指标
- **布林带**: 价格通道指标，包含上轨、中轨、下轨
- **随机振荡器**: 超买超卖指标

### 风险指标
- **波动率**: 价格变动的统计度量
- **夏普比率**: 风险调整后收益指标
- **最大回撤**: 从峰值到谷值的最大跌幅
- **VaR (风险价值)**: 在置信水平下的潜在最大损失

---

## 错误处理

### HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器内部错误

### 错误响应格式
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": "详细错误信息"
}
```

### 常见错误
- `STOCK_NOT_FOUND`: 找不到指定股票
- `INVALID_INPUT`: 输入格式错误
- `DATA_SOURCE_ERROR`: 数据源访问失败
- `CACHE_ERROR`: 缓存操作失败

---

## 性能优化

### 缓存机制
- **缓存时长**: 6小时
- **缓存范围**: 分析结果、股票基本信息、指数成分股
- **自动清理**: 定期清理过期缓存

### 限流策略
- **请求频率**: 限制每分钟最多60次请求
- **并发限制**: 同时处理的最大分析任务数
- **批量限制**: 批量分析最多10个输入

### 数据源策略
1. **优先级**: akShare主要 → akShare备用 → 新浪财经 → 腾讯财经 → 模拟数据
2. **故障切换**: 自动检测数据源可用性并切换
3. **数据验证**: 对获取的数据进行完整性验证

---

## 部署说明

### 环境要求
- Python 3.8+
- 依赖包: `fastapi`, `uvicorn`, `akshare`, `pandas`, `plotly`, `numpy`

### 启动服务
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 配置说明
- **端口**: 默认8000，可通过环境变量`PORT`修改
- **缓存目录**: `cache/`
- **静态文件**: `static/`
- **日志级别**: INFO，可通过环境变量`LOG_LEVEL`修改

---

## 更新日志

### v1.0.0 (2025-12-07)
- ✅ 实现基础股票分析功能
- ✅ 支持多时间窗口技术指标计算
- ✅ 添加指数成分股查询和分析
- ✅ 集成公司信息展示功能
- ✅ 实现交互式HTML报告生成
- ✅ 添加数据源标注和透明度
- ✅ 支持批量分析和搜索功能
- ✅ 完善缓存机制和错误处理

---

## 联系方式

如有问题或建议，请通过以下方式联系：
- 技术支持: 查看 `main.py` 中的日志输出
- 错误报告: 检查服务器控制台日志
- 功能建议: 可通过API接口的`/docs`页面提交反馈

---

*最后更新时间: 2025-12-07*