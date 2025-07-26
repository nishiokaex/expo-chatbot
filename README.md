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
- **UIライブラリ**: react-native-gifted-chat
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
python3 -m venv test_env && source test_env/bin/activate && pip install -r requirements.txt
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```
