#!/bin/bash
# 縦書きテキストプラグインのテスト実行スクリプト（Linux/macOS用）

echo "縦書きテキストプラグイン テスト実行"
echo "====================================="

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "仮想環境が見つかりません。作成します..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
echo "仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係のインストール
echo "依存関係をインストール中..."
pip install -r requirements-test.txt

echo ""
echo "テストを実行します..."
echo ""

# テストの実行
echo "1. 自動テストを実行中..."
python test_plugin.py --automated

echo ""
echo "2. 包括的なユニットテストを実行中..."
python test_vertical_text.py

echo ""
echo "テスト完了！"
echo "対話的テストを実行するには: python test_plugin.py --interactive"
echo ""
