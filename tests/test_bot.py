"""
チャットボットクラスのユニットテスト
LangChain Function Callingとツール実行のテスト
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch, call
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from api.bot import FunctionCallingChatBot


class TestFunctionCallingChatBotInit:
    """FunctionCallingChatBotの初期化テスト"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'})
    @patch('api.bot.ChatGoogleGenerativeAI')
    def test_init_with_api_key(self, mock_chat_google):
        """APIキーがある場合の初期化テスト"""
        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        mock_chat_google.return_value = mock_llm
        mock_llm.bind_tools.return_value = mock_llm_with_tools
        
        bot = FunctionCallingChatBot()
        
        # ChatGoogleGenerativeAIが正しいパラメータで呼び出されたことを確認
        mock_chat_google.assert_called_once_with(
            model="gemini-1.5-flash",
            google_api_key="test-api-key",
            temperature=0.7,
            max_tokens=1000
        )
        
        # bind_toolsが呼び出されたことを確認
        mock_llm.bind_tools.assert_called_once()
        
        assert bot.llm is mock_llm
        assert bot.llm_with_tools is mock_llm_with_tools
        assert bot.gemini_api_key == "test-api-key"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key(self):
        """APIキーがない場合の初期化テスト"""
        bot = FunctionCallingChatBot()
        
        assert bot.gemini_api_key is None
        assert bot.llm is None
        assert bot.llm_with_tools is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'})
    @patch('api.bot.ChatGoogleGenerativeAI')
    def test_init_with_exception(self, mock_chat_google):
        """初期化中に例外が発生した場合のテスト"""
        mock_chat_google.side_effect = Exception("API initialization error")
        
        bot = FunctionCallingChatBot()
        
        assert bot.llm is None
        assert bot.llm_with_tools is None


