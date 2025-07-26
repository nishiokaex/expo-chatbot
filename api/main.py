"""
FastAPIチャットボットバックエンド
LangChainのTool機能を活用したエージェント実装
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from datetime import datetime

# ローカル開発用の設定
app = FastAPI(
    title="ChatBot API",
    description="LangChainを使用したチャットボットAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なドメインを指定
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

# チャットボットエージェントクラス
class ChatBotAgent:
    """
    LangChainのTool機能を使用したチャットボットエージェント
    """
    
    def __init__(self):
        self.tools = []
        self._initialize_tools()
    
    def _initialize_tools(self):
        """利用可能なツールを初期化"""
        from api.exchanging_tool import ExchangingTool
        
        # 為替ツールを追加
        exchanging_tool = ExchangingTool()
        self.tools.append(exchanging_tool)
        
        logger.info(f"初期化完了: {len(self.tools)}個のツールが利用可能")
    
    def process_message(self, message: str) -> str:
        """
        メッセージを処理して適切なレスポンスを返す
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            str: エージェントからのレスポンス
        """
        try:
            # シンプルなキーワードベースのルーティング
            message_lower = message.lower()
            
            # 為替関連のキーワードをチェック
            forex_keywords = ['為替', 'レート', 'usd', 'eur', 'jpy', '円', 'ドル', 'ユーロ']
            if any(keyword in message_lower for keyword in forex_keywords):
                # 為替ツールを使用
                from api.exchanging_tool import ExchangingTool
                exchanging_tool = ExchangingTool()
                return exchanging_tool.get_rates()
            
            # 挨拶関連
            greeting_keywords = ['こんにちは', 'おはよう', 'こんばんは', 'はじめまして', 'hello', 'hi']
            if any(keyword in message_lower for keyword in greeting_keywords):
                return "こんにちは！私は為替情報などをお手伝いできるチャットボットです。何かご質問はありますか？"
            
            # 機能説明
            help_keywords = ['ヘルプ', 'help', '機能', '何ができる', 'できること']
            if any(keyword in message_lower for keyword in help_keywords):
                return """私ができることをご紹介します：

📈 為替レート情報の取得
- 「為替レートを教えて」「USDJPYのレートは？」など

🔧 利用可能なツール：
- 為替情報取得ツール

その他ご質問があれば、お気軽にお聞きください！"""
            
            # デフォルトレスポンス
            return "申し訳ございませんが、その質問にはお答えできません。為替レートについて聞いてみてください。例：「今日の為替レートを教えて」"
            
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
            return "申し訳ございません。処理中にエラーが発生しました。"

# グローバルエージェントインスタンス
agent = ChatBotAgent()

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
        
        # エージェントでメッセージを処理
        response = agent.process_message(request.message)
        
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
    tools_info = []
    for tool in agent.tools:
        tools_info.append({
            "name": tool.__class__.__name__,
            "description": getattr(tool, 'description', '説明なし')
        })
    
    return {"tools": tools_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)