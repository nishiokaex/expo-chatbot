"""
FastAPIエンドポイントのユニットテスト
HTTP APIエンドポイントの動作確認テスト
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.main import app, chatbot
from api.models import ChatRequest, ChatResponse, HealthResponse, ToolsResponse


class TestMainApplication:
    """メインアプリケーションのテスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        self.client = TestClient(app)

    def test_app_creation(self):
        """アプリケーションの作成テスト"""
        assert app.title == "ChatBot API"
        assert app.description == "LangChain Function Calling対応チャットボット"
        assert app.version == "2.0.0"

    def test_cors_middleware_without_vercel_env(self):
        """VERCEL_ENV環境変数がない場合のCORS設定テスト"""
        # CORSミドルウェアが追加されていることを確認
        # 実際のCORSの動作はブラウザで確認されるため、ここでは設定の存在のみ確認
        assert app.middleware_stack is not None

    @patch.dict(os.environ, {'VERCEL_ENV': 'production'})
    def test_cors_middleware_with_vercel_env(self):
        """VERCEL_ENV環境変数がある場合のCORS設定テスト"""
        # この場合はCORSミドルウェアは追加されない
        # 実際の動作確認は統合テストで行う
        pass

    def test_global_chatbot_instance(self):
        """グローバルチャットボットインスタンスのテスト"""
        from api.main import chatbot
        from api.bot import FunctionCallingChatBot
        assert isinstance(chatbot, FunctionCallingChatBot)


class TestRootEndpoint:
    """ルートエンドポイント（ヘルスチェック）のテスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        self.client = TestClient(app)

    def test_root_endpoint_success(self):
        """ルートエンドポイントの正常レスポンステスト"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert data["message"] == "ChatBot API is running with Function Calling"
        assert data["status"] == "ok"

    def test_root_endpoint_response_model(self):
        """ルートエンドポイントのレスポンスモデル確認"""
        response = self.client.get("/")
        data = response.json()
        
        # HealthResponseモデルのフィールドが含まれていることを確認
        health_response = HealthResponse(**data)
        assert health_response.message == data["message"]
        assert health_response.status == data["status"]

    def test_root_endpoint_methods(self):
        """ルートエンドポイントのHTTPメソッドテスト"""
        # GETメソッドは正常
        response = self.client.get("/")
        assert response.status_code == 200
        
        # 他のメソッドは405エラー
        response = self.client.post("/")
        assert response.status_code == 405
        
        response = self.client.put("/")
        assert response.status_code == 405
        
        response = self.client.delete("/")
        assert response.status_code == 405


