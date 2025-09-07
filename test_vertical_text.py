#!/usr/bin/env python3
"""
縦書きテキストプラグインの包括的なテストスイート
krita-python-mockを使用してKrita環境外でテストを実行
"""

import sys
import os
import unittest
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch, MagicMock

# krita-python-mockをインポート
try:
    import krita
    print("krita-python-mockが正常にインポートされました")
except ImportError:
    print("krita-python-mockがインストールされていません")
    print("pip install git+https://github.com/rbreu/krita-python-mock.git")
    sys.exit(1)

# プラグインディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'r_vertical_text'))

# PyQt5のインポート
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
except ImportError:
    print("PyQt5がインストールされていません")
    print("pip install PyQt5")
    sys.exit(1)

# プラグインのインポート
from r_vertical_text import VerticalTextDialog, RVerticalText

class TestVerticalTextDialog(unittest.TestCase):
    """VerticalTextDialogクラスのテスト"""
    
    def setUp(self):
        """テストの前準備"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.dialog = VerticalTextDialog()
    
    def tearDown(self):
        """テストの後処理"""
        if hasattr(self, 'dialog'):
            self.dialog.close()
    
    def test_dialog_initialization(self):
        """ダイアログの初期化テスト"""
        self.assertEqual(self.dialog.windowTitle(), "縦書きテキスト生成")
        self.assertEqual(self.dialog.text, "こんにちは\n世界")
        self.assertEqual(self.dialog.font_size, 24)
        self.assertEqual(self.dialog.line_spacing, 1.2)
        self.assertEqual(self.dialog.line_feed, 10)
        self.assertEqual(self.dialog.font_family, "Noto Serif CJK JP, Century, serif")
        self.assertEqual(self.dialog.text_color, QColor(0, 0, 0))
        self.assertFalse(self.dialog.force_monospace)
    
    def test_text_input_widget(self):
        """テキスト入力ウィジェットのテスト"""
        self.assertIsNotNone(self.dialog.text_input)
        self.assertEqual(self.dialog.text_input.toPlainText(), "こんにちは\n世界")
    
    def test_font_size_widget(self):
        """フォントサイズウィジェットのテスト"""
        self.assertIsNotNone(self.dialog.font_size_spin)
        self.assertEqual(self.dialog.font_size_spin.value(), 24)
        self.assertEqual(self.dialog.font_size_spin.minimum(), 8)
        self.assertEqual(self.dialog.font_size_spin.maximum(), 200)
    
    def test_line_spacing_widget(self):
        """行間ウィジェットのテスト"""
        self.assertIsNotNone(self.dialog.line_spacing_spin)
        self.assertEqual(self.dialog.line_spacing_spin.value(), 120)  # 1.2 * 100
        self.assertEqual(self.dialog.line_spacing_spin.minimum(), 50)
        self.assertEqual(self.dialog.line_spacing_spin.maximum(), 300)
    
    def test_line_feed_widget(self):
        """強制改行文字数ウィジェットのテスト"""
        self.assertIsNotNone(self.dialog.line_feed_spin)
        self.assertEqual(self.dialog.line_feed_spin.value(), 10)
        self.assertEqual(self.dialog.line_feed_spin.minimum(), 1)
        self.assertEqual(self.dialog.line_feed_spin.maximum(), 50)
    
    def test_font_family_widget(self):
        """フォントファミリーウィジェットのテスト"""
        self.assertIsNotNone(self.dialog.font_family_input)
        self.assertEqual(self.dialog.font_family_input.text(), "Noto Serif CJK JP, Century, serif")
    
    def test_color_selection(self):
        """色選択機能のテスト"""
        # 新しい色を設定
        new_color = QColor(255, 0, 0)  # 赤
        self.dialog.text_color = new_color
        self.dialog.color_label.setStyleSheet(f"background-color: {new_color.name()}; border: 1px solid black;")
        
        self.assertEqual(self.dialog.text_color, new_color)
        self.assertEqual(self.dialog.text_color.name(), "#ff0000")

class TestTextProcessing(unittest.TestCase):
    """テキスト処理機能のテスト"""
    
    def setUp(self):
        """テストの前準備"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.dialog = VerticalTextDialog()
    
    def tearDown(self):
        """テストの後処理"""
        if hasattr(self, 'dialog'):
            self.dialog.close()
    
    def test_split_text_into_lines_basic(self):
        """基本的なテキスト分割テスト"""
        text = "こんにちは世界"
        lines = self.dialog.splitTextIntoLines(text, 5)
        expected = ["こんにちは", "世界"]
        self.assertEqual(lines, expected)
    
    def test_split_text_into_lines_with_newlines(self):
        """改行文字を含むテキスト分割テスト"""
        text = "こんにちは\n世界\nテスト"
        lines = self.dialog.splitTextIntoLines(text, 10)
        expected = ["こんにちは", "世界", "テスト"]
        self.assertEqual(lines, expected)
    
    def test_split_text_into_lines_with_punctuation(self):
        """句読点を含むテキスト分割テスト"""
        text = "こんにちは。世界、テストです。"
        lines = self.dialog.splitTextIntoLines(text, 5)
        # 句読点は改行されない
        expected = ["こんにちは。", "世界、テストです。"]
        self.assertEqual(lines, expected)
    
    def test_split_text_into_lines_with_brackets(self):
        """括弧を含むテキスト分割テスト"""
        text = "こんにちは「世界」テスト『です』"
        lines = self.dialog.splitTextIntoLines(text, 5)
        # 括弧は改行されない
        expected = ["こんにちは「世界」", "テスト『です』"]
        self.assertEqual(lines, expected)
    
    def test_split_text_into_lines_empty(self):
        """空のテキスト分割テスト"""
        text = ""
        lines = self.dialog.splitTextIntoLines(text, 5)
        expected = []
        self.assertEqual(lines, expected)
    
    def test_split_text_into_lines_single_character(self):
        """単一文字のテキスト分割テスト"""
        text = "あ"
        lines = self.dialog.splitTextIntoLines(text, 5)
        expected = ["あ"]
        self.assertEqual(lines, expected)

