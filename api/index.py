"""
FastAPIチャットボットバックエンド
LangChainベースのGemini API実装
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import os
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from .exchanging_tool import get_exchange_rates, get_specific_exchange_rate

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

# LangChainベースのチャットボットクラス
class LangChainChatBot:
    """
    LangChainとGemini APIを使用したチャットボット
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY環境変数が設定されていません")
            self.llm = None
            self.agent_executor = None
        else:
            try:
                # ChatGoogleGenerativeAIでLLMを初期化
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=self.gemini_api_key,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # プロンプトテンプレートを作成
                self.prompt_template = ChatPromptTemplate.from_messages([
                    ("system", """あなたは親切で知識豊富な日本語チャットボットです。

このチャットボットは主に為替レート情報を提供することに特化しています。

為替、通貨、レートに関する質問の場合、以下の為替データを参照して回答してください：
{exchange_data}

為替関連以外の質問の場合は、丁寧にお断りし、為替関連の質問をお待ちしていることをお伝えください。

常に日本語で回答してください。"""),
                    ("human", "{message}")
                ])
                
                # チェーンを作成
                self.chain = self.prompt_template | self.llm | StrOutputParser()
                
                logger.info("LangChainChatBot初期化完了")
                
            except Exception as e:
                logger.error(f"LangChainChatBot初期化エラー: {e}")
                self.llm = None
                self.chain = None
    
    def _is_exchange_query(self, message: str) -> bool:
        """為替関連の質問かどうかを判定"""
        exchange_keywords = ["為替", "レート", "円", "ドル", "ユーロ", "ポンド", "豪ドル", "通貨", "USD", "EUR", "GBP", "AUD", "JPY"]
        return any(keyword in message for keyword in exchange_keywords)
    
    def process_message(self, message: str) -> str:
        """
        メッセージを処理して適切なレスポンスを返す
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            str: AIからのレスポンス
        """
        try:
            if not self.chain:
                return "申し訳ございません。システムの初期化中にエラーが発生しました。GEMINI_API_KEYが正しく設定されているか確認してください。"
            
            # 為替関連の質問かどうかを判定
            if self._is_exchange_query(message):
                # 為替データを取得
                exchange_data = get_exchange_rates.invoke({})
            else:
                # 為替以外の場合は空のデータ
                exchange_data = "為替データの取得は不要です。"
            
            # チェーンを実行してレスポンスを取得
            result = self.chain.invoke({
                "message": message,
                "exchange_data": exchange_data
            })
            
            return result
                
        except Exception as e:
            logger.error(f"LangChainメッセージ処理エラー: {e}")
            return "申し訳ございません。処理中にエラーが発生しました。しばらく時間をおいてから再度お試しください。"

# グローバルチャットボットインスタンス
chatbot = LangChainChatBot()

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
            "name": "get_exchange_rates",
            "description": "GMO Coin APIから主要通貨ペアの為替レート情報を取得"
        },
        {
            "name": "get_specific_exchange_rate", 
            "description": "GMO Coin APIから特定通貨ペアの為替レート情報を取得"
        },
        {
            "name": "ChatGoogleGenerativeAI",
            "description": "LangChain経由でGoogle Gemini APIによる自然言語処理"
        }
    ]
    
    return {"tools": tools_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)