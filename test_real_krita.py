#!/usr/bin/env python3
"""
実際のKrita環境でのテストスクリプト
このスクリプトはKrita内で実行して、レイヤーにコンテンツが正しく追加されるかテストします
"""

import sys
import os

# プラグインディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'r_vertical_text'))

try:
    from r_vertical_text import VerticalTextDialog
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
    
    def test_in_krita():
        """Krita環境でのテスト"""
        print("Krita環境での縦書きテキストプラグインテストを開始します...")
        print("=" * 60)
        
        # ダイアログを作成
        dialog = VerticalTextDialog()
        
        # テスト用の設定
        dialog.text_input.setPlainText("テスト\n縦書き\nテキスト")
        dialog.font_size_spin.setValue(24)
        dialog.line_spacing_spin.setValue(120)  # 120%
        dialog.char_spacing_spin.setValue(120)  # 120%
        dialog.line_feed_spin.setValue(10)
        dialog.font_family_input.setText("Arial")
        dialog.text_color = QColor(0, 0, 0)
        
        print("✅ ダイアログの設定が完了しました")
        
        # プレビューを更新
        dialog.updatePreview()
        print("✅ プレビューが更新されました")
        
        # SVG生成をテスト
        svg_content = dialog.generateVerticalTextSVG(
            "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left"
        )
        
        print(f"✅ SVG生成成功: {len(svg_content)}文字")
        print(f"SVG内容の一部: {svg_content[:100]}...")
        
        # 各メソッドを個別にテスト
        print("\n各メソッドのテスト:")
        print("-" * 40)
        
        # アクティブなドキュメントを取得
        try:
            from krita import Krita
            doc = Krita.instance().activeDocument()
            if doc is None:
                print("❌ アクティブなドキュメントがありません")
                print("Kritaで新しいドキュメントを作成してからテストしてください")
                return False
            else:
                print(f"✅ アクティブなドキュメントを取得: {doc.name()}")
        except ImportError:
            print("❌ Krita環境ではありません")
            return False
        
        # 方法1: Krita 5のaddShapesFromSvg（最も確実）
        print("\n1. Krita 5のaddShapesFromSvgのテスト:")
        try:
            result = dialog.addTextWithKrita5SVG(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ Krita 5のaddShapesFromSvg: 成功")
            else:
                print("❌ Krita 5のaddShapesFromSvg: 失敗")
        except Exception as e:
            print(f"❌ Krita 5のaddShapesFromSvg: エラー - {e}")
        
        # 方法1.5: クリップボード経由
        print("\n1.5. クリップボード経由のテスト:")
        try:
            result = dialog.addTextViaClipboard(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ クリップボード経由: 成功")
            else:
                print("❌ クリップボード経由: 失敗")
        except Exception as e:
            print(f"❌ クリップボード経由: エラー - {e}")
        
        # 方法1.5: ファイルインポート経由
        print("\n1.5. ファイルインポート経由のテスト:")
        try:
            result = dialog.addTextViaFileImport(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ ファイルインポート経由: 成功")
            else:
                print("❌ ファイルインポート経由: 失敗")
        except Exception as e:
            print(f"❌ ファイルインポート経由: エラー - {e}")
        
        # 方法1.6: テキストツール直接使用
        print("\n1.6. テキストツール直接使用のテスト:")
        try:
            result = dialog.createTextLayerDirectly(doc, "テスト", 24, "Arial", QColor(0, 0, 0), "right_to_left")
            if result:
                print("✅ テキストツール直接使用: 成功")
            else:
                print("❌ テキストツール直接使用: 失敗")
        except Exception as e:
            print(f"❌ テキストツール直接使用: エラー - {e}")
        
        # 方法1.7: Krita API直接描画
        print("\n1.7. Krita API直接描画のテスト:")
        try:
            result = dialog.drawTextWithKritaAPI(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ Krita API直接描画: 成功")
            else:
                print("❌ Krita API直接描画: 失敗")
        except Exception as e:
            print(f"❌ Krita API直接描画: エラー - {e}")
        
        # 方法1.5: 簡易ベクターレイヤーテスト
        print("\n1.5. 簡易ベクターレイヤーのテスト:")
        try:
            result = dialog.createSimpleVectorLayer(doc, "テスト", 24, "Arial", QColor(0, 0, 0))
            if result:
                print("✅ 簡易ベクターレイヤー: 成功")
            else:
                print("❌ 簡易ベクターレイヤー: 失敗")
        except Exception as e:
            print(f"❌ 簡易ベクターレイヤー: エラー - {e}")
        
        # 方法1.6: 基本図形描画テスト
        print("\n1.6. 基本図形描画のテスト:")
        try:
            result = dialog.createBasicShapeLayer(doc, "テスト", 24, "Arial", QColor(0, 0, 0))
            if result:
                print("✅ 基本図形描画: 成功")
            else:
                print("❌ 基本図形描画: 失敗")
        except Exception as e:
            print(f"❌ 基本図形描画: エラー - {e}")
        
        # 方法1.7: 確実なテキスト描画
        print("\n1.7. 確実なテキスト描画のテスト:")
        try:
            result = dialog.drawTextWithGuaranteedMethod(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ 確実なテキスト描画: 成功")
            else:
                print("❌ 確実なテキスト描画: 失敗")
        except Exception as e:
            print(f"❌ 確実なテキスト描画: エラー - {e}")
        
        # 方法2: ペイントレイヤー直接描画
        print("\n2. ペイントレイヤー直接描画のテスト:")
        try:
            result = dialog.drawTextToPaintLayer(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ ペイントレイヤー直接描画: 成功")
            else:
                print("❌ ペイントレイヤー直接描画: 失敗")
        except Exception as e:
            print(f"❌ ペイントレイヤー直接描画: エラー - {e}")
        
        # 方法3: テキストツール使用
        print("\n3. テキストツール使用のテスト:")
        try:
            result = dialog.createTextLayerWithTool(doc, "テスト", 24, "Arial", QColor(0, 0, 0), "right_to_left")
            if result:
                print("✅ テキストツール使用: 成功")
            else:
                print("❌ テキストツール使用: 失敗")
        except Exception as e:
            print(f"❌ テキストツール使用: エラー - {e}")
        
        # 方法4: 画像として描画
        print("\n4. 画像として描画のテスト:")
        try:
            result = dialog.drawTextAsImage(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ 画像として描画: 成功")
            else:
                print("❌ 画像として描画: 失敗")
        except Exception as e:
            print(f"❌ 画像として描画: エラー - {e}")
        
        # 方法5: SVGレイヤー直接作成
        print("\n5. SVGレイヤー直接作成のテスト:")
        try:
            result = dialog.createSVGLayerDirectly(doc, svg_content)
            if result:
                print("✅ SVGレイヤー直接作成: 成功")
            else:
                print("❌ SVGレイヤー直接作成: 失敗")
        except Exception as e:
            print(f"❌ SVGレイヤー直接作成: エラー - {e}")
        
        # 方法6: ベクターレイヤー直接描画
        print("\n6. ベクターレイヤー直接描画のテスト:")
        try:
            result = dialog.drawTextToVectorLayer(doc, "テスト", 24, 1.2, 1.2, 10, "Arial", QColor(0, 0, 0), False, "right_to_left")
            if result:
                print("✅ ベクターレイヤー直接描画: 成功")
            else:
                print("❌ ベクターレイヤー直接描画: 失敗")
        except Exception as e:
            print(f"❌ ベクターレイヤー直接描画: エラー - {e}")
        
        # Kritaバージョン情報を表示
        print("\n" + "=" * 60)
        print("Kritaバージョン情報:")
        try:
            from krita import Krita
            krita_instance = Krita.instance()
            if krita_instance:
                if hasattr(krita_instance, 'version'):
                    print(f"Kritaバージョン: {krita_instance.version()}")
                else:
                    print("Kritaバージョン: 情報取得不可")
            else:
                print("Kritaインスタンス: 取得不可")
        except Exception as e:
            print(f"Kritaバージョン取得エラー: {e}")
        
        # PyQt5.QtSvgの可用性を表示
        print("\nPyQt5.QtSvgの可用性:")
        try:
            from PyQt5.QtSvg import QSvgRenderer, QSvgGenerator
            print("✅ PyQt5.QtSvg: 利用可能")
        except ImportError:
            print("❌ PyQt5.QtSvg: 利用不可")
        
        print("\n" + "=" * 60)
        print("🎉 テストが完了しました！")
        print("レイヤーパネルで作成されたレイヤーを確認してください。")
        print("空でないレイヤーが作成されていれば、修正は成功です。")
        
        return True
    
    if __name__ == "__main__":
        test_in_krita()
        
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("Krita環境で実行してください。")
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
