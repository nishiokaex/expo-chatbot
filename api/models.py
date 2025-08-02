"""
Pydanticモデル定義
リクエスト/レスポンスの型定義
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """チャットリクエストモデル"""
    message: str


class ChatResponse(BaseModel):
    """チャットレスポンスモデル"""
    response: str
    timestamp: str


class ToolInfo(BaseModel):
    """ツール情報モデル"""
    name: str
    description: str


class ToolsResponse(BaseModel):
    """ツール一覧レスポンスモデル"""
    tools: list[ToolInfo]


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンスモデル"""
    message: str
    status: str