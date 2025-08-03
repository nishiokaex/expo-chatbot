# Expo Chatbot

React Native for Web と Python FastAPIを使用したチャットボットアプリケーション

## デプロイ先

**本番環境**: https://expo-chatbot.vercel.app/

## 機能

- **チャットボット機能**: 自然言語でのやり取り
- **為替レート取得**: リアルタイムの為替情報を提供

## アーキテクチャ

### フロントエンド
- **React Native**: Expo SDK v52
- **状態管理**: Zustand (Class構文)
- **UIライブラリ**: react-native-paper
- **言語**: JavaScript

### バックエンド
- **Webフレームワーク**: FastAPI (Python 3)

### 必要な環境
- Node.js
- Python 3.x
- Expo CLI

### ローカル開発

#### フロントエンド起動
```bash
cd frontend
npm install
npm run web
```

#### バックエンド起動
```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate

# 本番用パッケージのインストール
pip install -r requirements.txt

# 開発・テスト用パッケージのインストール（開発時のみ）
pip install -r requirements-dev.txt

# サーバー起動
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### テスト実行
```bash
# 仮想環境が有効になっていることを確認
source venv/bin/activate

# 全テストの実行
python -m pytest tests/ -v

# カバレッジ付きテスト実行
python -m pytest tests/ --cov=api --cov-report=term-missing
```

## 依存関係の管理

プロジェクトでは依存関係を以下のように分離しています：

- **requirements.txt**: 本番環境に必要なパッケージ（FastAPI、LangChain等）
- **requirements-dev.txt**: 開発・テスト環境のみに必要なパッケージ（pytest等）

### 本番環境
Vercelでのデプロイ時は`requirements.txt`のみが自動でインストールされます。

### 開発環境
ローカル開発時は両方のrequirementsファイルをインストールしてください。
