# アーキテクチャ・ディレクトリ構成

## 概要
Expo SDK v52を使用したReact Nativeチャットボットアプリケーション（フロントエンド）とFastAPI（バックエンド）による構成。

## 全体構成
```
expo-chatbot/
├── フロントエンド（React Native + Expo）
├── バックエンド（FastAPI + Python）
├── テスト
├── ドキュメント
└── 設定ファイル
```

## ディレクトリ構成

### ルートレベル
```
expo-chatbot/
├── CLAUDE.md           # Claude Code用プロジェクト指示書
├── README.md           # プロジェクト概要
├── package.json        # フロントエンド依存関係
├── app.json           # Expoアプリ設定
├── requirements.txt    # Python依存関係（本番）
├── requirements-dev.txt # Python依存関係（開発）
├── vercel.json        # Vercelデプロイ設定
├── oxlintrc.json      # ESLint設定
├── memo.txt           # 開発メモ
└── venv/              # Python仮想環境
```

### フロントエンド（app/）
```
app/
├── _layout.js         # ルートレイアウト（expo-router）
├── index.js           # ホーム画面
└── settings.js        # 設定画面
```

### コンポーネント（src/）
```
src/
├── components/
│   ├── ChatScreen.js          # チャット画面
│   ├── MessageBubble.js       # メッセージ表示
│   ├── UrlSettingsScreen.js   # URL設定画面
│   └── adaptive-cards/        # Adaptive Cards実装
│       ├── AdaptiveCard.js    # メインコンポーネント
│       ├── index.js           # エクスポート
│       ├── actions/           # アクション要素
│       │   └── SubmitAction.js
│       ├── elements/          # 表示要素
│       │   ├── Column.js
│       │   ├── ColumnSet.js
│       │   ├── Container.js
│       │   └── TextBlock.js
│       ├── inputs/            # 入力要素
│       │   ├── TextInput.js
│       │   └── ToggleInput.js
│       └── utils/             # ユーティリティ
│           ├── parser.js      # JSONパーサー
│           └── validation.js   # バリデーション
└── stores/
    └── ChatStore.js           # Zustandストア（Chat状態管理）
```

### バックエンド（api/）
```
api/
├── main.py              # FastAPIメインアプリケーション
├── index.py            # Vercelエントリーポイント
├── bot.py              # チャットボットロジック
├── models.py           # データモデル定義
├── tools.py            # 外部ツール連携
├── vector_store.py     # ベクトルストア管理
└── exchanging_tool.py  # データ交換ツール
```

### テスト（tests/）
```
tests/
├── __init__.py                # Python package初期化
├── test_bot.py               # botロジックテスト
├── test_index.py             # indexエンドポイントテスト
├── test_main.py              # メインAPIテスト
├── test_models.py            # データモデルテスト
├── test_tools.py             # ツールテスト
├── test_adaptive_cards.js    # Adaptive Cardsテスト
└── test_new_chat_ui.js       # 新Chat UIテスト
```

### ドキュメント（docs/）
```
docs/
├── coding-conventions.md     # コーディング規約
└── requirements.md          # 要件定義
```

### その他
```
diary/                       # 開発日誌ディレクトリ
examples/
└── adaptive-cards-examples.js # Adaptive Cards使用例
.claude/                     # Claude Code設定
.expo/                       # Expo開発用キャッシュ
.pytest_cache/               # pytest キャッシュ
```

## 技術スタック

### フロントエンド
- **フレームワーク**: React Native + Expo SDK v52
- **ルーティング**: expo-router
- **状態管理**: Zustand（Class構文）
- **UI**: react-native-paper, react-native-safe-area-context
- **通信**: axios, fetch
- **テスト**: jest-expo, @testing-library/react-native

### バックエンド
- **フレームワーク**: FastAPI (Python 3)
- **BaaS**: Supabase
- **データベース**: PostgreSQL（Supabase）
- **認証**: Supabase Auth

### 開発・デプロイ
- **フロントエンド**: Expo Web (`npm run web`)
- **バックエンド**: Vercel Functions
- **バージョン管理**: Git + GitHub（機能ブランチ運用）

## アーキテクチャ設計

