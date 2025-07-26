"""
FastAPIチャットボットバックエンド
軽量なGemini API直接呼び出し実装
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import os
from datetime import datetime

# ローカル開発用の設定
app = FastAPI(
    title="ChatBot API",
    description="軽量なGemini APIチャットボット",
    version="1.0.0"
)

# CORS設定（VERCEL_ENV環境変数が存在する場合は無効化）
if not os.getenv("VERCEL_ENV"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# リクエスト/レスポンスモデル
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str

# 軽量チャットボットクラス
class SimpleChatBot:
    """
    Gemini API直接呼び出しによる軽量チャットボット
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
        self.exchange_api_url = "https://forex-api.coin.z.com/public/v1/ticker"
        
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY環境変数が設定されていません")
        else:
            logger.info("SimpleChatBot初期化完了")
    
    def _is_exchange_query(self, message: str) -> bool:
        """為替関連の質問かどうかを判定"""
        exchange_keywords = ["為替", "レート", "円", "ドル", "ユーロ", "ポンド", "豪ドル", "通貨", "USD", "EUR", "GBP", "AUD", "JPY"]
        return any(keyword in message for keyword in exchange_keywords)
    
    def _get_exchange_rates(self) -> str:
        """為替レートを取得して整形"""
        try:
            response = requests.get(self.exchange_api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 0:
                return "為替データの取得に失敗しました。"
            
            rates_data = data.get('data', [])
            if not rates_data:
                return "為替データが見つかりませんでした。"
            
            # 主要通貨ペアの表示
            major_pairs = ['USD_JPY', 'EUR_JPY', 'GBP_JPY', 'AUD_JPY', 'EUR_USD']
            
            result = "📈 現在の為替レート\\n\\n"
            
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
                    
                    result += f"🔹 {pair_name} ({symbol})\\n"
                    result += f"   買値: {bid}\\n"
                    result += f"   売値: {ask}\\n"
                    if spread != 'N/A':
                        result += f"   スプレッド: {spread:.4f}\\n"
                    result += "\\n"
            
            # タイムスタンプを追加
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result += f"⏰ 取得時刻: {current_time}\\n"
            result += "\\n※ レートは参考値です。実際の取引レートとは異なる場合があります。"
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"為替API呼び出しエラー: {e}")
            return "為替データの取得中にネットワークエラーが発生しました。しばらく時間をおいてから再度お試しください。"
        
        except Exception as e:
            logger.error(f"為替データ処理エラー: {e}")
            return "為替データの処理中にエラーが発生しました。"
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Gemini API直接呼び出し"""
        try:
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                return content
            else:
                return "レスポンスの解析に失敗しました。"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API呼び出しエラー: {e}")
            return "AIサービスとの通信でエラーが発生しました。しばらく時間をおいてから再度お試しください。"
        
        except Exception as e:
            logger.error(f"Gemini API処理エラー: {e}")
            return "AI処理中にエラーが発生しました。"
    
    def process_message(self, message: str) -> str:
        """
        メッセージを処理して適切なレスポンスを返す
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            str: AIからのレスポンス
        """
        try:
            if not self.gemini_api_key:
                return "申し訳ございません。システムの初期化中にエラーが発生しました。GEMINI_API_KEYが正しく設定されているか確認してください。"
            
            # 為替関連の質問かどうかを判定
            if self._is_exchange_query(message):
                # 為替データを取得
                exchange_data = self._get_exchange_rates()
                
                # 為替データを含むプロンプトを作成
                system_prompt = """あなたは親切で知識豊富な日本語チャットボットです。

以下の為替データを参照して、ユーザーの質問に答えてください：

{exchange_data}

ユーザーの質問に対して、上記の為替データを使って適切に回答してください。
為替レートについて詳しく説明し、必要に応じて投資のアドバイスも含めてください。"""
                
                prompt = system_prompt.format(exchange_data=exchange_data) + f"\\n\\nユーザーの質問: {message}"
                
            else:
                # 為替以外の質問
                system_prompt = """あなたは親切で知識豊富な日本語チャットボットです。

このチャットボットは主に為替レート情報を提供することに特化しています。
為替、通貨、レートに関する質問以外については、丁寧にお断りし、為替関連の質問をお待ちしていることをお伝えください。"""
                
                prompt = f"{system_prompt}\\n\\nユーザーの質問: {message}"
            
            # Gemini APIを呼び出し
            return self._call_gemini_api(prompt)
            
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
            return "申し訳ございません。処理中にエラーが発生しました。しばらく時間をおいてから再度お試しください。"

# グローバルチャットボットインスタンス
chatbot = SimpleChatBot()

@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {"message": "ChatBot API is running", "status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    チャットエンドポイント
    
    Args:
        request: チャットリクエスト
        
    Returns:
        ChatResponse: チャットレスポンス
    """
    try:
        logger.info(f"受信メッセージ: {request.message}")
        
        # チャットボットでメッセージを処理
        response = chatbot.process_message(request.message)
        
        logger.info(f"送信レスポンス: {response}")
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"チャット処理エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/tools")
async def get_available_tools():
    """利用可能なツール一覧を取得"""
    tools_info = [
        {
            "name": "ExchangeRateTool",
            "description": "GMO Coin APIから為替レート情報を取得"
        },
        {
            "name": "GeminiAI",
            "description": "Google Gemini APIによる自然言語処理"
        }
    ]
    
    return {"tools": tools_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)