#!/usr/bin/env python3
"""
SVG追加機能の包括的なテスト（モック版）
PyQt5がインストールされていない環境でも実行可能
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'r_vertical_text'))

# PyQt5のモックを作成
class MockQApplication:
    @staticmethod
    def clipboard():
        return MockClipboard()

class MockClipboard:
    def __init__(self):
        self._text = ""
    
    def setText(self, text):
        self._text = text
    
    def text(self):
        return self._text

class MockQColor:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    
    def name(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

# モックを設定
sys.modules['PyQt5'] = Mock()
sys.modules['PyQt5.QtWidgets'] = Mock()
sys.modules['PyQt5.QtCore'] = Mock()
sys.modules['PyQt5.QtGui'] = Mock()

# モッククラスを設定
sys.modules['PyQt5.QtWidgets'].QApplication = MockQApplication
sys.modules['PyQt5.QtWidgets'].QDialog = Mock
sys.modules['PyQt5.QtWidgets'].QVBoxLayout = Mock
sys.modules['PyQt5.QtWidgets'].QHBoxLayout = Mock
sys.modules['PyQt5.QtWidgets'].QLabel = Mock
sys.modules['PyQt5.QtWidgets'].QLineEdit = Mock
sys.modules['PyQt5.QtWidgets'].QSpinBox = Mock
sys.modules['PyQt5.QtWidgets'].QPushButton = Mock
sys.modules['PyQt5.QtWidgets'].QTextEdit = Mock
sys.modules['PyQt5.QtWidgets'].QCheckBox = Mock
sys.modules['PyQt5.QtWidgets'].QColorDialog = Mock
sys.modules['PyQt5.QtWidgets'].QGroupBox = Mock
sys.modules['PyQt5.QtWidgets'].QFormLayout = Mock
sys.modules['PyQt5.QtWidgets'].QMessageBox = Mock
sys.modules['PyQt5.QtCore'].Qt = Mock()
sys.modules['PyQt5.QtGui'].QColor = MockQColor
sys.modules['PyQt5.QtGui'].QFont = Mock
sys.modules['PyQt5.QtGui'].QPixmap = Mock
sys.modules['PyQt5.QtGui'].QPainter = Mock

# テスト対象のモジュールをインポート
try:
    from r_vertical_text import VerticalTextDialog, RVerticalText
except ImportError as e:
    print(f"インポートエラー: {e}")
    sys.exit(1)

class TestSVGAdditionMock(unittest.TestCase):
    """SVG追加機能のテスト（モック版）"""
    
    def setUp(self):
        """テストのセットアップ"""
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
            pass  # モックなので実際のクリーンアップは不要
    
    def test_svg_generation(self):
        """SVG生成のテスト"""
        print("SVG生成テストを実行中...")
        
        # テスト用の設定
        text = "テスト"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = MockQColor(0, 0, 0)
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
        print(f"生成されたSVG: {svg_content[:100]}...")
    
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
        
        print(f"✅ SVG一時ファイル保存テスト成功: {temp_path}")
        
        # クリーンアップ
        os.unlink(temp_path)
    
    def test_clipboard_addition(self):
        """クリップボード追加のテスト"""
        print("クリップボード追加テストを実行中...")
        
        svg_content = "<svg><text>テスト</text></svg>"
        
        # クリップボードに追加
        result = self.dialog.addSVGToClipboard(svg_content)
        
        # 検証
        self.assertTrue(result)
        
        print("✅ クリップボード追加テスト成功")
    
    def test_direct_svg_layer_creation(self):
        """直接SVGレイヤー作成のテスト"""
        print("直接SVGレイヤー作成テストを実行中...")
        
        svg_content = "<svg><text>テスト</text></svg>"
        
        # 直接SVGレイヤー作成
        result = self.dialog.createSVGLayerDirectly(self.mock_doc, svg_content)
        
        # 検証
        self.assertTrue(result)
        self.mock_doc.createVectorLayer.assert_called_once_with("縦書きテキスト")
        self.mock_root.addChildNode.assert_called_once()
        
        print("✅ 直接SVGレイヤー作成テスト成功")
    
    def test_import_svg_to_krita(self):
        """SVGインポートのテスト"""
        print("SVGインポートテストを実行中...")
        
        svg_content = "<svg><text>テスト</text></svg>"
        
        # SVGインポート
        result = self.dialog.importSVGToKrita(svg_content)
        
        # 検証
        self.assertTrue(result is True or isinstance(result, str))
        
        print("✅ SVGインポートテスト成功")
    
    def test_draw_text_to_vector_layer(self):
        """ベクターレイヤー描画のテスト"""
        print("ベクターレイヤー描画テストを実行中...")
        
        # テスト用の設定
        text = "テスト"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = MockQColor(0, 0, 0)
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
    
    def test_add_to_krita_integration(self):
        """Krita追加の統合テスト"""
        print("Krita追加統合テストを実行中...")
        
        # テスト用のテキストを設定
        self.dialog.text_input.setPlainText("テストテキスト")
        
        # モックのKritaインスタンスを設定
        with patch('r_vertical_text.Krita') as mock_krita_class:
            mock_krita_instance = Mock()
            mock_krita_class.instance.return_value = mock_krita_instance
            mock_krita_instance.activeDocument.return_value = self.mock_doc
            
            # Kritaに追加
            self.dialog.addToKrita()
            
            # 検証
            # 少なくとも一つの方法が試行されることを確認
            self.mock_doc.createVectorLayer.assert_called()
        
        print("✅ Krita追加統合テスト成功")

def run_comprehensive_tests():
    """包括的なテストを実行"""
    print("=" * 60)
    print("SVG追加機能の包括的なテストを開始します（モック版）")
    print("=" * 60)
    
    # テストスイートを作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSVGAdditionMock)
    
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
