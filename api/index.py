"""
メインエントリーポイント
FastAPIアプリケーションの起動
"""

from api.main import app

# main.pyからアプリケーションをインポートして公開
__all__ = ["app"]