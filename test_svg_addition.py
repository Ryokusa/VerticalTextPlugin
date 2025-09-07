#!/usr/bin/env python3
"""
SVG追加機能の包括的なテスト
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'r_vertical_text'))

try:
    from r_vertical_text import VerticalTextDialog, RVerticalText
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("PyQt5がインストールされていない可能性があります")
    sys.exit(1)

class TestSVGAddition(unittest.TestCase):
    """SVG追加機能のテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.dialog = VerticalTextDialog()
        
        # モックのKritaインスタンスを作成
        self.mock_krita = Mock()
        self.mock_doc = Mock()
        self.mock_root = Mock()
        self.mock_layer = Mock()
        
        # モックの設定
        self.mock_krita.activeDocument.return_value = self.mock_doc
        self.mock_doc.rootNode.return_value = self.mock_root
        self.mock_doc.createVectorLayer.return_value = self.mock_layer
        
    def tearDown(self):
        """テストのクリーンアップ"""
        if hasattr(self, 'dialog'):
            self.dialog.close()
    
    def test_svg_generation(self):
        """SVG生成のテスト"""
        print("SVG生成テストを実行中...")
        
        # テスト用の設定
        text = "テスト"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = QColor(0, 0, 0)
        force_monospace = False
        
        # SVGを生成
        svg_content = self.dialog.generateVerticalTextSVG(
            text, font_size, line_spacing, line_feed, 
            font_family, text_color, force_monospace
        )
        
        # 検証
        self.assertIsInstance(svg_content, str)
        self.assertIn("<svg", svg_content)
        self.assertIn("テスト", svg_content)
        self.assertIn("xmlns", svg_content)
        
        print("✅ SVG生成テスト成功")
    
    def test_svg_to_temp_file(self):
        """SVG一時ファイル保存のテスト"""
        print("SVG一時ファイル保存テストを実行中...")
        
        svg_content = "<svg><text>テスト</text></svg>"
        
        # 一時ファイルに保存
        temp_path = self.dialog.saveSVGToTempFile(svg_content)
        
        # 検証
        self.assertIsInstance(temp_path, str)
        self.assertTrue(os.path.exists(temp_path))
        self.assertTrue(temp_path.endswith('.svg'))
        
        # ファイル内容を確認
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, svg_content)
        
        # クリーンアップ
        os.unlink(temp_path)
        
        print("✅ SVG一時ファイル保存テスト成功")
    
    def test_clipboard_addition(self):
        """クリップボード追加のテスト"""
        print("クリップボード追加テストを実行中...")
        
        svg_content = "<svg><text>テスト</text></svg>"
        
        # クリップボードに追加
        result = self.dialog.addSVGToClipboard(svg_content)
        
        # 検証
        self.assertTrue(result)
        
        # クリップボードの内容を確認
        clipboard = QApplication.clipboard()
        clipboard_content = clipboard.text()
        self.assertEqual(clipboard_content, svg_content)
        
        print("✅ クリップボード追加テスト成功")
    
    @patch('r_vertical_text.Krita')
    def test_direct_svg_layer_creation(self, mock_krita_class):
        """直接SVGレイヤー作成のテスト"""
        print("直接SVGレイヤー作成テストを実行中...")
        
        # モックの設定
        mock_krita_instance = Mock()
        mock_krita_class.instance.return_value = mock_krita_instance
        mock_krita_instance.activeDocument.return_value = self.mock_doc
        
        svg_content = "<svg><text>テスト</text></svg>"
        
        # 直接SVGレイヤー作成
        result = self.dialog.createSVGLayerDirectly(self.mock_doc, svg_content)
        
        # 検証
        self.assertTrue(result)
        self.mock_doc.createVectorLayer.assert_called_once_with("縦書きテキスト")
        self.mock_root.addChildNode.assert_called_once()
        
        print("✅ 直接SVGレイヤー作成テスト成功")
    
    @patch('r_vertical_text.Krita')
    def test_import_svg_to_krita(self, mock_krita_class):
        """SVGインポートのテスト"""
        print("SVGインポートテストを実行中...")
        
        # モックの設定
        mock_krita_instance = Mock()
        mock_krita_class.instance.return_value = mock_krita_instance
        mock_krita_instance.activeDocument.return_value = self.mock_doc
        
        svg_content = "<svg><text>テスト</text></svg>"
        
        # SVGインポート
        result = self.dialog.importSVGToKrita(svg_content)
        
        # 検証
        self.assertTrue(result is True or isinstance(result, str))
        
        print("✅ SVGインポートテスト成功")
    
    @patch('r_vertical_text.Krita')
    def test_draw_text_to_vector_layer(self, mock_krita_class):
        """ベクターレイヤー描画のテスト"""
        print("ベクターレイヤー描画テストを実行中...")
        
        # モックの設定
        mock_krita_instance = Mock()
        mock_krita_class.instance.return_value = mock_krita_instance
        mock_krita_instance.activeDocument.return_value = self.mock_doc
        
        # テスト用の設定
        text = "テスト"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = QColor(0, 0, 0)
        force_monospace = False
        
        # ベクターレイヤー描画
        result = self.dialog.drawTextToVectorLayer(
            self.mock_doc, text, font_size, line_spacing, line_feed, 
            font_family, text_color, force_monospace
        )
        
        # 検証
        self.assertTrue(result)
        self.mock_doc.createVectorLayer.assert_called_once_with("縦書きテキスト")
        self.mock_root.addChildNode.assert_called_once()
        
        print("✅ ベクターレイヤー描画テスト成功")
    
    @patch('r_vertical_text.Krita')
    @patch('r_vertical_text.QMessageBox')
    def test_add_to_krita_integration(self, mock_message_box, mock_krita_class):
        """Krita追加の統合テスト"""
        print("Krita追加統合テストを実行中...")
        
        # モックの設定
        mock_krita_instance = Mock()
        mock_krita_class.instance.return_value = mock_krita_instance
        mock_krita_instance.activeDocument.return_value = self.mock_doc
        
        # メッセージボックスのモック
        mock_message_box.information = Mock()
        mock_message_box.warning = Mock()
        mock_message_box.critical = Mock()
        
        # テスト用のテキストを設定
        self.dialog.text_input.setPlainText("テストテキスト")
        
        # Kritaに追加
        self.dialog.addToKrita()
        
        # 検証
        # 少なくとも一つの方法が試行されることを確認
        mock_message_box.information.assert_called()
        
        print("✅ Krita追加統合テスト成功")
    
    def test_text_splitting(self):
        """テキスト分割のテスト"""
        print("テキスト分割テストを実行中...")
        
        # テストケース1: 改行文字による分割
        text1 = "テスト\n複数行"
        lines1 = self.dialog.splitTextIntoLines(text1, 10)
        expected1 = ["テスト", "複数行"]
        self.assertEqual(lines1, expected1)
        
        # テストケース2: 強制改行
        text2 = "これは長いテキストです"
        lines2 = self.dialog.splitTextIntoLines(text2, 5)
        expected2 = ["これは長い", "テキストです"]
        self.assertEqual(lines2, expected2)
        
        # テストケース3: 句読点での改行制御
        text3 = "これは。テスト、です"
        lines3 = self.dialog.splitTextIntoLines(text3, 3)
        # 句読点は改行されない
        self.assertIn("これは。", lines3[0])
        
        print("✅ テキスト分割テスト成功")

def run_comprehensive_tests():
    """包括的なテストを実行"""
    print("=" * 60)
    print("SVG追加機能の包括的なテストを開始します")
    print("=" * 60)
    
    # テストスイートを作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSVGAddition)
    
    # テストランナーを作成
    runner = unittest.TextTestRunner(verbosity=2)
    
    # テストを実行
    result = runner.run(test_suite)
    
    # 結果を表示
    print("\n" + "=" * 60)
    print("テスト結果:")
    print(f"実行されたテスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.failures:
        print("\n失敗したテスト:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nエラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
