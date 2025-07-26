"""
FastAPIチャットボットバックエンド
LangChainのTool機能を活用したエージェント実装
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import os
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

# ローカル開発用の設定
app = FastAPI(
    title="ChatBot API",
    description="LangChainを使用したチャットボットAPI",
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

# チャットボットエージェントクラス
class ChatBotAgent:
    """
    LangChainのTool機能とGemini APIを使用したチャットボットエージェント
    """
    
    def __init__(self):
        self.tools = []
        self.llm = None
        self.agent_executor = None
        self._initialize_tools()
        self._initialize_llm()
        self._initialize_agent()
    
    def _initialize_tools(self):
        """利用可能なツールを初期化"""
        from api.exchanging_tool import ExchangingTool
        
        # 為替ツールを追加
        exchanging_tool = ExchangingTool()
        self.tools.append(exchanging_tool)
        
        logger.info(f"初期化完了: {len(self.tools)}個のツールが利用可能")
    
    def _initialize_llm(self):
        """Gemini LLMを初期化"""
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                logger.error("GEMINI_API_KEY環境変数が設定されていません")
                return
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=gemini_api_key,
                temperature=0.7
            )
            logger.info("Gemini LLM初期化完了")
        except Exception as e:
            logger.error(f"Gemini LLM初期化エラー: {e}")
    
    def _initialize_agent(self):
        """LangChainエージェントを初期化"""
        if not self.llm:
            logger.error("LLMが初期化されていないため、エージェントを作成できません")
            return
        
        try:
            # システムプロンプトの設定
            system_prompt = """あなたは親切で知識豊富な日本語チャットボットです。
            
以下のツールを使用してユーザーの質問に答えてください：
- exchange_rate_tool: 為替レート情報を取得する

ユーザーが為替、通貨、レートについて質問した場合は、必ず為替ツールを使用してください。
その他の質問には、丁寧に対応できない旨を回答してください。"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            # エージェントの作成
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            logger.info("LangChainエージェント初期化完了")
        except Exception as e:
            logger.error(f"エージェント初期化エラー: {e}")
    
    def process_message(self, message: str) -> str:
        """
        メッセージを処理して適切なレスポンスを返す
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            str: エージェントからのレスポンス
        """
        try:
            if not self.agent_executor:
                return "申し訳ございません。システムの初期化中にエラーが発生しました。GEMINI_API_KEYが正しく設定されているか確認してください。"
            
            # LangChainエージェントでメッセージを処理
            response = self.agent_executor.invoke({"input": message})
            return response["output"]
            
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
            return "申し訳ございません。処理中にエラーが発生しました。しばらく時間をおいてから再度お試しください。"

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