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
from api.vector_store import vector_store_service
from pydantic import BaseModel
from typing import Optional, List

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

# リクエストモデル
class SetUrlRequest(BaseModel):
    urls: List[str]

class SetUrlResponse(BaseModel):
    success: bool
    message: str
    urls: Optional[List[str]] = None
    failed_urls: Optional[List[str]] = None

class ClearVectorStoreResponse(BaseModel):
    success: bool
    message: str


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


@app.post("/api/set-url", response_model=SetUrlResponse)
async def set_url(request: SetUrlRequest):
    """
    ベクトルストア用複数URLを設定し、ドキュメントを読み込み
    
    Args:
        request: URL設定リクエスト（複数URL対応）
        
    Returns:
        SetUrlResponse: 設定結果
    """
    try:
        logger.info(f"複数URL設定開始: {len(request.urls)}個のURL")
        
        # URLバリデーション
        invalid_urls = []
        for url in request.urls:
            if not url.startswith(('http://', 'https://')):
                invalid_urls.append(url)
        
        if invalid_urls:
            return SetUrlResponse(
                success=False,
                message=f"無効なURLがあります。http://またはhttps://で始まるURLを指定してください: {', '.join(invalid_urls)}"
            )
        
        # ベクトルストアが初期化されている場合はクリア
        if vector_store_service.is_initialized():
            vector_store_service.clear_vector_store()
            logger.info("既存のベクトルストアをクリアしました")
        
        # URLからドキュメントを読み込みベクトルストアを構築
        successful_urls, failed_urls = vector_store_service.load_and_store_documents(request.urls)
        
        if successful_urls:
            if failed_urls:
                return SetUrlResponse(
                    success=True,
                    message=f"{len(successful_urls)}個のURLの読み込みが完了しました。{len(failed_urls)}個のURLで失敗がありました。",
                    urls=successful_urls,
                    failed_urls=failed_urls
                )
            else:
                return SetUrlResponse(
                    success=True,
                    message=f"全{len(successful_urls)}個のURLの読み込みが完了しました。",
                    urls=successful_urls
                )
        else:
            return SetUrlResponse(
                success=False,
                message="全てのURLでドキュメントの読み込みに失敗しました。URLが正しいか確認してください。",
                failed_urls=failed_urls
            )
        
    except Exception as e:
        logger.error(f"URL設定エラー: {e}")
        return SetUrlResponse(
            success=False,
            message="URL設定中にエラーが発生しました。"
        )


@app.post("/api/clear-vectorstore", response_model=ClearVectorStoreResponse)
async def clear_vectorstore():
    """
    ベクトルストアをクリア
    
    Returns:
        ClearVectorStoreResponse: クリア結果
    """
    try:
        logger.info("ベクトルストアクリア開始")
        
        success = vector_store_service.clear_vector_store()
        
        if success:
            return ClearVectorStoreResponse(
                success=True,
                message="ベクトルストアをクリアしました。"
            )
        else:
            return ClearVectorStoreResponse(
                success=False,
                message="ベクトルストアのクリアに失敗しました。"
            )
        
    except Exception as e:
        logger.error(f"ベクトルストアクリアエラー: {e}")
        return ClearVectorStoreResponse(
            success=False,
            message="ベクトルストアクリア中にエラーが発生しました。"
        )


@app.get("/api/vectorstore-status")
async def get_vectorstore_status():
    """
    ベクトルストアの状態を取得
    
    Returns:
        dict: ベクトルストアの状態情報
    """
    try:
        is_initialized = vector_store_service.is_initialized()
        current_url = vector_store_service.get_current_url()
        
        return {
            "initialized": is_initialized,
            "current_url": current_url,
            "status": "ready" if is_initialized else "not_initialized"
        }
        
    except Exception as e:
        logger.error(f"ベクトルストア状態取得エラー: {e}")
        return {
            "initialized": False,
            "current_url": None,
            "status": "error"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)