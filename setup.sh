#!/bin/bash
# セットアップスクリプト

set -e

echo "🚀 SDS2Rosterのセットアップを開始します..."

# Python バージョンチェック
echo "📌 Pythonバージョンを確認中..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python $python_version が見つかりました"

# 仮想環境の作成
echo "📦 仮想環境を作成中..."
if [ -d ".venv" ]; then
    echo "   既存の仮想環境が見つかりました"
    read -p "   既存の仮想環境を削除して再作成しますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .venv
        python3 -m venv .venv
        echo "   ✅ 仮想環境を再作成しました"
    fi
else
    python3 -m venv .venv
    echo "   ✅ 仮想環境を作成しました"
fi

# 仮想環境のアクティベート
echo "🔌 仮想環境をアクティベート中..."
source .venv/bin/activate

# pip のアップグレード
echo "⬆️  pipをアップグレード中..."
pip install --upgrade pip

# 依存関係のインストール
echo "📚 依存関係をインストール中..."
pip install -r requirements.txt
echo "   ✅ 本番依存関係をインストールしました"

pip install -r requirements-dev.txt
echo "   ✅ 開発依存関係をインストールしました"

# パッケージのインストール（開発モード）
echo "🔧 パッケージをインストール中（開発モード）..."
pip install -e .
echo "   ✅ パッケージをインストールしました"

# .envファイルの作成
if [ ! -f ".env" ]; then
    echo "📝 .envファイルを作成中..."
    cp .env.example .env
    echo "   ✅ .envファイルを作成しました（.env.exampleからコピー）"
    echo "   ⚠️  .envファイルを編集して、Azure認証情報を設定してください"
else
    echo "   ℹ️  .envファイルは既に存在します"
fi

# 初期テストの実行
echo "🧪 初期テストを実行中..."
pytest tests/unit/test_converter.py -v

echo ""
echo "✅ セットアップが完了しました！"
echo ""
echo "次のステップ："
echo "  1. .envファイルを編集してAzure認証情報を設定"
echo "  2. 仮想環境をアクティベート: source .venv/bin/activate"
echo "  3. CLIを試す: sds2roster version"
echo ""
