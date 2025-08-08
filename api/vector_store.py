"""
ベクトルストアサービス
URLからHTMLドキュメントを読み込み、InMemoryVectorStoreで検索機能を提供
"""

import logging
from typing import List, Optional
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ログ設定
logger = logging.getLogger(__name__)

class VectorStoreService:
    """ベクトルストアサービスクラス"""
    
    def __init__(self):
        """初期化"""
        self.vector_store: Optional[InMemoryVectorStore] = None
        self.embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        self.current_urls: List[str] = []
    
    def _get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """エンベディングインスタンスの遅延初期化"""
        if self.embeddings is None:
            self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        return self.embeddings
    
    def load_and_store_documents(self, urls: List[str]) -> tuple[List[str], List[str]]:
        """
        複数のURLからHTMLドキュメントを読み込み、ベクトルストアに格納
        
        Args:
            urls: 読み込むWebページのURLのリスト
            
        Returns:
            tuple[List[str], List[str]]: (成功したURL, 失敗したURL)
        """
        successful_urls = []
        failed_urls = []
        all_split_documents = []
        
        logger.info(f"複数HTMLドキュメントを読み込み中: {len(urls)}個のURL")
        
        # 各URLからドキュメントを読み込み
        for url in urls:
            try:
                logger.info(f"HTMLドキュメントを読み込み中: {url}")
                
                # WebBaseLoaderでHTMLを取得
                loader = WebBaseLoader([url])  # リスト形式で渡す
                documents = loader.load()
                
                if not documents:
                    logger.error(f"ドキュメントが見つかりませんでした: {url}")
                    failed_urls.append(url)
                    continue
                
                # 空のコンテンツもチェック
                if not documents[0].page_content.strip():
                    logger.error(f"ドキュメントのコンテンツが空です: {url}")
                    failed_urls.append(url)
                    continue
                
                logger.info(f"ドキュメントを分割中: {len(documents)}個のドキュメント from {url}")
                
                # ドキュメントを分割
                split_documents = self.text_splitter.split_documents(documents)
                logger.info(f"分割完了: {len(split_documents)}個のチャンク from {url}")
                
                all_split_documents.extend(split_documents)
                successful_urls.append(url)
                
            except Exception as e:
                logger.error(f"ドキュメント読み込みエラー ({url}): {e}")
                failed_urls.append(url)
        
        # 成功したドキュメントがある場合のみベクトルストアを構築
        if all_split_documents:
            try:
                embeddings = self._get_embeddings()
                self.vector_store = InMemoryVectorStore.from_documents(
                    documents=all_split_documents,
                    embedding=embeddings
                )
                
                self.current_urls = successful_urls
                logger.info(f"ベクトルストア構築完了: {len(successful_urls)}個のURL")
            except Exception as e:
                logger.error(f"ベクトルストア構築エラー: {e}")
                return [], urls  # 全て失敗として扱う
        
        return successful_urls, failed_urls
    
    def search_documents(self, query: str, k: int = 3) -> List[Document]:
        """
        ベクトルストアから関連ドキュメントを検索
        
        Args:
            query: 検索クエリ
            k: 取得する関連ドキュメント数
            
        Returns:
            List[Document]: 関連ドキュメントのリスト
        """
        if not self.vector_store:
            logger.warning("ベクトルストアが初期化されていません")
            return []
        
        try:
            logger.info(f"ドキュメント検索中: {query}")
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"検索結果: {len(results)}個のドキュメント")
            return results
            
        except Exception as e:
            logger.error(f"ドキュメント検索エラー: {e}")
            return []
    
    def clear_vector_store(self) -> bool:
        """
        ベクトルストアをクリア
        
        Returns:
            bool: 成功時True
        """
        try:
            self.vector_store = None
            self.current_urls = []
            logger.info("ベクトルストアをクリアしました")
            return True
            
        except Exception as e:
            logger.error(f"ベクトルストアクリアエラー: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """
        ベクトルストアが初期化されているかチェック
        
        Returns:
            bool: 初期化済みの場合True
        """
        return self.vector_store is not None
    
    def get_current_urls(self) -> List[str]:
        """
        現在設定されているURLリストを取得
        
        Returns:
            List[str]: 現在のURLリスト
        """
        return self.current_urls

# グローバルインスタンス
vector_store_service = VectorStoreService()