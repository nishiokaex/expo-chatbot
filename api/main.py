"""
FastAPIルーティング
エンドポイント定義とミドルウェア設定
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime
from api.models import ChatRequest, ChatResponse, ToolsResponse, HealthResponse, ToolInfo
from api.bot import FunctionCallingChatBot

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション設定
app = FastAPI(
    title="ChatBot API",
    description="LangChain Function Calling対応チャットボット",
    version="2.0.0"
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

# グローバルチャットボットインスタンス
chatbot = FunctionCallingChatBot()


@app.get("/", response_model=HealthResponse)
async def root():
    """ヘルスチェックエンドポイント"""
    return HealthResponse(
        message="ChatBot API is running with Function Calling", 
        status="ok"
    )


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


@app.get("/api/tools", response_model=ToolsResponse)
async def get_available_tools():
    """利用可能なツール一覧を取得"""
    tools_info = [
        ToolInfo(
            name="get_exchange_rates",
            description="GMO Coin APIから主要通貨ペアの為替レート情報を取得"
        ),
        ToolInfo(
            name="get_specific_exchange_rate", 
            description="GMO Coin APIから特定通貨ペアの為替レート情報を取得"
        ),
        ToolInfo(
            name="ChatGoogleGenerativeAI",
            description="LangChain経由でGoogle Gemini APIによる自然言語処理"
        )
    ]
    
    return ToolsResponse(tools=tools_info)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)