"""
Function Calling対応チャットボット
LangChain CoreのFunction Callingを使用
ベクトルストア検索機能付き
"""

import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from api.tools import get_exchange_rates, get_specific_exchange_rate
from api.vector_store import vector_store_service

logger = logging.getLogger(__name__)


class FunctionCallingChatBot:
    """
    LangChain CoreのFunction Callingを使用したチャットボット
    """
    
    def __init__(self):
        # ツールマッピング辞書の定義
        self.TOOLS = {
            'get_exchange_rates': get_exchange_rates,
            'get_specific_exchange_rate': get_specific_exchange_rate
        }
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
                self.llm_with_tools = self.llm.bind_tools(list(self.TOOLS.values()))
                
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
            
            if tool_name in self.TOOLS:
                # 辞書マッピングを使用してツールを実行
                if tool_name == 'get_exchange_rates':
                    return self.TOOLS[tool_name].invoke({})
                else:
                    return self.TOOLS[tool_name].invoke(tool_args)
            else:
                return f"不明なツール: {tool_name}"
                
        except Exception as e:
            logger.error(f"ツール実行エラー: {e}")
            return f"ツール実行中にエラーが発生しました: {str(e)}"
    
    def _generate_search_query(self, message: str) -> str:
        """
        ユーザーメッセージからベクトル検索用クエリを生成
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            str: 検索クエリ
        """
        try:
            if not self.llm:
                return message
            
            query_prompt = f"""以下のユーザーメッセージから、ベクトル検索に適した検索クエリを生成してください。
            
ユーザーメッセージ: {message}

検索クエリは以下の点を考慮してください:
- 重要なキーワードを含む
- 簡潔で明確
- 検索しやすい形式

検索クエリのみを返してください（説明不要）:"""
            
            response = self.llm.invoke([HumanMessage(content=query_prompt)])
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"検索クエリ生成エラー: {e}")
            return message
    
    def _search_context_documents(self, message: str) -> list:
        """
        ベクトルストア検索でコンテキストドキュメントを取得
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            list: 検索されたドキュメントのリスト
        """
        context_documents = []
        if vector_store_service.is_initialized():
            # 検索クエリを生成
            search_query = self._generate_search_query(message)
            logger.info(f"生成された検索クエリ: {search_query}")
            
            # ベクトル検索を実行
            context_documents = vector_store_service.search_documents(search_query, k=3)
            logger.info(f"検索結果: {len(context_documents)}個のドキュメント")
        
        return context_documents
    
    def _build_context_text(self, context_documents: list) -> str:
        """
        検索されたドキュメントからコンテキストテキストを構築
        
        Args:
            context_documents: 検索されたドキュメントのリスト
            
        Returns:
            str: 構築されたコンテキストテキスト
        """
        if not context_documents:
            return ""
        
        context_text = "\n\n参考情報:\n"
        for i, doc in enumerate(context_documents, 1):
            context_text += f"{i}. {doc.page_content}\n"
        context_text += "\n"
        
        return context_text
    
    def _create_system_message(self, has_context: bool) -> str:
        """
        システムメッセージを作成
        
        Args:
            has_context: コンテキスト情報があるかどうか
            
        Returns:
            str: システムメッセージ
        """
        if has_context:
            return """あなたは親切で知識豊富な日本語チャットボットです。

設定されたWebページの内容に基づいて質問に回答してください。
参考情報が提供されている場合は、その情報を活用して回答してください。
参考情報で回答できない場合や、為替・通貨に関する質問の場合は、適切なツールを使用してください。

利用可能なツール:
- get_exchange_rates: 主要通貨ペアの為替レートを取得
- get_specific_exchange_rate: 特定通貨ペアの為替レートを取得

常に日本語で回答してください。"""
        else:
            return """あなたは親切で知識豊富な日本語チャットボットです。

このチャットボットは主に為替レート情報を提供することに特化しています。

利用可能なツール:
- get_exchange_rates: 主要通貨ペアの為替レートを取得
- get_specific_exchange_rate: 特定通貨ペアの為替レートを取得

為替、通貨、レートに関する質問の場合は、適切なツールを使用して最新のデータを取得してください。
為替関連以外の質問の場合は、丁寧にお断りし、為替関連の質問をお待ちしていることをお伝えください。

常に日本語で回答してください。"""
    
    def _handle_tool_calls(self, messages: list, response) -> str:
        """
        ツール呼び出しを処理して最終回答を生成
        
        Args:
            messages: メッセージ履歴のリスト
            response: LLMからの初回レスポンス
            
        Returns:
            str: 最終回答
        """
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

    def process_message(self, message: str) -> str:
        """
        ベクトル検索とFunction Callingを使用してメッセージを処理
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            str: AIからのレスポンス
        """
        try:
            if not self.llm_with_tools:
                return "申し訳ございません。システムの初期化中にエラーが発生しました。GEMINI_API_KEYが正しく設定されているか確認してください。"
            
            # ベクトルストア検索でコンテキストドキュメントを取得
            context_documents = self._search_context_documents(message)
            
            # コンテキスト情報を構築
            context_text = self._build_context_text(context_documents)
            
            # システムメッセージを作成
            system_message = self._create_system_message(bool(context_documents))
            
            # 初回のLLM呼び出し（ツール付き）
            messages = [
                HumanMessage(content=f"{system_message}\n\n{context_text}ユーザーの質問: {message}")
            ]
            
            response = self.llm_with_tools.invoke(messages)
            
            # ツール呼び出しがあるかチェック
            if hasattr(response, 'tool_calls') and response.tool_calls:
                return self._handle_tool_calls(messages, response)
            
            # ツール呼び出しがない場合は直接回答
            return response.content
                
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
            return "申し訳ございません。処理中にエラーが発生しました。しばらく時間をおいてから再度お試しください。"