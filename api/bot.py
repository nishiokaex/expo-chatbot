"""
Function Calling対応チャットボット
LangChain CoreのFunction Callingを使用
"""

import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from api.tools import get_exchange_rates, get_specific_exchange_rate

logger = logging.getLogger(__name__)


class FunctionCallingChatBot:
    """
    LangChain CoreのFunction Callingを使用したチャットボット
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY環境変数が設定されていません")
            self.llm = None
            self.llm_with_tools = None
        else:
            try:
                # ChatGoogleGenerativeAIでLLMを初期化
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=self.gemini_api_key,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # ツール付きLLMを作成
                self.llm_with_tools = self.llm.bind_tools([
                    get_exchange_rates,
                    get_specific_exchange_rate
                ])
                
                logger.info("FunctionCallingChatBot初期化完了")
                
            except Exception as e:
                logger.error(f"FunctionCallingChatBot初期化エラー: {e}")
                self.llm = None
                self.llm_with_tools = None
    
    def _execute_tool(self, tool_call: dict) -> str:
        """
        ツール実行ヘルパーメソッド
        
        Args:
            tool_call: ツール呼び出し情報
            
        Returns:
            str: ツール実行結果
        """
        try:
            tool_name = tool_call.get('name', '')
            tool_args = tool_call.get('args', {})
            
            if tool_name == 'get_exchange_rates':
                return get_exchange_rates.invoke({})
            elif tool_name == 'get_specific_exchange_rate':
                return get_specific_exchange_rate.invoke(tool_args)
            else:
                return f"不明なツール: {tool_name}"
                
        except Exception as e:
            logger.error(f"ツール実行エラー: {e}")
            return f"ツール実行中にエラーが発生しました: {str(e)}"
    
    def process_message(self, message: str) -> str:
        """
        Function Callingを使用してメッセージを処理
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            str: AIからのレスポンス
        """
        try:
            if not self.llm_with_tools:
                return "申し訳ございません。システムの初期化中にエラーが発生しました。GEMINI_API_KEYが正しく設定されているか確認してください。"
            
            # システムプロンプトを含むメッセージを作成
            system_message = """あなたは親切で知識豊富な日本語チャットボットです。

このチャットボットは主に為替レート情報を提供することに特化しています。

利用可能なツール:
- get_exchange_rates: 主要通貨ペアの為替レートを取得
- get_specific_exchange_rate: 特定通貨ペアの為替レートを取得

為替、通貨、レートに関する質問の場合は、適切なツールを使用して最新のデータを取得してください。
為替関連以外の質問の場合は、丁寧にお断りし、為替関連の質問をお待ちしていることをお伝えください。

常に日本語で回答してください。"""
            
            # 初回のLLM呼び出し（ツール付き）
            messages = [
                HumanMessage(content=f"{system_message}\n\nユーザーの質問: {message}")
            ]
            
            response = self.llm_with_tools.invoke(messages)
            
            # ツール呼び出しがあるかチェック
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # メッセージ履歴にAIレスポンスを追加
                messages.append(response)
                
                # 各ツールを実行
                for tool_call in response.tool_calls:
                    tool_result = self._execute_tool(tool_call)
                    
                    # ツール結果をメッセージ履歴に追加
                    messages.append(ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call.get('id', 'unknown')
                    ))
                
                # ツール結果を含めて最終回答を生成
                final_response = self.llm.invoke(messages)
                return final_response.content
            
            # ツール呼び出しがない場合は直接回答
            return response.content
                
        except Exception as e:
            logger.error(f"Function Callingメッセージ処理エラー: {e}")
            return "申し訳ございません。処理中にエラーが発生しました。しばらく時間をおいてから再度お試しください。"