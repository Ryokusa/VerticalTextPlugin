#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フォントウェイト制御機能のテスト
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
from r_vertical_text.r_vertical_text import VerticalTextDialog

def test_weight_control():
    """フォントウェイト制御機能のテスト"""
    print("=== フォントウェイト制御機能のテスト ===")
    
    # QApplicationを作成（PyQt5のウィジェットを使用するため）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # ダイアログを作成
    dialog = VerticalTextDialog()
    
    # フォントウェイトコンボボックスの存在確認
    print("✓ フォントウェイトコンボボックスが存在することを確認")
    assert hasattr(dialog, 'font_weight_combo'), "フォントウェイトコンボボックスが存在しません"
    
    # デフォルト値の確認
    print("✓ デフォルトのフォントウェイトが400であることを確認")
    default_weight = dialog.font_weight_combo.currentData()
    assert default_weight == 400, f"デフォルトのフォントウェイトが400ではありません: {default_weight}"
    
    # フォントウェイトの変更テスト
    print("✓ フォントウェイトをBold (700)に変更")
    dialog.font_weight_combo.setCurrentIndex(6)  # Bold (700)
    new_weight = dialog.font_weight_combo.currentData()
    assert new_weight == 700, f"フォントウェイトが700に変更されていません: {new_weight}"
    
    # SVG生成テスト（異なるウェイトで）
    print("✓ 異なるフォントウェイトでSVG生成テスト")
    text = "テスト"
    font_size = 24
    line_spacing = 1.2
    char_spacing = 1.2
    line_feed = 10
    font_family = "Arial"
    font_weight = 700  # Bold
    text_color = QColor(0, 0, 0)
    force_monospace = False
    text_direction = "right_to_left"
    
    svg_content = dialog.generateVerticalTextSVG(
        text, font_size, line_spacing, char_spacing, line_feed,
        font_family, font_weight, text_color, force_monospace, text_direction
    )
    
    # SVGにフォントウェイトが含まれているかチェック
    assert 'font-weight: 700' in svg_content, "SVGにフォントウェイトが含まれていません"
    print("✓ SVGにフォントウェイトが正しく含まれていることを確認")
    
    # フォントファミリー変更時の自動ウェイト検出テスト
    print("✓ フォントファミリー変更時の自動ウェイト検出テスト")
    dialog.font_family_combo.setCurrentText("Arial Bold")
    # フォント名からウェイトが自動検出されることを確認
    detected_weight = dialog.detectFontWeight("Arial Bold")
    assert detected_weight == 700, f"フォント名からウェイトが正しく検出されていません: {detected_weight}"
    print("✓ フォント名からウェイトが正しく検出されることを確認")
    
    # プレビュー更新テスト
    print("✓ プレビュー更新テスト")
    dialog.updatePreview()
    print("✓ プレビューが正常に更新されることを確認")
    
    dialog.close()
    print("=== フォントウェイト制御機能のテスト完了 ===")
    print("✅ すべてのテストが成功しました！")

if __name__ == "__main__":
    test_weight_control()
