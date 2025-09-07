#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなプレビュー更新テスト
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
from r_vertical_text.r_vertical_text import VerticalTextDialog

def test_simple_preview():
    """シンプルなプレビュー更新テスト"""
    print("=== シンプルなプレビュー更新テスト ===")
    
    # QApplicationを作成
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # ダイアログを作成
    dialog = VerticalTextDialog()
    
    print("✓ ダイアログの初期化完了")
    
    # 初期プレビュー更新
    print("✓ 初期プレビュー更新を実行")
    dialog.updatePreview()
    
    # フォントウェイトを変更
    print("✓ フォントウェイトをBold (700)に変更")
    dialog.font_weight_combo.setCurrentIndex(6)  # Bold (700)
    
    # 手動でプレビュー更新
    print("✓ 手動でプレビュー更新を実行")
    dialog.updatePreview()
    
    # 結果を確認
    current_weight = dialog.font_weight_combo.currentData()
    print(f"✓ 現在のフォントウェイト: {current_weight}")
    
    if dialog.preview_label.pixmap() is not None:
        print("✓ プレビューラベルにピクセマップが設定されています")
        print(f"  ピクセマップサイズ: {dialog.preview_label.pixmap().width()}x{dialog.preview_label.pixmap().height()}")
    else:
        print("❌ プレビューラベルにピクセマップが設定されていません")
    
    # フォントウェイトをLight (300)に変更
    print("✓ フォントウェイトをLight (300)に変更")
    dialog.font_weight_combo.setCurrentIndex(2)  # Light (300)
    
    # 再度プレビュー更新
    print("✓ 再度プレビュー更新を実行")
    dialog.updatePreview()
    
    # 結果を確認
    current_weight = dialog.font_weight_combo.currentData()
    print(f"✓ 現在のフォントウェイト: {current_weight}")
    
    if dialog.preview_label.pixmap() is not None:
        print("✓ 2回目のプレビューラベルにピクセマップが設定されています")
        print(f"  ピクセマップサイズ: {dialog.preview_label.pixmap().width()}x{dialog.preview_label.pixmap().height()}")
    else:
        print("❌ 2回目のプレビューラベルにピクセマップが設定されていません")
    
    dialog.close()
    print("=== シンプルなプレビュー更新テスト完了 ===")

if __name__ == "__main__":
    test_simple_preview()
