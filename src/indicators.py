"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """技术指标计算器"""

    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """简单移动平均线"""
        return data.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """指数移动平均线"""
        return data.ewm(span=window, adjust=False).mean()

    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """相对强弱指数"""
        delta = data.diff()
        # 使用更安全的比较方法避免numpy数组布尔值问题
        gain = (delta.where(delta.gt(0), 0)).rolling(window=window).mean()
        loss = (-delta.where(delta.lt(0), 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD指标"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, num_std: int = 2) -> Dict[str, pd.Series]:
        """布林带"""
        sma = TechnicalIndicators.sma(data, window)
        std = data.rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)

        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }

    @staticmethod
    def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series,
                            k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
        """随机振荡器"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()

        return {
            'k': k_percent,
            'd': d_percent
        }

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """平均真实范围"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        return atr

    @staticmethod
    def volume_sma(volume: pd.Series, window: int = 20) -> pd.Series:
        """成交量移动平均"""
        return volume.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def volume_ratio(volume: pd.Series, window: int = 20) -> pd.Series:
        """量比"""
        volume_ma = TechnicalIndicators.volume_sma(volume, window)
        return volume / volume_ma

    @staticmethod
    def price_change_pct(data: pd.Series, periods: int = 1) -> pd.Series:
        """价格变化百分比"""
        return data.pct_change(periods=periods) * 100

    @staticmethod
    def volatility(data: pd.Series, window: int = 20) -> pd.Series:
        """波动率（年化）"""
        returns = data.pct_change().dropna()
        volatility = returns.rolling(window=window).std() * np.sqrt(252)  # 年化波动率
        return volatility

    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, window: int = 252) -> pd.Series:
        """夏普比率"""
        excess_returns = returns - risk_free_rate / 252
        rolling_mean = excess_returns.rolling(window=window).mean() * 252
        rolling_std = excess_returns.rolling(window=window).std() * np.sqrt(252)
        sharpe = rolling_mean / rolling_std
        return sharpe

    @staticmethod
    def max_drawdown(data: pd.Series, window: int = 252) -> pd.Series:
        """最大回撤"""
        rolling_max = data.rolling(window=window, min_periods=1).max()
        drawdown = (data - rolling_max) / rolling_max
        max_drawdown = drawdown.rolling(window=window, min_periods=1).min()
        return max_drawdown

    @staticmethod
    def calculate_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算基础技术指标"""
        result_df = df.copy()

        try:
            # 移动平均线
            result_df['MA5'] = TechnicalIndicators.sma(df['close'], 5)
            result_df['MA10'] = TechnicalIndicators.sma(df['close'], 10)
            result_df['MA20'] = TechnicalIndicators.sma(df['close'], 20)
            result_df['MA60'] = TechnicalIndicators.sma(df['close'], 60)

            # EMA
            result_df['EMA12'] = TechnicalIndicators.ema(df['close'], 12)
            result_df['EMA26'] = TechnicalIndicators.ema(df['close'], 26)

            # RSI
            result_df['RSI'] = TechnicalIndicators.rsi(df['close'])

            # MACD
            macd_data = TechnicalIndicators.macd(df['close'])
            result_df['MACD'] = macd_data['macd']
            result_df['MACD_Signal'] = macd_data['signal']
            result_df['MACD_Histogram'] = macd_data['histogram']

            # 布林带
            bb_data = TechnicalIndicators.bollinger_bands(df['close'])
            result_df['BB_Upper'] = bb_data['upper']
            result_df['BB_Middle'] = bb_data['middle']
            result_df['BB_Lower'] = bb_data['lower']
            result_df['BB_Width'] = (bb_data['upper'] - bb_data['lower']) / bb_data['middle'] * 100
            result_df['BB_Position'] = (df['close'] - bb_data['lower']) / (bb_data['upper'] - bb_data['lower']) * 100

            # 随机振荡器
            stoch_data = TechnicalIndicators.stochastic_oscillator(df['high'], df['low'], df['close'])
            result_df['Stoch_K'] = stoch_data['k']
            result_df['Stoch_D'] = stoch_data['d']

            # ATR
            result_df['ATR'] = TechnicalIndicators.atr(df['high'], df['low'], df['close'])

            # 成交量指标
            if 'volume' in df.columns:
                result_df['Volume_MA20'] = TechnicalIndicators.volume_sma(df['volume'], 20)
                result_df['Volume_Ratio'] = TechnicalIndicators.volume_ratio(df['volume'], 20)

                # 成交额指标
                if 'amount' in df.columns:
                    result_df['Amount_MA20'] = TechnicalIndicators.volume_sma(df['amount'], 20)

            # 价格变化
            result_df['Price_Change_1d'] = TechnicalIndicators.price_change_pct(df['close'], 1)
            result_df['Price_Change_5d'] = TechnicalIndicators.price_change_pct(df['close'], 5)
            result_df['Price_Change_20d'] = TechnicalIndicators.price_change_pct(df['close'], 20)

            # 波动率
            result_df['Volatility_20d'] = TechnicalIndicators.volatility(df['close'], 20)

            # 最大回撤
            result_df['Max_Drawdown'] = TechnicalIndicators.max_drawdown(df['close'], 60)

            logger.info(f"成功计算 {len(result_df)} 行的技术指标")

        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return df

        return result_df

    @staticmethod
    def calculate_risk_metrics(df: pd.DataFrame, benchmark_return: float = 0.02) -> Dict:
        """计算风险指标"""
        try:
            returns = df['close'].pct_change().dropna()

            # 基础统计
            volatility = returns.std() * np.sqrt(252)  # 年化波动率
            mean_return = returns.mean() * 252  # 年化收益率

            # 夏普比率
            excess_returns = returns - benchmark_return / 252
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)

            # 最大回撤
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()

            # Calmar比率 (年化收益率 / 最大回撤)
            calmar_ratio = abs(mean_return / max_drawdown) if float(max_drawdown) != 0 else 0

            # VaR (95%置信度)
            var_95 = returns.quantile(0.05)

            # 偏度和峰度
            skewness = returns.skew()
            kurtosis = returns.kurtosis()

            return {
                'volatility': float(volatility),
                'annual_return': float(mean_return),
                'sharpe_ratio': float(sharpe_ratio),
                'max_drawdown': float(max_drawdown),
                'calmar_ratio': float(calmar_ratio),
                'var_95': float(var_95),
                'skewness': float(skewness),
                'kurtosis': float(kurtosis),
                'total_trading_days': len(returns),
                'positive_days': len(returns[returns > 0]),
                'negative_days': len(returns[returns < 0]),
                'win_rate': float(len(returns[returns > 0]) / len(returns)) if len(returns) > 0 else 0
            }

        except Exception as e:
            logger.error(f"计算风险指标失败: {e}")
            return {}

    @staticmethod
    def get_latest_indicators(df: pd.DataFrame) -> Dict:
        """获取最新的技术指标值"""
        if df.empty:
            return {}

        try:
            latest_row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) > 1 else latest_row

            indicators = {
                'price': float(latest_row['close']),
                'price_change': float(latest_row['close'] - prev_row['close']) if len(df) > 1 else 0,
                'price_change_pct': float(latest_row.get('Price_Change_1d', 0)),
                'volume': float(latest_row.get('volume', 0)),
                'volume_ratio': float(latest_row.get('Volume_Ratio', 1)),
                'turnover_rate': float(latest_row.get('turnover', 0)),
                'amplitude': float(latest_row.get('amplitude', 0)),
                'rsi': float(latest_row.get('RSI', 50)),
                'macd': float(latest_row.get('MACD', 0)),
                'macd_signal': float(latest_row.get('MACD_Signal', 0)),
                'macd_histogram': float(latest_row.get('MACD_Histogram', 0)),
                'bb_position': float(latest_row.get('BB_Position', 50)),
                'bb_width': float(latest_row.get('BB_Width', 0)),
                'stoch_k': float(latest_row.get('Stoch_K', 50)),
                'stoch_d': float(latest_row.get('Stoch_D', 50)),
                'atr': float(latest_row.get('ATR', 0)),
                'volatility_20d': float(latest_row.get('Volatility_20d', 0)),
                'ma5': float(latest_row.get('MA5', latest_row['close'])),
                'ma20': float(latest_row.get('MA20', latest_row['close'])),
                'ma60': float(latest_row.get('MA60', latest_row['close'])),
                'ema12': float(latest_row.get('EMA12', latest_row['close'])),
                'ema26': float(latest_row.get('EMA26', latest_row['close'])),
                'max_drawdown': float(latest_row.get('Max_Drawdown', 0))
            }

            return indicators

        except Exception as e:
            logger.error(f"获取最新技术指标失败: {e}")
            return {}