class TestFunctionCallingChatBotExecuteTool:
    """ツール実行メソッドのテスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch('api.bot.ChatGoogleGenerativeAI'):
                self.bot = FunctionCallingChatBot()

    @patch('api.bot.get_exchange_rates')
    def test_execute_get_exchange_rates(self, mock_get_rates):
        """get_exchange_ratesツールの実行テスト"""
        mock_get_rates.invoke.return_value = "モック為替レート情報"
        
        tool_call = {
            'name': 'get_exchange_rates',
            'args': {}
        }
        
        result = self.bot._execute_tool(tool_call)
        
        mock_get_rates.invoke.assert_called_once_with({})
        assert result == "モック為替レート情報"

    @patch('api.bot.get_specific_exchange_rate')
    def test_execute_get_specific_exchange_rate(self, mock_get_specific_rate):
        """get_specific_exchange_rateツールの実行テスト"""
        mock_get_specific_rate.invoke.return_value = "モック特定為替レート情報"
        
        tool_call = {
            'name': 'get_specific_exchange_rate',
            'args': {'currency_pair': 'USD_JPY'}
        }
        
        result = self.bot._execute_tool(tool_call)
        
        mock_get_specific_rate.invoke.assert_called_once_with({'currency_pair': 'USD_JPY'})
        assert result == "モック特定為替レート情報"

    def test_execute_unknown_tool(self):
        """未知のツールの実行テスト"""
        tool_call = {
            'name': 'unknown_tool',
            'args': {}
        }
        
        result = self.bot._execute_tool(tool_call)
        assert result == "不明なツール: unknown_tool"

    @patch('api.bot.get_exchange_rates')
    def test_execute_tool_exception(self, mock_get_rates):
        """ツール実行中の例外テスト"""
        mock_get_rates.invoke.side_effect = Exception("Tool execution error")
        
        tool_call = {
            'name': 'get_exchange_rates',
            'args': {}
        }
        
        result = self.bot._execute_tool(tool_call)
        assert "ツール実行中にエラーが発生しました" in result

    def test_execute_tool_missing_name(self):
        """ツール名が欠けている場合のテスト"""
        tool_call = {
            'args': {}
        }
        
        result = self.bot._execute_tool(tool_call)
        assert result == "不明なツール: "

    def test_execute_tool_missing_args(self):
        """引数が欠けている場合のテスト"""
        tool_call = {
            'name': 'get_specific_exchange_rate'
        }
        
        with patch('api.bot.get_specific_exchange_rate') as mock_tool:
            mock_tool.invoke.return_value = "結果"
            result = self.bot._execute_tool(tool_call)
            mock_tool.invoke.assert_called_once_with({})


class TestFunctionCallingChatBotProcessMessage:
    """メッセージ処理メソッドのテスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch('api.bot.ChatGoogleGenerativeAI'):
                self.bot = FunctionCallingChatBot()

    def test_process_message_no_llm(self):
        """LLMが初期化されていない場合のテスト"""
        self.bot.llm_with_tools = None
        
        result = self.bot.process_message("テストメッセージ")
        
        assert "システムの初期化中にエラーが発生しました" in result
        assert "GEMINI_API_KEY" in result

    def test_process_message_without_tool_calls(self):
        """ツール呼び出しがない場合のメッセージ処理テスト"""
        # モックLLMの設定
        mock_llm_with_tools = MagicMock()
        mock_response = MagicMock()
        mock_response.tool_calls = []  # ツール呼び出しなし
        mock_response.content = "通常のレスポンス"
        mock_llm_with_tools.invoke.return_value = mock_response
        
        self.bot.llm_with_tools = mock_llm_with_tools
        
        result = self.bot.process_message("こんにちは")
        
        # LLMが呼び出されたことを確認
        mock_llm_with_tools.invoke.assert_called_once()
        call_args = mock_llm_with_tools.invoke.call_args[0][0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], HumanMessage)
        assert "こんにちは" in call_args[0].content
        
        assert result == "通常のレスポンス"

    def test_process_message_with_tool_calls(self):
        """ツール呼び出しがある場合のメッセージ処理テスト"""
        # モックLLMの設定
        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        
        # 最初のレスポンス（ツール呼び出しあり）
        mock_first_response = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.get.side_effect = lambda key, default=None: {
            'name': 'get_exchange_rates',
            'args': {},
            'id': 'tool_call_1'
        }.get(key, default)
        mock_first_response.tool_calls = [mock_tool_call]
        
        # 最終レスポンス
        mock_final_response = MagicMock()
        mock_final_response.content = "為替レート情報を取得しました"
        
        mock_llm_with_tools.invoke.return_value = mock_first_response
        mock_llm.invoke.return_value = mock_final_response
        
        self.bot.llm = mock_llm
        self.bot.llm_with_tools = mock_llm_with_tools
        
        # _execute_toolメソッドをモック化
        with patch.object(self.bot, '_execute_tool') as mock_execute_tool:
            mock_execute_tool.return_value = "モック為替レート結果"
            
            result = self.bot.process_message("為替レートを教えて")
            
            # 最初のLLM呼び出しが行われたことを確認
            mock_llm_with_tools.invoke.assert_called_once()
            
            # ツール実行が呼び出されたことを確認
            mock_execute_tool.assert_called_once_with(mock_tool_call)
            
            # 最終的なLLM呼び出しが行われたことを確認
            mock_llm.invoke.assert_called_once()
            final_call_args = mock_llm.invoke.call_args[0][0]
            
            # メッセージ履歴の確認
            assert len(final_call_args) == 3  # HumanMessage, AIMessage, ToolMessage
            assert isinstance(final_call_args[0], HumanMessage)
            assert final_call_args[1] == mock_first_response
            assert isinstance(final_call_args[2], ToolMessage)
            
            assert result == "為替レート情報を取得しました"

    def test_process_message_multiple_tool_calls(self):
        """複数のツール呼び出しがある場合のテスト"""
        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        
        # 複数のツール呼び出しを持つレスポンス
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.get.side_effect = lambda key, default=None: {
            'name': 'get_exchange_rates',
            'args': {},
            'id': 'tool_call_1'
        }.get(key, default)
        
        mock_tool_call_2 = MagicMock()
        mock_tool_call_2.get.side_effect = lambda key, default=None: {
            'name': 'get_specific_exchange_rate',
            'args': {'currency_pair': 'USD_JPY'},
            'id': 'tool_call_2'
        }.get(key, default)
        
        mock_first_response = MagicMock()
        mock_first_response.tool_calls = [mock_tool_call_1, mock_tool_call_2]
        
        mock_final_response = MagicMock()
        mock_final_response.content = "複数の為替情報を取得しました"
        
        mock_llm_with_tools.invoke.return_value = mock_first_response
        mock_llm.invoke.return_value = mock_final_response
        
        self.bot.llm = mock_llm
        self.bot.llm_with_tools = mock_llm_with_tools
        
        with patch.object(self.bot, '_execute_tool') as mock_execute_tool:
            mock_execute_tool.side_effect = ["結果1", "結果2"]
            
            result = self.bot.process_message("為替レートを教えて")
            
            # 2回のツール実行が行われたことを確認
            assert mock_execute_tool.call_count == 2
            mock_execute_tool.assert_has_calls([
                call(mock_tool_call_1),
                call(mock_tool_call_2)
            ])
            
            # 最終的なLLM呼び出しの確認
            final_call_args = mock_llm.invoke.call_args[0][0]
            assert len(final_call_args) == 4  # HumanMessage, AIMessage, ToolMessage, ToolMessage
            
            assert result == "複数の為替情報を取得しました"

    def test_process_message_exception(self):
        """メッセージ処理中の例外テスト"""
        mock_llm_with_tools = MagicMock()
        mock_llm_with_tools.invoke.side_effect = Exception("LLM error")
        
        self.bot.llm_with_tools = mock_llm_with_tools
        
        result = self.bot.process_message("テストメッセージ")
        
        assert "処理中にエラーが発生しました" in result
        assert "しばらく時間をおいてから再度お試しください" in result

    def test_system_prompt_content(self):
        """システムプロンプトの内容確認テスト"""
        mock_llm_with_tools = MagicMock()
        mock_response = MagicMock()
        mock_response.tool_calls = []
        mock_response.content = "レスポンス"
        mock_llm_with_tools.invoke.return_value = mock_response
        
        self.bot.llm_with_tools = mock_llm_with_tools
        
        self.bot.process_message("テストメッセージ")
        
        # LLMに渡されたメッセージの内容を確認
        call_args = mock_llm_with_tools.invoke.call_args[0][0]
        message_content = call_args[0].content
        
        # システムプロンプトの主要要素が含まれていることを確認
        assert "親切で知識豊富な日本語チャットボット" in message_content
        assert "為替レート情報を提供" in message_content
        assert "get_exchange_rates" in message_content
        assert "get_specific_exchange_rate" in message_content
        assert "常に日本語で回答" in message_content
        assert "テストメッセージ" in message_content

    def test_tool_message_creation(self):
        """ToolMessageの作成テスト"""
        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        
        mock_tool_call = MagicMock()
        mock_tool_call.get.side_effect = lambda key, default=None: {
            'name': 'get_exchange_rates',
            'args': {},
            'id': 'test_tool_id'
        }.get(key, default)
        
        mock_first_response = MagicMock()
        mock_first_response.tool_calls = [mock_tool_call]
        
        mock_final_response = MagicMock()
        mock_final_response.content = "最終レスポンス"
        
        mock_llm_with_tools.invoke.return_value = mock_first_response
        mock_llm.invoke.return_value = mock_final_response
        
        self.bot.llm = mock_llm
        self.bot.llm_with_tools = mock_llm_with_tools
        
        with patch.object(self.bot, '_execute_tool') as mock_execute_tool:
            mock_execute_tool.return_value = "ツール結果"
            
            self.bot.process_message("テスト")
            
            # 最終的なLLM呼び出しでToolMessageが正しく作成されたことを確認
            final_call_args = mock_llm.invoke.call_args[0][0]
            tool_message = final_call_args[2]
            
            assert isinstance(tool_message, ToolMessage)
            assert tool_message.content == "ツール結果"
            assert tool_message.tool_call_id == "test_tool_id"