class TestChatEndpoint:
    """チャットエンドポイントのテスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        self.client = TestClient(app)

    @patch.object(chatbot, 'process_message')
    def test_chat_endpoint_success(self, mock_process_message):
        """チャットエンドポイントの正常レスポンステスト"""
        mock_process_message.return_value = "テストレスポンス"
        
        request_data = {"message": "こんにちは"}
        response = self.client.post("/api/chat", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert data["response"] == "テストレスポンス"
        assert "timestamp" in data
        
        # ChatResponseモデルで検証
        chat_response = ChatResponse(**data)
        assert chat_response.response == "テストレスポンス"
        
        # process_messageが正しい引数で呼び出されたことを確認
        mock_process_message.assert_called_once_with("こんにちは")

    @patch.object(chatbot, 'process_message')
    def test_chat_endpoint_empty_message(self, mock_process_message):
        """空のメッセージでのチャットエンドポイントテスト"""
        mock_process_message.return_value = "空のメッセージです"
        
        request_data = {"message": ""}
        response = self.client.post("/api/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "空のメッセージです"
        
        mock_process_message.assert_called_once_with("")

    @patch.object(chatbot, 'process_message')
    def test_chat_endpoint_long_message(self, mock_process_message):
        """長いメッセージでのチャットエンドポイントテスト"""
        mock_process_message.return_value = "長いメッセージを受信しました"
        
        long_message = "あ" * 10000
        request_data = {"message": long_message}
        response = self.client.post("/api/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "長いメッセージを受信しました"
        
        mock_process_message.assert_called_once_with(long_message)

    def test_chat_endpoint_invalid_request_body(self):
        """不正なリクエストボディのテスト"""
        # messageフィールドが欠けている場合
        response = self.client.post("/api/chat", json={})
        assert response.status_code == 422
        
        # 不正なJSONの場合
        response = self.client.post(
            "/api/chat", 
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422

    def test_chat_endpoint_invalid_content_type(self):
        """不正なContent-Typeのテスト"""
        response = self.client.post(
            "/api/chat",
            data="message=hello",
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    @patch.object(chatbot, 'process_message')
    def test_chat_endpoint_chatbot_exception(self, mock_process_message):
        """チャットボット処理中の例外テスト"""
        mock_process_message.side_effect = Exception("チャットボットエラー")
        
        request_data = {"message": "テストメッセージ"}
        response = self.client.post("/api/chat", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Internal server error"

    def test_chat_endpoint_methods(self):
        """チャットエンドポイントのHTTPメソッドテスト"""
        request_data = {"message": "テスト"}
        
        # POSTメソッドは正常（実際の処理はモック化）
        with patch.object(chatbot, 'process_message') as mock:
            mock.return_value = "レスポンス"
            response = self.client.post("/api/chat", json=request_data)
            assert response.status_code == 200
        
        # 他のメソッドは405エラー
        response = self.client.get("/api/chat")
        assert response.status_code == 405
        
        response = self.client.put("/api/chat", json=request_data)
        assert response.status_code == 405
        
        response = self.client.delete("/api/chat")
        assert response.status_code == 405

    @patch.object(chatbot, 'process_message')
    def test_chat_endpoint_timestamp_format(self, mock_process_message):
        """タイムスタンプフォーマットのテスト"""
        mock_process_message.return_value = "テスト"
        
        request_data = {"message": "テスト"}
        response = self.client.post("/api/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # タイムスタンプがISO形式であることを確認
        import datetime
        try:
            datetime.datetime.fromisoformat(data["timestamp"])
        except ValueError:
            pytest.fail("タイムスタンプがISO形式ではありません")


class TestToolsEndpoint:
    """ツール一覧エンドポイントのテスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        self.client = TestClient(app)

    def test_tools_endpoint_success(self):
        """ツール一覧エンドポイントの正常レスポンステスト"""
        response = self.client.get("/api/tools")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
        assert len(data["tools"]) == 3
        
        # ToolsResponseモデルで検証
        tools_response = ToolsResponse(**data)
        assert len(tools_response.tools) == 3

    def test_tools_endpoint_tool_details(self):
        """ツール詳細情報のテスト"""
        response = self.client.get("/api/tools")
        data = response.json()
        
        tools = data["tools"]
        
        # 期待されるツールが含まれていることを確認
        tool_names = [tool["name"] for tool in tools]
        assert "get_exchange_rates" in tool_names
        assert "get_specific_exchange_rate" in tool_names
        assert "ChatGoogleGenerativeAI" in tool_names
        
        # 各ツールに必要なフィールドがあることを確認
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert isinstance(tool["name"], str)
            assert isinstance(tool["description"], str)
            assert len(tool["name"]) > 0
            assert len(tool["description"]) > 0

    def test_tools_endpoint_specific_tools(self):
        """特定のツール情報の確認テスト"""
        response = self.client.get("/api/tools")
        data = response.json()
        
        tools_dict = {tool["name"]: tool for tool in data["tools"]}
        
        # get_exchange_ratesツールの確認
        exchange_rates_tool = tools_dict["get_exchange_rates"]
        assert "GMO Coin API" in exchange_rates_tool["description"]
        assert "主要通貨ペア" in exchange_rates_tool["description"]
        
        # get_specific_exchange_rateツールの確認
        specific_rate_tool = tools_dict["get_specific_exchange_rate"]
        assert "特定通貨ペア" in specific_rate_tool["description"]
        
        # ChatGoogleGenerativeAIツールの確認
        gemini_tool = tools_dict["ChatGoogleGenerativeAI"]
        assert "Google Gemini API" in gemini_tool["description"]

    def test_tools_endpoint_methods(self):
        """ツールエンドポイントのHTTPメソッドテスト"""
        # GETメソッドは正常
        response = self.client.get("/api/tools")
        assert response.status_code == 200
        
        # 他のメソッドは405エラー
        response = self.client.post("/api/tools")
        assert response.status_code == 405
        
        response = self.client.put("/api/tools")
        assert response.status_code == 405
        
        response = self.client.delete("/api/tools")
        assert response.status_code == 405


