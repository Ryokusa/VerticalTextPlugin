#!/usr/bin/env python3
"""
縦書きテキストプラグインのテストスクリプト
Krita環境外でプラグインの基本機能をテストします
krita-python-mockを使用してKrita APIをモックします
"""

import sys
import os

# krita-python-mockをインポート
try:
    import krita
    print("✅ krita-python-mockが正常にインポートされました")
except ImportError:
    print("❌ krita-python-mockがインストールされていません")
    print("以下のコマンドでインストールしてください:")
    print("pip install git+https://github.com/rbreu/krita-python-mock.git")
    sys.exit(1)

# プラグインディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'r_vertical_text'))

try:
    from r_vertical_text import VerticalTextDialog, RVerticalText
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
    
    def test_plugin_interactive():
        """プラグインの対話的テスト"""
        app = QApplication(sys.argv)
        
        print("縦書きテキストプラグインの対話的テストを開始します...")
        print("=" * 60)
        
        # ダイアログを作成
        dialog = VerticalTextDialog()
        
        # プレビューの初期状態をチェック
        pixmap = dialog.preview_label.pixmap()
        if pixmap is not None and not pixmap.isNull():
            print("✅ 初期プレビューが正常に生成されました")
        else:
            print("❌ 初期プレビューが生成されませんでした")
            # 手動でプレビューを更新
            dialog.updatePreview()
            pixmap2 = dialog.preview_label.pixmap()
            if pixmap2 is not None and not pixmap2.isNull():
                print("✅ 手動更新でプレビューが生成されました")
            else:
                print("❌ 手動更新でもプレビューが生成されませんでした")
        
        # ダイアログを表示
        dialog.show()
        
        print("✅ ダイアログが表示されました")
        print("📝 以下の機能をテストしてください:")
        print("   - テキスト入力とプレビュー")
        print("   - フォントサイズの変更")
        print("   - 色の選択")
        print("   - 行間の調整")
        print("   - SVG生成機能")
        print("=" * 60)
        
        # アプリケーションを実行
        sys.exit(app.exec_())
    
    def test_plugin_automated():
        """プラグインの自動テスト"""
        print("縦書きテキストプラグインの自動テストを開始します...")
        print("=" * 60)
        
        # 基本的な機能テスト
        app = QApplication(sys.argv)
        
        try:
            # ダイアログの作成テスト
            dialog = VerticalTextDialog()
            print("✅ ダイアログの作成に成功")
            
            # デフォルト値のテスト
            assert dialog.text == "こんにちは\n世界", "デフォルトテキストが正しくありません"
            assert dialog.font_size == 24, "デフォルトフォントサイズが正しくありません"
            assert dialog.line_spacing == 1.2, "デフォルト行間が正しくありません"
            print("✅ デフォルト値の設定が正しい")
            
            # テキスト処理のテスト
            test_text = "テスト\n複数行"
            lines = dialog.splitTextIntoLines(test_text, 5)
            expected_lines = ["テスト", "複数行"]
            assert lines == expected_lines, f"テキスト分割が正しくありません: {lines}"
            print("✅ テキスト分割機能が正常")
            
            # SVG生成のテスト
            svg_content = dialog.generateVerticalTextSVG(
                "テスト", 24, 1.2, 10, "Arial", QColor(0, 0, 0), False
            )
            assert isinstance(svg_content, str), "SVG生成が文字列を返していません"
            assert "<svg" in svg_content, "SVGコンテンツが正しくありません"
            # 個別の文字がSVGに含まれているかチェック
            assert "テ" in svg_content, "文字「テ」がSVGに含まれていません"
            assert "ス" in svg_content, "文字「ス」がSVGに含まれていません"
            assert "ト" in svg_content, "文字「ト」がSVGに含まれていません"
            print("✅ SVG生成機能が正常")
            
            # 拡張機能のテスト
            mock_krita = krita.Krita.instance()
            extension = RVerticalText(mock_krita)
            assert extension is not None, "拡張機能の作成に失敗"
            print("✅ 拡張機能の作成に成功")
            
            dialog.close()
            print("=" * 60)
            print("🎉 すべての自動テストが成功しました！")
            
        except Exception as e:
            print(f"❌ テスト中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        return 0
    
    def show_help():
        """ヘルプを表示"""
        print("縦書きテキストプラグイン テストスクリプト")
        print("=" * 50)
        print("使用方法:")
        print("  python test_plugin.py [オプション]")
        print("")
        print("オプション:")
        print("  --interactive, -i    対話的テスト（GUI表示）")
        print("  --automated, -a      自動テスト（コンソールのみ）")
        print("  --help, -h           このヘルプを表示")
        print("")
        print("例:")
        print("  python test_plugin.py --interactive")
        print("  python test_plugin.py --automated")
        print("")
        print("注意:")
        print("  - PyQt5が必要です: pip install PyQt5")
        print("  - krita-python-mockが必要です: pip install git+https://github.com/rbreu/krita-python-mock.git")
    
    if __name__ == "__main__":
        if len(sys.argv) > 1:
            if sys.argv[1] in ["--interactive", "-i"]:
                test_plugin_interactive()
            elif sys.argv[1] in ["--automated", "-a"]:
                sys.exit(test_plugin_automated())
            elif sys.argv[1] in ["--help", "-h"]:
                show_help()
            else:
                print(f"不明なオプション: {sys.argv[1]}")
                show_help()
                sys.exit(1)
        else:
            # デフォルトは対話的テスト
            test_plugin_interactive()
        
except ImportError as e:
    print(f"❌ 必要なライブラリがインストールされていません: {e}")
    print("")
    print("以下のコマンドで必要なライブラリをインストールしてください:")
    print("  pip install PyQt5")
    print("  pip install git+https://github.com/rbreu/krita-python-mock.git")
    sys.exit(1)
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
