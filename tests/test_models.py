"""
Pydanticモデルのユニットテスト
リクエスト/レスポンスモデルのバリデーションテスト
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from api.models import (
    ChatRequest,
    ChatResponse,
    ToolInfo,
    ToolsResponse,
    HealthResponse
)


class TestChatRequest:
    """ChatRequestモデルのテスト"""

    def test_valid_chat_request(self):
        """正常なチャットリクエストの作成テスト"""
        request = ChatRequest(message="こんにちは")
        assert request.message == "こんにちは"

    def test_empty_message(self):
        """空のメッセージでの作成テスト"""
        request = ChatRequest(message="")
        assert request.message == ""

    def test_long_message(self):
        """長いメッセージでの作成テスト"""
        long_message = "a" * 10000
        request = ChatRequest(message=long_message)
        assert request.message == long_message

    def test_missing_message_field(self):
        """必須フィールドmessageが欠けている場合のテスト"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest()
        
        error = exc_info.value.errors()[0]
        assert error['type'] == 'missing'
        assert error['loc'] == ('message',)

    def test_invalid_message_type(self):
        """messageフィールドの型が不正な場合のテスト"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message=123)
        
        error = exc_info.value.errors()[0]
        assert error['type'] == 'string_type'


class TestChatResponse:
    """ChatResponseモデルのテスト"""

    def test_valid_chat_response(self):
        """正常なチャットレスポンスの作成テスト"""
        timestamp = datetime.now().isoformat()
        response = ChatResponse(
            response="テストレスポンス",
            timestamp=timestamp
        )
        assert response.response == "テストレスポンス"
        assert response.timestamp == timestamp

    def test_empty_response(self):
        """空のレスポンスでの作成テスト"""
        timestamp = datetime.now().isoformat()
        response = ChatResponse(
            response="",
            timestamp=timestamp
        )
        assert response.response == ""

    def test_missing_fields(self):
        """必須フィールドが欠けている場合のテスト"""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 2
        error_fields = [error['loc'][0] for error in errors]
        assert 'response' in error_fields
        assert 'timestamp' in error_fields

    def test_invalid_timestamp_format(self):
        """不正なタイムスタンプ形式でのテスト"""
        # 文字列として渡すので、Pydanticはバリデーションしない
        response = ChatResponse(
            response="テスト",
            timestamp="invalid-timestamp"
        )
        assert response.timestamp == "invalid-timestamp"


class TestToolInfo:
    """ToolInfoモデルのテスト"""

    def test_valid_tool_info(self):
        """正常なツール情報の作成テスト"""
        tool = ToolInfo(
            name="test_tool",
            description="テストツールの説明"
        )
        assert tool.name == "test_tool"
        assert tool.description == "テストツールの説明"

    def test_empty_fields(self):
        """空のフィールドでの作成テスト"""
        tool = ToolInfo(name="", description="")
        assert tool.name == ""
        assert tool.description == ""

    def test_missing_fields(self):
        """必須フィールドが欠けている場合のテスト"""
        with pytest.raises(ValidationError) as exc_info:
            ToolInfo()
        
        errors = exc_info.value.errors()
        assert len(errors) == 2
        error_fields = [error['loc'][0] for error in errors]
        assert 'name' in error_fields
        assert 'description' in error_fields


class TestToolsResponse:
    """ToolsResponseモデルのテスト"""

    def test_valid_tools_response(self):
        """正常なツール一覧レスポンスの作成テスト"""
        tools = [
            ToolInfo(name="tool1", description="ツール1"),
            ToolInfo(name="tool2", description="ツール2")
        ]
        response = ToolsResponse(tools=tools)
        assert len(response.tools) == 2
        assert response.tools[0].name == "tool1"
        assert response.tools[1].name == "tool2"

    def test_empty_tools_list(self):
        """空のツールリストでの作成テスト"""
        response = ToolsResponse(tools=[])
        assert len(response.tools) == 0
        assert response.tools == []

    def test_missing_tools_field(self):
        """必須フィールドtoolsが欠けている場合のテスト"""
        with pytest.raises(ValidationError) as exc_info:
            ToolsResponse()
        
        error = exc_info.value.errors()[0]
        assert error['type'] == 'missing'
        assert error['loc'] == ('tools',)

    def test_invalid_tools_item(self):
        """toolsリスト内に不正なアイテムがある場合のテスト"""
        with pytest.raises(ValidationError) as exc_info:
            ToolsResponse(tools=[{"invalid": "data"}])
        
        # ToolInfoのバリデーションエラーが発生する
        assert exc_info.value.errors()


class TestHealthResponse:
    """HealthResponseモデルのテスト"""

    def test_valid_health_response(self):
        """正常なヘルスレスポンスの作成テスト"""
        response = HealthResponse(
            message="API is running",
            status="ok"
        )
        assert response.message == "API is running"
        assert response.status == "ok"

    def test_different_status_values(self):
        """異なるステータス値でのテスト"""
        statuses = ["ok", "error", "warning", "maintenance"]
        for status in statuses:
            response = HealthResponse(
                message=f"Status is {status}",
                status=status
            )
            assert response.status == status

    def test_missing_fields(self):
        """必須フィールドが欠けている場合のテスト"""
        with pytest.raises(ValidationError) as exc_info:
            HealthResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 2
        error_fields = [error['loc'][0] for error in errors]
        assert 'message' in error_fields
        assert 'status' in error_fields

    def test_model_serialization(self):
        """モデルのシリアライゼーションテスト"""
        response = HealthResponse(
            message="Test message",
            status="test"
        )
        
        # dict()でシリアライズできることを確認
        data = response.model_dump()
        assert data == {
            "message": "Test message",
            "status": "test"
        }


class TestModelIntegration:
    """モデル間の統合テスト"""

    def test_tools_response_with_multiple_tools(self):
        """複数のツールを含むToolsResponseの作成テスト"""
        tools = [
            ToolInfo(
                name="get_exchange_rates",
                description="為替レート取得ツール"
            ),
            ToolInfo(
                name="get_specific_exchange_rate",
                description="特定通貨ペアの為替レート取得"
            ),
            ToolInfo(
                name="ChatGoogleGenerativeAI",
                description="Google Gemini API"
            )
        ]
        
        response = ToolsResponse(tools=tools)
        assert len(response.tools) == 3
        
        # 各ツールの属性を確認
        for i, tool in enumerate(response.tools):
            assert isinstance(tool, ToolInfo)
            assert tool.name
            assert tool.description

    def test_model_json_compatibility(self):
        """モデルのJSON互換性テスト"""
        import json
        
        # ChatRequestのテスト
        request = ChatRequest(message="テストメッセージ")
        request_json = json.loads(request.model_dump_json())
        assert request_json["message"] == "テストメッセージ"
        
        # ChatResponseのテスト
        response = ChatResponse(
            response="テストレスポンス",
            timestamp="2024-01-01T12:00:00"
        )
        response_json = json.loads(response.model_dump_json())
        assert response_json["response"] == "テストレスポンス"
        assert response_json["timestamp"] == "2024-01-01T12:00:00"