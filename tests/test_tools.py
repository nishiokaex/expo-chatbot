"""
為替レート取得ツールのユニットテスト
GMO Coin API呼び出しとレスポンス処理のテスト
"""

import pytest
import responses
import requests
from datetime import datetime
from unittest.mock import patch, MagicMock
from api.tools import ExchangingTool, get_exchange_rates, get_specific_exchange_rate


class TestExchangingTool:
    """ExchangingToolクラスのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.tool = ExchangingTool()

    def test_init(self):
        """初期化テスト"""
        assert self.tool.api_url == "https://forex-api.coin.z.com/public/v1/ticker"
        assert self.tool.description == "為替レート情報を取得するツール"

    @responses.activate
    def test_get_rates_success(self):
        """正常な為替レート取得のテスト"""
        # モックレスポンスを設定
        mock_response = {
            "status": 0,
            "data": [
                {
                    "symbol": "USD_JPY",
                    "bid": "150.123",
                    "ask": "150.126"
                },
                {
                    "symbol": "EUR_JPY",
                    "bid": "165.456",
                    "ask": "165.460"
                },
                {
                    "symbol": "GBP_JPY",
                    "bid": "190.789",
                    "ask": "190.793"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_rates()
        
        # レスポンス内容を確認
        assert "📈 現在の為替レート" in result
        assert "ドル/円 (USD_JPY)" in result
        assert "ユーロ/円 (EUR_JPY)" in result
        assert "ポンド/円 (GBP_JPY)" in result
        assert "150.123" in result
        assert "150.126" in result
        assert "⏰ 取得時刻:" in result
        assert "※ レートは参考値です" in result

    @responses.activate
    def test_get_rates_api_error_status(self):
        """APIエラーステータスのテスト"""
        mock_response = {
            "status": 1,
            "data": []
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_rates()
        assert result == "為替データの取得に失敗しました。"

    @responses.activate
    def test_get_rates_empty_data(self):
        """空のデータが返された場合のテスト"""
        mock_response = {
            "status": 0,
            "data": []
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_rates()
        assert result == "為替データが見つかりませんでした。"

    @responses.activate
    def test_get_rates_network_error(self):
        """ネットワークエラーのテスト"""
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            body=requests.exceptions.ConnectionError("Network error")
        )
        
        result = self.tool.get_rates()
        assert "為替データの取得中にネットワークエラーが発生しました" in result

    @responses.activate
    def test_get_rates_http_error(self):
        """HTTPエラーのテスト"""
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            status=500
        )
        
        result = self.tool.get_rates()
        assert "為替データの取得中にネットワークエラーが発生しました" in result

    @responses.activate
    def test_get_rates_timeout(self):
        """タイムアウトエラーのテスト"""
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            body=requests.exceptions.Timeout("Timeout error")
        )
        
        result = self.tool.get_rates()
        assert "為替データの取得中にネットワークエラーが発生しました" in result

    @responses.activate
    def test_get_rates_spread_calculation(self):
        """スプレッド計算のテスト"""
        mock_response = {
            "status": 0,
            "data": [
                {
                    "symbol": "USD_JPY",
                    "bid": "150.000",
                    "ask": "150.005"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_rates()
        assert "スプレッド: 0.0050" in result

    @responses.activate
    def test_get_rates_invalid_bid_ask(self):
        """不正なbid/ask値のテスト"""
        mock_response = {
            "status": 0,
            "data": [
                {
                    "symbol": "USD_JPY",
                    "bid": "N/A",
                    "ask": "N/A"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_rates()
        assert "買値: N/A" in result
        assert "売値: N/A" in result
        assert "スプレッド:" not in result  # スプレッドは計算されない

    @responses.activate
    def test_get_specific_rate_success(self):
        """特定通貨ペア取得の正常テスト"""
        mock_response = {
            "status": 0,
            "data": [
                {
                    "symbol": "USD_JPY",
                    "bid": "150.123",
                    "ask": "150.126"
                },
                {
                    "symbol": "EUR_JPY",
                    "bid": "165.456",
                    "ask": "165.460"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_specific_rate("USD_JPY")
        
        assert "💱 USD_JPY" in result
        assert "買値: 150.123" in result
        assert "売値: 150.126" in result
        assert "取得時刻:" in result

    @responses.activate
    def test_get_specific_rate_lowercase_input(self):
        """小文字入力での特定通貨ペア取得テスト"""
        mock_response = {
            "status": 0,
            "data": [
                {
                    "symbol": "USD_JPY",
                    "bid": "150.123",
                    "ask": "150.126"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_specific_rate("usd_jpy")
        assert "💱 usd_jpy" in result
        assert "買値: 150.123" in result

    @responses.activate
    def test_get_specific_rate_not_found(self):
        """存在しない通貨ペアの取得テスト"""
        mock_response = {
            "status": 0,
            "data": [
                {
                    "symbol": "USD_JPY",
                    "bid": "150.123",
                    "ask": "150.126"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_specific_rate("XYZ_ABC")
        assert "通貨ペア 'XYZ_ABC' が見つかりませんでした。" in result

    @responses.activate
    def test_get_specific_rate_api_error(self):
        """特定通貨ペア取得でのAPIエラーテスト"""
        mock_response = {
            "status": 1,
            "data": []
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_specific_rate("USD_JPY")
        assert "USD_JPYのデータ取得に失敗しました。" in result

    @responses.activate
    def test_get_specific_rate_exception(self):
        """特定通貨ペア取得での例外テスト"""
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            body=Exception("Unexpected error")
        )
        
        result = self.tool.get_specific_rate("USD_JPY")
        assert "USD_JPYのレート取得中にエラーが発生しました。" in result

    @patch('api.tools.datetime')
    @responses.activate
    def test_timestamp_format(self, mock_datetime):
        """タイムスタンプフォーマットのテスト"""
        # 固定された日時をモック
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        mock_datetime.strftime = datetime.strftime
        
        mock_response = {
            "status": 0,
            "data": [
                {
                    "symbol": "USD_JPY",
                    "bid": "150.000",
                    "ask": "150.005"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_rates()
        assert "⏰ 取得時刻: 2024-01-01 12:00:00" in result


class TestLangChainToolFunctions:
    """LangChainツール形式の関数テスト"""

    @patch('api.tools.ExchangingTool')
    def test_get_exchange_rates_function(self, mock_tool_class):
        """get_exchange_rates関数のテスト"""
        # モックインスタンスを設定
        mock_instance = MagicMock()
        mock_instance.get_rates.return_value = "モックレート情報"
        mock_tool_class.return_value = mock_instance
        
        result = get_exchange_rates.invoke({})
        
        # ExchangingToolが呼び出されたことを確認
        mock_tool_class.assert_called_once()
        mock_instance.get_rates.assert_called_once()
        assert result == "モックレート情報"

    @patch('api.tools.ExchangingTool')
    def test_get_specific_exchange_rate_function(self, mock_tool_class):
        """get_specific_exchange_rate関数のテスト"""
        # モックインスタンスを設定
        mock_instance = MagicMock()
        mock_instance.get_specific_rate.return_value = "モック特定レート情報"
        mock_tool_class.return_value = mock_instance
        
        result = get_specific_exchange_rate.invoke({"currency_pair": "USD_JPY"})
        
        # ExchangingToolが呼び出されたことを確認
        mock_tool_class.assert_called_once()
        mock_instance.get_specific_rate.assert_called_once_with("USD_JPY")
        assert result == "モック特定レート情報"

    def test_langchain_tool_decorators(self):
        """LangChainツールデコレータの確認"""
        # get_exchange_ratesがツール化されていることを確認
        assert hasattr(get_exchange_rates, 'name')
        assert hasattr(get_exchange_rates, 'description')
        
        # get_specific_exchange_rateがツール化されていることを確認
        assert hasattr(get_specific_exchange_rate, 'name')
        assert hasattr(get_specific_exchange_rate, 'description')
        
        # ツールの説明が適切に設定されていることを確認
        assert "GMO Coin API" in get_exchange_rates.description
        assert "特定の通貨ペア" in get_specific_exchange_rate.description


class TestIntegrationTests:
    """統合テスト"""

    def setup_method(self):
        """テストメソッドの初期化"""
        self.tool = ExchangingTool()

    @responses.activate
    def test_full_workflow_major_pairs(self):
        """主要通貨ペアの完全なワークフローテスト"""
        mock_response = {
            "status": 0,
            "data": [
                {"symbol": "USD_JPY", "bid": "150.123", "ask": "150.126"},
                {"symbol": "EUR_JPY", "bid": "165.456", "ask": "165.460"},
                {"symbol": "GBP_JPY", "bid": "190.789", "ask": "190.793"},
                {"symbol": "AUD_JPY", "bid": "98.123", "ask": "98.127"},
                {"symbol": "EUR_USD", "bid": "1.0845", "ask": "1.0848"},
                {"symbol": "CHF_JPY", "bid": "168.234", "ask": "168.238"}  # 主要通貨ペアではない
            ]
        }
        
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json=mock_response,
            status=200
        )
        
        result = self.tool.get_rates()
        
        # 主要通貨ペアが含まれていることを確認
        assert "ドル/円 (USD_JPY)" in result
        assert "ユーロ/円 (EUR_JPY)" in result
        assert "ポンド/円 (GBP_JPY)" in result
        assert "豪ドル/円 (AUD_JPY)" in result
        assert "ユーロ/ドル (EUR_USD)" in result
        
        # 主要通貨ペア以外は含まれていないことを確認
        assert "CHF_JPY" not in result

    @responses.activate
    def test_error_handling_chain(self):
        """エラーハンドリングのチェーンテスト"""
        # 最初のリクエストは失敗
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            body=requests.exceptions.ConnectionError("Network error"),
            status=500
        )
        
        result1 = self.tool.get_rates()
        assert "ネットワークエラー" in result1
        
        # 2回目のリクエストは成功
        responses.add(
            responses.GET,
            "https://forex-api.coin.z.com/public/v1/ticker",
            json={"status": 0, "data": [{"symbol": "USD_JPY", "bid": "150.000", "ask": "150.005"}]},
            status=200
        )
        
        result2 = self.tool.get_rates()
        assert "ドル/円" in result2