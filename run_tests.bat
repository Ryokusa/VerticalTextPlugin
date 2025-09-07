@echo off
REM 縦書きテキストプラグインのテスト実行スクリプト（Windows用）

echo 縦書きテキストプラグイン テスト実行
echo =====================================

REM 仮想環境の確認
if not exist "venv" (
    echo 仮想環境が見つかりません。作成します...
    python -m venv venv
)

REM 仮想環境をアクティベート
echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

REM 依存関係のインストール
echo 依存関係をインストール中...
pip install -r requirements-test.txt

echo.
echo テストを実行します...
echo.

REM テストの実行
echo 1. 自動テストを実行中...
python test_plugin.py --automated

echo.
echo 2. 包括的なユニットテストを実行中...
python test_vertical_text.py

echo.
echo テスト完了！
echo 対話的テストを実行するには: python test_plugin.py --interactive
echo.

pause
