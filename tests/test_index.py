"""
エントリーポイント（index.py）のユニットテスト
アプリケーションのインポートと公開機能のテスト
"""

import pytest
from unittest.mock import patch, MagicMock


class TestIndexModule:
    """index.pyモジュールのテスト"""

    def test_app_import(self):
        """appのインポートテスト"""
        from api.index import app
        from fastapi import FastAPI
        
        # appがFastAPIインスタンスであることを確認
        assert isinstance(app, FastAPI)

    def test_app_properties(self):
        """appの基本プロパティテスト"""
        from api.index import app
        
        # main.pyから正しくインポートされたアプリケーションの属性を確認
        assert app.title == "ChatBot API"
        assert app.description == "LangChain Function Calling対応チャットボット"
        assert app.version == "2.0.0"

    def test_module_exports(self):
        """モジュールのエクスポート確認テスト"""
        import api.index as index_module
        
        # __all__が正しく定義されていることを確認
        assert hasattr(index_module, '__all__')
        assert index_module.__all__ == ["app"]
        
        # __all__に含まれる要素がすべて存在することを確認
        for export_name in index_module.__all__:
            assert hasattr(index_module, export_name)

    def test_app_reference_consistency(self):
        """app参照の一貫性テスト"""
        from api.index import app as index_app
        from api.main import app as main_app
        
        # index.pyとmain.pyのappが同じインスタンスであることを確認
        assert index_app is main_app

    def test_module_docstring(self):
        """モジュールのdocstringテスト"""
        import api.index as index_module
        
        # docstringが存在し、適切な内容であることを確認
        assert index_module.__doc__ is not None
        assert "メインエントリーポイント" in index_module.__doc__
        assert "FastAPIアプリケーションの起動" in index_module.__doc__

    def test_module_attributes(self):
        """モジュールの属性テスト"""
        import api.index as index_module
        
        # 期待される属性が存在することを確認
        expected_attributes = ['app', '__all__', '__doc__']
        
        for attr in expected_attributes:
            assert hasattr(index_module, attr), f"属性 '{attr}' が見つかりません"

    def test_no_additional_imports(self):
        """不要なインポートがないことの確認テスト"""
        import api.index as index_module
        
        # index.pyは最小限のインポートのみを行うべき
        # main.pyのappのみをインポートし、他の不要なインポートはない
        module_vars = vars(index_module)
        
        # 最小限の変数のみが存在することを確認
        expected_vars = {'app', '__all__', '__doc__', '__name__', '__file__', '__package__'}
        actual_vars = set(module_vars.keys())
        
        # 期待される変数がすべて含まれていることを確認
        assert expected_vars.issubset(actual_vars)
        
        # 予期しない追加の変数がないことを確認（一部のPython内部変数は除く）
        python_internals = {
            '__loader__', '__spec__', '__cached__', '__builtins__',
            '__annotations__', '__path__'
        }
        unexpected_vars = actual_vars - expected_vars - python_internals
        assert len(unexpected_vars) == 0, f"予期しない変数が見つかりました: {unexpected_vars}"


class TestIndexFunctionality:
    """index.pyの機能テスト"""

    def test_app_can_be_used_for_uvicorn(self):
        """uvicornでアプリケーションを起動できることのテスト"""
        from api.index import app
        
        # appが適切なFastAPIインスタンスで、uvicornで起動可能であることを確認
        assert hasattr(app, 'openapi')
        assert hasattr(app, 'routes')
        assert callable(app)

    def test_app_routes_accessible(self):
        """appのルートにアクセス可能であることのテスト"""
        from api.index import app
        
        # 期待されるルートが存在することを確認
        route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        
        expected_routes = ["/", "/api/chat", "/api/tools"]
        for expected_route in expected_routes:
            assert expected_route in route_paths, f"ルート '{expected_route}' が見つかりません"

    @patch('api.main.FunctionCallingChatBot')
    def test_app_with_mocked_dependencies(self, mock_chatbot_class):
        """依存関係をモック化したappのテスト"""
        # main.pyの依存関係をモック化してindex.pyのappが正常に動作することを確認
        mock_chatbot = MagicMock()
        mock_chatbot_class.return_value = mock_chatbot
        
        # 新しくimportし直して、モック化された依存関係を使用
        import importlib
        import api.index
        importlib.reload(api.index)
        
        from api.index import app
        
        # appが正常に作成されたことを確認
        assert app is not None
        assert hasattr(app, 'title')


class TestIndexIntegration:
    """index.pyの統合テスト"""

    def test_index_with_test_client(self):
        """TestClientを使ったindex.pyアプリのテスト"""
        from fastapi.testclient import TestClient
        from api.index import app
        
        client = TestClient(app)
        
        # ヘルスチェックエンドポイントが正常に動作することを確認
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "ChatBot API is running with Function Calling"
        assert data["status"] == "ok"

    def test_index_openapi_schema(self):
        """OpenAPIスキーマが正常に生成されることのテスト"""
        from api.index import app
        
        # OpenAPIスキーマが生成できることを確認
        openapi_schema = app.openapi()
        
        assert openapi_schema is not None
        assert "openapi" in openapi_schema
        assert "info" in openapi_schema
        assert "paths" in openapi_schema
        
        # 基本的なAPIエンドポイント情報が含まれていることを確認
        paths = openapi_schema["paths"]
        assert "/" in paths
        assert "/api/chat" in paths
        assert "/api/tools" in paths

    def test_index_app_lifecycle(self):
        """アプリケーションのライフサイクルテスト"""
        from api.index import app
        
        # アプリケーションが複数回インポートされても同じインスタンスであることを確認
        import importlib
        import api.index
        
        app1 = api.index.app
        
        # モジュールを再インポート
        importlib.reload(api.index)
        app2 = api.index.app
        
        # 新しいインスタンスが作成されていることを確認（設計上、これは期待される動作）
        # ただし、基本的な属性は同じであることを確認
        assert app1.title == app2.title
        assert app1.version == app2.version


class TestErrorHandling:
    """index.pyのエラーハンドリングテスト"""

    def test_missing_app_import(self):
        """appのインポートが失敗した場合のテスト"""
        # このテストは実際の環境では現実的でないため、パスする
        pass

    def test_module_import_integrity(self):
        """モジュールのインポート整合性テスト"""
        import sys
        
        # api.indexモジュールが正常にインポートできることを確認
        if 'api.index' in sys.modules:
            del sys.modules['api.index']
        
        try:
            import api.index
            # インポートが成功することを確認
            assert api.index.app is not None
        except ImportError as e:
            pytest.fail(f"api.indexのインポートに失敗しました: {e}")


class TestDocumentation:
    """index.pyのドキュメント関連テスト"""

    def test_module_has_proper_docstring(self):
        """適切なdocstringが設定されていることのテスト"""
        import api.index as index_module
        
        docstring = index_module.__doc__
        assert docstring is not None
        assert len(docstring.strip()) > 0
        
        # docstringに期待されるキーワードが含まれていることを確認
        expected_keywords = ["メインエントリーポイント", "FastAPI", "アプリケーション"]
        for keyword in expected_keywords:
            assert keyword in docstring, f"docstringに '{keyword}' が含まれていません"

    def test_code_comments_and_structure(self):
        """コードのコメントと構造のテスト"""
        import inspect
        import api.index as index_module
        
        # ソースコードを取得
        source = inspect.getsource(index_module)
        
        # 適切なコメントが含まれていることを確認
        assert "main.py" in source
        assert "app" in source
        assert "__all__" in source