### レイヤ構成（クリーンアーキテクチャ）
1. **Presentation Layer** (app/, src/components/)
   - UI コンポーネント
   - 画面遷移
   - ユーザーインタラクション

2. **Domain Layer** (src/stores/)
   - ビジネスロジック
   - 状態管理

3. **Infrastructure Layer** (api/)
   - 外部API連携
   - データアクセス
   - 永続化処理

## 新規プロジェクト構築手順

### 前提条件
- Node.js (v18以上)
- Python 3.11以上
- npm または yarn
- git

### 1. プロジェクト初期設定

#### 1.1 プロジェクトディレクトリ作成
```bash
mkdir your-chatbot-project
cd your-chatbot-project
git init
```

#### 1.2 Expoプロジェクト初期化
```bash
# Expo CLI インストール（グローバル）
npm install -g @expo/cli

# Expo プロジェクト作成（expo-router テンプレート使用）
npx create-expo-app@latest . --template blank

# または手動でpackage.json作成後に依存関係をインストール
npm init -y
```

#### 1.3 package.json設定
```bash
# 必要な依存関係をインストール
npm install expo@^53.0.4 \
  expo-router@~5.0.3 \
  expo-constants@~17.1.4 \
  expo-linking@~7.1.4 \
  expo-notifications@^0.31.4 \
  expo-splash-screen@~0.30.7 \
  expo-status-bar@~2.2.3 \
  react@19.0.0 \
  react-dom@19.0.0 \
  react-native@0.79.1 \
  react-native-web@^0.20.0 \
  react-native-screens@~4.10.0 \
  react-native-safe-area-context@^5.3.0 \
  react-native-gesture-handler@~2.24.0 \
  react-native-reanimated@^3.18.0 \
  react-native-paper@^5.14.5 \
  @react-native-async-storage/async-storage@^2.2.0 \
  axios@^1.10.0 \
  react-hook-form@^7.60.0 \
  react-i18next@^15.6.0 \
  react-icons@^5.5.0 \
  zustand@^5.0.6

# 開発用依存関係
npm install --save-dev oxlint@^1.7.0
```

### 2. プロジェクト構造作成

#### 2.1 ディレクトリ構造作成
```bash
# メインディレクトリ
mkdir -p app src/components src/stores api tests docs diary examples

# コンポーネントディレクトリ
mkdir -p src/components/adaptive-cards/{actions,elements,inputs,utils}

# テストディレクトリ
mkdir -p tests

# 設定ファイルディレクトリ
mkdir -p .claude
```

#### 2.2 設定ファイル作成
```bash
# app.json作成
cat > app.json << 'EOF'
{
  "expo": {
    "scheme": "your-app-scheme",
    "plugins": [
      "expo-router"
    ],
    "name": "your-app-name",
    "slug": "your-app-slug"
  }
}
EOF

# oxlintrc.json作成
cat > oxlintrc.json << 'EOF'
{
  "rules": {}
}
EOF

# vercel.json作成（Vercelデプロイ用）
cat > vercel.json << 'EOF'
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build"
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/(.*)",
      "destination": "/"
    }
  ]
}
EOF
```

### 3. Python環境設定

#### 3.1 Python仮想環境作成
```bash
# Python仮想環境作成
python3 -m venv venv

# 仮想環境アクティベート（macOS/Linux）
source venv/bin/activate

# 仮想環境アクティベート（Windows）
# venv\Scripts\activate
```

#### 3.2 Python依存関係設定
```bash
# requirements.txt作成
cat > requirements.txt << 'EOF'
fastapi==0.115.2
uvicorn==0.34.0
requests==2.32.3
python-dotenv==1.0.1
pydantic==2.10.4
langchain-core==0.3.72
langchain-google-genai==2.1.8
langchain-community
beautifulsoup4==4.12.2
EOF

# requirements-dev.txt作成
cat > requirements-dev.txt << 'EOF'
# 開発・テスト用パッケージ
# 本番環境にはデプロイされません

# テストフレームワーク
pytest==7.4.4
pytest-asyncio==0.23.2
pytest-cov==4.1.0
pytest-mock==3.12.0

# HTTPモック用
responses==0.24.1

# 開発時に必要なその他のパッケージをここに追加
EOF

# Python パッケージインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. 基本ファイル作成

#### 4.1 フロントエンド基本ファイル
```bash
# app/_layout.js（ルートレイアウト）
cat > app/_layout.js << 'EOF'
import { Stack } from 'expo-router';
import { PaperProvider } from 'react-native-paper';