class TestSVGGeneration(unittest.TestCase):
    """SVG生成機能のテスト"""
    
    def setUp(self):
        """テストの前準備"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.dialog = VerticalTextDialog()
    
    def tearDown(self):
        """テストの後処理"""
        if hasattr(self, 'dialog'):
            self.dialog.close()
    
    def test_generate_vertical_text_svg_basic(self):
        """基本的なSVG生成テスト"""
        text = "テスト"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = QColor(0, 0, 0)
        force_monospace = False
        
        svg_content = self.dialog.generateVerticalTextSVG(
            text, font_size, line_spacing, line_feed, 
            font_family, text_color, force_monospace
        )
        
        # SVGが生成されているかチェック
        self.assertIsInstance(svg_content, str)
        self.assertIn('<svg', svg_content)
        self.assertIn('</svg>', svg_content)
        
        # XMLとして解析可能かチェック
        try:
            root = ET.fromstring(svg_content)
            self.assertEqual(root.tag, 'svg')
        except ET.ParseError:
            self.fail("生成されたSVGが有効なXMLではありません")
    
    def test_generate_vertical_text_svg_multiline(self):
        """複数行のSVG生成テスト"""
        text = "テスト\n複数行"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = QColor(255, 0, 0)
        force_monospace = False
        
        svg_content = self.dialog.generateVerticalTextSVG(
            text, font_size, line_spacing, line_feed, 
            font_family, text_color, force_monospace
        )
        
        # SVGが生成されているかチェック
        self.assertIsInstance(svg_content, str)
        self.assertIn('<svg', svg_content)
        self.assertIn('</svg>', svg_content)
        
        # テキスト要素が含まれているかチェック
        self.assertIn('<text', svg_content)
        self.assertIn('テスト', svg_content)
        self.assertIn('複数行', svg_content)
    
    def test_generate_vertical_text_svg_with_monospace(self):
        """等幅フォント指定のSVG生成テスト"""
        text = "テスト"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = QColor(0, 0, 0)
        force_monospace = True
        
        svg_content = self.dialog.generateVerticalTextSVG(
            text, font_size, line_spacing, line_feed, 
            font_family, text_color, force_monospace
        )
        
        # 等幅フォント設定が含まれているかチェック
        self.assertIn('tabular-nums', svg_content)
    
    def test_generate_vertical_text_svg_color(self):
        """色指定のSVG生成テスト"""
        text = "テスト"
        font_size = 24
        line_spacing = 1.2
        line_feed = 10
        font_family = "Arial"
        text_color = QColor(255, 128, 64)  # オレンジ色
        force_monospace = False
        
        svg_content = self.dialog.generateVerticalTextSVG(
            text, font_size, line_spacing, line_feed, 
            font_family, text_color, force_monospace
        )
        
        # 色が正しく設定されているかチェック
        self.assertIn('#ff8040', svg_content)  # QColor(255, 128, 64)の16進表現

class TestRVerticalTextExtension(unittest.TestCase):
    """RVerticalText拡張機能のテスト"""
    
    def setUp(self):
        """テストの前準備"""
        # krita-python-mockを使用
        self.mock_krita = krita.Krita.instance()
        self.extension = RVerticalText(self.mock_krita)
    
    def test_extension_initialization(self):
        """拡張機能の初期化テスト"""
        self.assertIsNotNone(self.extension)
        self.assertEqual(self.extension.parent, self.mock_krita)
    
    def test_setup(self):
        """setup メソッドのテスト"""
        # setup メソッドが例外を発生させないことを確認
        try:
            self.extension.setup()
        except Exception as e:
            self.fail(f"setup メソッドが例外を発生させました: {e}")
    
    def test_create_actions(self):
        """createActions メソッドのテスト"""
        # モックウィンドウを作成
        mock_window = Mock()
        mock_action = Mock()
        mock_window.createAction.return_value = mock_action
        
        # createActions を実行
        self.extension.createActions(mock_window)
        
        # createAction が呼ばれたことを確認
        mock_window.createAction.assert_called_once()
        call_args = mock_window.createAction.call_args[0]
        self.assertEqual(call_args[0], "rVerticalText")
        self.assertEqual(call_args[1], "縦書きテキスト生成")
        self.assertEqual(call_args[2], "tools/scripts")
    
    @patch('r_vertical_text.r_vertical_text.VerticalTextDialog')
    def test_show_vertical_text_dialog(self, mock_dialog_class):
        """showVerticalTextDialog メソッドのテスト"""
        # モックダイアログを作成
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog
        
        # メソッドを実行
        self.extension.showVerticalTextDialog()
        
        # ダイアログが作成され、exec_ が呼ばれたことを確認
        mock_dialog_class.assert_called_once()
        mock_dialog.exec_.assert_called_once()

class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        """テストの前準備"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
    
    def test_full_workflow(self):
        """完全なワークフローのテスト"""
        # ダイアログを作成
        dialog = VerticalTextDialog()
        
        try:
            # テキストを設定
            dialog.text_input.setPlainText("縦書きテスト\n複数行")
            
            # フォントサイズを変更
            dialog.font_size_spin.setValue(32)
            
            # 色を変更
            dialog.text_color = QColor(0, 128, 255)
            
            # SVGを生成
            svg_content = dialog.generateVerticalTextSVG(
                dialog.text_input.toPlainText(),
                dialog.font_size_spin.value(),
                dialog.line_spacing_spin.value() / 100.0,
                dialog.line_feed_spin.value(),
                dialog.font_family_input.text(),
                dialog.text_color,
                dialog.force_monospace_check.isChecked()
            )
            
            # SVGが正しく生成されているかチェック
            self.assertIsInstance(svg_content, str)
            self.assertIn('<svg', svg_content)
            self.assertIn('縦書きテスト', svg_content)
            self.assertIn('複数行', svg_content)
            
            # XMLとして解析可能かチェック
            root = ET.fromstring(svg_content)
            self.assertEqual(root.tag, 'svg')
            
        finally:
            dialog.close()

def run_tests():
    """テストを実行"""
    print("縦書きテキストプラグインのテストを開始します...")
    print("=" * 60)
    
    # テストスイートを作成
    test_suite = unittest.TestSuite()
    
    # テストクラスを追加
    test_classes = [
        TestVerticalTextDialog,
        TestTextProcessing,
        TestSVGGeneration,
        TestRVerticalTextExtension,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ すべてのテストが成功しました！")
        return 0
    else:
        print("❌ 一部のテストが失敗しました")
        print(f"失敗: {len(result.failures)}, エラー: {len(result.errors)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
