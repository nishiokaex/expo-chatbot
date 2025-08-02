"""
為替レート取得ツール
GMOコインのAPIを使用して為替レートを取得
LangChainツール形式で実装
"""

import requests
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

class ExchangingTool:
    """
    為替レート取得ツール
    GMO Coin APIから為替データを取得
    """
    
    def __init__(self):
        self.api_url = "https://forex-api.coin.z.com/public/v1/ticker"
        self.description = "為替レート情報を取得するツール"
    
    def get_rates(self) -> str:
        """
        為替レートを取得して整形した文字列を返す
        
        Returns:
            str: 整形された為替レート情報
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 0:
                return "為替データの取得に失敗しました。"
            
            rates_data = data.get('data', [])
            if not rates_data:
                return "為替データが見つかりませんでした。"
            
            # 主要通貨ペアの表示
            major_pairs = ['USD_JPY', 'EUR_JPY', 'GBP_JPY', 'AUD_JPY', 'EUR_USD']
            
            result = "📈 現在の為替レート\n\n"
            
            for rate_info in rates_data:
                symbol = rate_info.get('symbol', '')
                if symbol in major_pairs:
                    bid = rate_info.get('bid', 'N/A')
                    ask = rate_info.get('ask', 'N/A')
                    spread = float(ask) - float(bid) if bid != 'N/A' and ask != 'N/A' else 'N/A'
                    
                    # 通貨ペア名を日本語表記に変換
                    pair_names = {
                        'USD_JPY': 'ドル/円',
                        'EUR_JPY': 'ユーロ/円', 
                        'GBP_JPY': 'ポンド/円',
                        'AUD_JPY': '豪ドル/円',
                        'EUR_USD': 'ユーロ/ドル'
                    }
                    
                    pair_name = pair_names.get(symbol, symbol)
                    
                    result += f"🔹 {pair_name} ({symbol})\n"
                    result += f"   買値: {bid}\n"
                    result += f"   売値: {ask}\n"
                    if spread != 'N/A':
                        result += f"   スプレッド: {spread:.4f}\n"
                    result += "\n"
            
            # タイムスタンプを追加
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result += f"⏰ 取得時刻: {current_time}\n"
            result += "\n※ レートは参考値です。実際の取引レートとは異なる場合があります。"
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"為替API呼び出しエラー: {e}")
            return "為替データの取得中にネットワークエラーが発生しました。しばらく時間をおいてから再度お試しください。"
        
        except Exception as e:
            logger.error(f"為替データ処理エラー: {e}")
            return "為替データの処理中にエラーが発生しました。"
    
    def get_specific_rate(self, currency_pair: str) -> str:
        """
        特定の通貨ペアのレートを取得
        
        Args:
            currency_pair: 取得したい通貨ペア（例: USD_JPY）
            
        Returns:
            str: 通貨ペアのレート情報
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 0:
                return f"{currency_pair}のデータ取得に失敗しました。"
            
            rates_data = data.get('data', [])
            
            # 指定された通貨ペアを検索
            for rate_info in rates_data:
                if rate_info.get('symbol', '') == currency_pair.upper():
                    bid = rate_info.get('bid', 'N/A')
                    ask = rate_info.get('ask', 'N/A')
                    
                    result = f"💱 {currency_pair}\n"
                    result += f"買値: {bid}\n"
                    result += f"売値: {ask}\n"
                    
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result += f"取得時刻: {current_time}"
                    
                    return result
            
            return f"通貨ペア '{currency_pair}' が見つかりませんでした。"
            
        except Exception as e:
            logger.error(f"特定レート取得エラー: {e}")
            return f"{currency_pair}のレート取得中にエラーが発生しました。"


# LangChainツール形式の為替レート取得関数
@tool
def get_exchange_rates() -> str:
    """
    GMO Coin APIから為替レート情報を取得します。
    主要通貨ペア（USD/JPY、EUR/JPY、GBP/JPY、AUD/JPY、EUR/USD）のレートを返します。
    
    Returns:
        str: 整形された為替レート情報
    """
    tool_instance = ExchangingTool()
    return tool_instance.get_rates()


@tool
def get_specific_exchange_rate(currency_pair: str) -> str:
    """
    特定の通貨ペアの為替レートを取得します。
    
    Args:
        currency_pair: 取得したい通貨ペア（例: USD_JPY, EUR_JPY）
        
    Returns:
        str: 指定された通貨ペアのレート情報
    """
    tool_instance = ExchangingTool()
    return tool_instance.get_specific_rate(currency_pair)