class TestFunctionCallingChatBotIntegration:
    """統合テスト"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'})
    @patch('api.bot.ChatGoogleGenerativeAI')
    @patch('api.bot.get_exchange_rates')
    def test_full_exchange_rate_workflow(self, mock_get_rates, mock_chat_google):
        """為替レート取得の完全なワークフローテスト"""
        # LLMの設定
        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        mock_chat_google.return_value = mock_llm
        mock_llm.bind_tools.return_value = mock_llm_with_tools
        
        # ツール呼び出しを含むレスポンス
        mock_tool_call = MagicMock()
        mock_tool_call.get.side_effect = lambda key, default=None: {
            'name': 'get_exchange_rates',
            'args': {},
            'id': 'rate_call_1'
        }.get(key, default)
        
        mock_first_response = MagicMock()
        mock_first_response.tool_calls = [mock_tool_call]
        
        mock_final_response = MagicMock()
        mock_final_response.content = "現在の為替レートは以下の通りです：..."
        
        mock_llm_with_tools.invoke.return_value = mock_first_response
        mock_llm.invoke.return_value = mock_final_response
        
        # ツールのモック設定
        mock_get_rates.invoke.return_value = "USD/JPY: 150.00"
        
        bot = FunctionCallingChatBot()
        result = bot.process_message("今日の為替レートを教えて")
        
        # 全体のワークフローが正しく実行されたことを確認
        mock_llm_with_tools.invoke.assert_called_once()
        mock_get_rates.invoke.assert_called_once_with({})
        mock_llm.invoke.assert_called_once()
        
        assert result == "現在の為替レートは以下の通りです：..."

    @patch.dict(os.environ, {}, clear=True)
    def test_no_api_key_workflow(self):
        """APIキーなしでのワークフローテスト"""
        bot = FunctionCallingChatBot()
        result = bot.process_message("テストメッセージ")
        
        assert "GEMINI_API_KEY" in result
        assert "システムの初期化中にエラーが発生しました" in result