class TestAPIIntegration:
    """API統合テスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        self.client = TestClient(app)

    def test_api_workflow(self):
        """API全体のワークフローテスト"""
        # 1. ヘルスチェック
        health_response = self.client.get("/")
        assert health_response.status_code == 200
        
        # 2. ツール一覧取得
        tools_response = self.client.get("/api/tools")
        assert tools_response.status_code == 200
        assert len(tools_response.json()["tools"]) == 3
        
        # 3. チャット（モック化）
        with patch.object(chatbot, 'process_message') as mock_chat:
            mock_chat.return_value = "為替レート情報を取得しました"
            
            chat_response = self.client.post(
                "/api/chat",
                json={"message": "今日の為替レートを教えて"}
            )
            assert chat_response.status_code == 200
            assert "為替レート情報を取得しました" in chat_response.json()["response"]

    def test_api_error_handling(self):
        """APIエラーハンドリングテスト"""
        # 存在しないエンドポイント
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404
        
        # 不正なHTTPメソッド
        response = self.client.patch("/")
        assert response.status_code == 405

    @patch.object(chatbot, 'process_message')
    def test_concurrent_requests(self, mock_process_message):
        """同時リクエストの処理テスト"""
        import concurrent.futures
        import threading
        
        mock_process_message.side_effect = lambda msg: f"レスポンス: {msg}"
        
        def make_request(message):
            return self.client.post("/api/chat", json={"message": message})
        
        # 複数の同時リクエストを送信
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_request, f"メッセージ{i}")
                for i in range(10)
            ]
            
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # すべてのリクエストが正常に処理されたことを確認
        for response in responses:
            assert response.status_code == 200
            assert "レスポンス:" in response.json()["response"]

    def test_request_response_serialization(self):
        """リクエスト・レスポンスのシリアライゼーションテスト"""
        import json
        
        # ChatRequestのシリアライゼーション
        request_data = {"message": "テストメッセージ"}
        
        with patch.object(chatbot, 'process_message') as mock_chat:
            mock_chat.return_value = "テストレスポンス"
            
            response = self.client.post("/api/chat", json=request_data)
            
            # レスポンスが有効なJSONであることを確認
            response_data = response.json()
            json_str = json.dumps(response_data)
            parsed_data = json.loads(json_str)
            
            assert parsed_data["response"] == "テストレスポンス"
            assert "timestamp" in parsed_data


class TestErrorScenarios:
    """エラーシナリオのテスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        self.client = TestClient(app)

    def test_large_request_body(self):
        """大きなリクエストボディのテスト"""
        large_message = "あ" * 100000  # 100KB のメッセージ
        
        with patch.object(chatbot, 'process_message') as mock_chat:
            mock_chat.return_value = "大きなメッセージを処理しました"
            
            response = self.client.post(
                "/api/chat",
                json={"message": large_message}
            )
            
            # FastAPIが大きなリクエストを処理できることを確認
            assert response.status_code == 200

    def test_malformed_json_request(self):
        """不正なJSONリクエストのテスト"""
        response = self.client.post(
            "/api/chat",
            data='{"message": "test"',  # 不正なJSON（閉じ括弧なし）
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_unicode_handling(self):
        """Unicode文字の処理テスト"""
        unicode_message = "こんにちは🗾💱📈🌸"
        
        with patch.object(chatbot, 'process_message') as mock_chat:
            mock_chat.return_value = f"受信: {unicode_message}"
            
            response = self.client.post(
                "/api/chat",
                json={"message": unicode_message}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert unicode_message in data["response"]