export default function RootLayout() {
  return (
    <PaperProvider>
      <Stack>
        <Stack.Screen name="index" />
        <Stack.Screen name="settings" />
      </Stack>
    </PaperProvider>
  );
}
EOF

# app/index.js（ホーム画面）
cat > app/index.js << 'EOF'
import { View, Text } from 'react-native';

export default function HomeScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Welcome to Your Chatbot App</Text>
    </View>
  );
}
EOF

# app/settings.js（設定画面）
cat > app/settings.js << 'EOF'
import { View, Text } from 'react-native';

export default function SettingsScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Settings Screen</Text>
    </View>
  );
}
EOF
```

#### 4.2 バックエンド基本ファイル
```bash
# api/main.py（FastAPIメインアプリ）
cat > api/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
EOF

# api/index.py（Vercelエントリーポイント）
cat > api/index.py << 'EOF'
from main import app

# Vercel用のハンドラー
handler = app
EOF
```

#### 4.3 プロジェクト管理ファイル
```bash
# CLAUDE.md（プロジェクト指示書）
# 既存のCLAUDE.mdをコピーして、プロジェクト名などを変更

# README.md
cat > README.md << 'EOF'
# Your Chatbot Project

Expo SDK v52を使用したReact Nativeチャットボットアプリケーション

## 開発環境セットアップ

### 前提条件
- Node.js v18以上
- Python 3.11以上
- Expo CLI

### インストール
```bash
# フロントエンド依存関係
npm install

# バックエンド依存関係
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 開発サーバー起動
```bash
# フロントエンド（Web版）
npm run web

# フロントエンド（モバイル版）
npm start

# バックエンド（ローカル開発用）
cd api && python -m uvicorn main:app --reload
```

## テスト実行
```bash
# フロントエンドリント
npm run lint

# バックエンドテスト
pytest
```
EOF
```

### 5. Git設定

#### 5.1 .gitignore作成
```bash
cat > .gitignore << 'EOF'
# OSX
.DS_Store

# Xcode
build/
*.pbxuser
!default.pbxuser
*.mode1v3
!default.mode1v3
*.mode2v3
!default.mode2v3
*.perspectivev3
!default.perspectivev3
xcuserdata
*.xccheckout
*.moved-aside
DerivedData
*.hmap
*.ipa
*.xcuserstate
project.xcworkspace

# Android
*.apk
*.ap_
*.dex
*.class
bin/
gen/
out/

# node.js
node_modules/
npm-debug.log
yarn-error.log

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.pytest_cache/
.coverage

# Expo
.expo/
dist/
web-build/

# misc
*.log
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/

# Temporary files
*.tmp
*.temp
memo.txt
EOF
```

#### 5.2 初期コミット
```bash
git add .
git commit -m "feat: initial project setup with Expo and FastAPI"
```

### 6. 開発開始

#### 6.1 開発サーバー起動確認
```bash
# フロントエンド起動テスト
npm run web

# 別ターミナルでバックエンド起動テスト（オプション）
source venv/bin/activate
cd api
python -m uvicorn main:app --reload --port 8000
```

#### 6.2 基本動作確認
- フロントエンド: http://localhost:8081
- バックエンドAPI: http://localhost:8000 （ローカル開発時）

### 実行順序まとめ

1. **環境準備** → Node.js, Python, git インストール
2. **プロジェクト作成** → ディレクトリ作成、git init
3. **フロントエンド設定** → npm init, 依存関係インストール
4. **バックエンド設定** → venv作成、Python依存関係インストール
5. **ファイル構造作成** → 必要なディレクトリとファイルの作成
6. **設定ファイル作成** → app.json, vercel.json, .gitignore等
7. **基本実装** → 最小限の動作するコードを配置
8. **Git初期化** → .gitignore設定、初回コミット
9. **動作確認** → 開発サーバー起動テスト

この手順で同じ構成のプロジェクトを新規作成できます。