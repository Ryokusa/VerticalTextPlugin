try:
    from krita import Extension, Krita
except ImportError:
    # Krita環境外でのテスト用
    class Extension:
        def __init__(self, parent):
            self.parent = parent
        def setup(self):
            pass
        def createActions(self, window):
            pass
    
    class Krita:
        @staticmethod
        def instance():
            return None

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QPushButton, 
                             QTextEdit, QCheckBox, QColorDialog, QGroupBox,
                             QFormLayout, QMessageBox, QRadioButton, QButtonGroup,
                             QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPixmap, QPainter, QFontDatabase
import xml.etree.ElementTree as ET

# PyQt5.QtSvgの可用性をチェック
try:
    import importlib.util
    spec = importlib.util.find_spec("PyQt5.QtSvg")
    QTSVG_AVAILABLE = spec is not None
    if QTSVG_AVAILABLE:
        print("PyQt5.QtSvg is available - SVG vector layer support enabled")
    else:
        print("PyQt5.QtSvg is not available - SVG vector layer support disabled")
except ImportError:
    QTSVG_AVAILABLE = False
    print("PyQt5.QtSvg is not available - SVG vector layer support disabled")

class VerticalTextDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("縦書きテキスト生成")
        self.setModal(True)
        self.resize(500, 700)
        
        # デフォルト値
        self.text = "こんにちは\n世界"
        self.font_size = 24
        self.line_spacing = 1.2
        self.char_spacing = 1.2  # 文字間隔（文字と文字の間のスペース）- 少し広めに設定
        self.line_feed = 10
        self.font_family = "Noto Serif CJK JP, Century, serif"
        self.font_weight = 400  # デフォルトのフォントウェイト
        self.text_color = QColor(0, 0, 0)
        self.force_monospace = False
        self.text_direction = "right_to_left"  # デフォルトは右から左
        
        # システムフォントを取得
        self.available_fonts = self.getSystemFonts()
        
        self.setupUI()
    
    def getSystemFonts(self):
        """システムにインストールされているフォントを取得"""
        try:
            font_db = QFontDatabase()
            families = font_db.families()
            
            # 日本語フォントを優先して並べ替え
            japanese_fonts = []
            other_fonts = []
            
            for family in families:
                if any(keyword in family.lower() for keyword in ['noto', 'source', 'hiragino', 'yu', 'meiryo', 'ms gothic', 'ms mincho', 'cjk', 'japanese']):
                    japanese_fonts.append(family)
                else:
                    other_fonts.append(family)
            
            # 日本語フォントを先頭に、その他をアルファベット順に
            sorted_fonts = sorted(japanese_fonts) + sorted(other_fonts)
            
            # デフォルトフォントを先頭に追加
            default_fonts = ["Noto Serif CJK JP", "Source Han Serif JP", "Hiragino Mincho ProN", "Yu Mincho", "MS Mincho"]
            final_fonts = []
            
            for default_font in default_fonts:
                if default_font in sorted_fonts:
                    final_fonts.append(default_font)
                    sorted_fonts.remove(default_font)
            
            final_fonts.extend(sorted_fonts)
            return final_fonts
            
        except Exception as e:
            print(f"フォント取得エラー: {e}")
            # フォールバック用のデフォルトフォントリスト
            return ["Noto Serif CJK JP", "Source Han Serif JP", "Hiragino Mincho ProN", "Yu Mincho", "MS Mincho", "serif", "sans-serif"]
    
    def detectFontWeight(self, font_name):
        """フォント名からフォントウェイトを検出"""
        font_name_lower = font_name.lower()
        
        # フォント名に含まれるウェイトキーワードを検出
        if any(keyword in font_name_lower for keyword in ['black', 'heavy', '900']):
            return 900
        elif any(keyword in font_name_lower for keyword in ['extra bold', 'ultra bold', '800']):
            return 800
        elif any(keyword in font_name_lower for keyword in ['bold', '700']):
            return 700
        elif any(keyword in font_name_lower for keyword in ['semi bold', 'demi bold', '600']):
            return 600
        elif any(keyword in font_name_lower for keyword in ['medium', '500']):
            return 500
        elif any(keyword in font_name_lower for keyword in ['regular', 'normal', '400']):
            return 400
        elif any(keyword in font_name_lower for keyword in ['light', '300']):
            return 300
        elif any(keyword in font_name_lower for keyword in ['extra light', 'ultra light', '200']):
            return 200
        elif any(keyword in font_name_lower for keyword in ['thin', '100']):
            return 100
        else:
            return 400  # デフォルト
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # テキスト入力グループ
        text_group = QGroupBox("テキスト設定")
        text_layout = QFormLayout()
        
        self.text_input = QTextEdit()
        self.text_input.setPlainText(self.text)
        self.text_input.setMaximumHeight(100)
        text_layout.addRow("テキスト:", self.text_input)
        
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # フォント設定グループ
        font_group = QGroupBox("フォント設定")
        font_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 200)
        self.font_size_spin.setValue(self.font_size)
        font_layout.addRow("フォントサイズ:", self.font_size_spin)
        
        # フォント選択用のComboBox
        self.font_family_combo = QComboBox()
        self.font_family_combo.setEditable(True)  # 手動入力も可能にする
        self.font_family_combo.addItems(self.available_fonts)
        
        # デフォルトフォントを設定
        default_index = self.font_family_combo.findText(self.font_family)
        if default_index >= 0:
            self.font_family_combo.setCurrentIndex(default_index)
        else:
            self.font_family_combo.setCurrentText(self.font_family)
        
        # フォント選択時のイベント接続
        self.font_family_combo.currentTextChanged.connect(self.onFontFamilyChanged)
        
        font_layout.addRow("フォントファミリー:", self.font_family_combo)
        
        # フォントウェイト選択用のComboBox
        self.font_weight_combo = QComboBox()
        self.font_weight_combo.addItem("Thin (100)", 100)
        self.font_weight_combo.addItem("Extra Light (200)", 200)
        self.font_weight_combo.addItem("Light (300)", 300)
        self.font_weight_combo.addItem("Regular (400)", 400)
        self.font_weight_combo.addItem("Medium (500)", 500)
        self.font_weight_combo.addItem("Semi Bold (600)", 600)
        self.font_weight_combo.addItem("Bold (700)", 700)
        self.font_weight_combo.addItem("Extra Bold (800)", 800)
        self.font_weight_combo.addItem("Black (900)", 900)
        
        # デフォルトウェイトを設定
        for i in range(self.font_weight_combo.count()):
            if self.font_weight_combo.itemData(i) == self.font_weight:
                self.font_weight_combo.setCurrentIndex(i)
                break
        
        # フォントウェイト選択時のイベント接続
        self.font_weight_combo.currentIndexChanged.connect(self.onFontWeightChanged)
        
        font_layout.addRow("フォントウェイト:", self.font_weight_combo)
        
        self.force_monospace_check = QCheckBox("強制的に等幅にする")
        self.force_monospace_check.setChecked(self.force_monospace)
        font_layout.addRow("", self.force_monospace_check)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # レイアウト設定グループ
        layout_group = QGroupBox("レイアウト設定")
        layout_layout = QFormLayout()
        
        self.line_spacing_spin = QSpinBox()
        self.line_spacing_spin.setRange(50, 300)
        self.line_spacing_spin.setValue(int(self.line_spacing * 100))
        self.line_spacing_spin.setSuffix("%")
        layout_layout.addRow("行間:", self.line_spacing_spin)
        
        self.char_spacing_spin = QSpinBox()
        self.char_spacing_spin.setRange(50, 200)
        self.char_spacing_spin.setValue(int(self.char_spacing * 100))
        self.char_spacing_spin.setSuffix("%")
        layout_layout.addRow("文字間隔:", self.char_spacing_spin)
        
        self.line_feed_spin = QSpinBox()
        self.line_feed_spin.setRange(1, 50)
        self.line_feed_spin.setValue(self.line_feed)
        layout_layout.addRow("強制改行文字数:", self.line_feed_spin)
        
        # テキスト方向設定
        direction_layout = QHBoxLayout()
        self.direction_button_group = QButtonGroup()
        
        self.direction_right_to_left = QRadioButton("右から左")
        self.direction_right_to_left.setChecked(self.text_direction == "right_to_left")
        self.direction_button_group.addButton(self.direction_right_to_left, 0)
        
        self.direction_left_to_right = QRadioButton("左から右")
        self.direction_left_to_right.setChecked(self.text_direction == "left_to_right")
        self.direction_button_group.addButton(self.direction_left_to_right, 1)
        
        direction_layout.addWidget(self.direction_right_to_left)
        direction_layout.addWidget(self.direction_left_to_right)
        direction_layout.addStretch()
        
        layout_layout.addRow("テキスト方向:", direction_layout)
        
        layout_group.setLayout(layout_layout)
        layout.addWidget(layout_group)
        
        # 色設定グループ
        color_group = QGroupBox("色設定")
        color_layout = QHBoxLayout()
        
        self.color_label = QLabel()
        self.color_label.setFixedSize(30, 30)
        self.color_label.setStyleSheet(f"background-color: {self.text_color.name()}; border: 1px solid black;")
        
        self.color_button = QPushButton("文字色を選択")
        self.color_button.clicked.connect(self.selectColor)
        
        color_layout.addWidget(QLabel("文字色:"))
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # プレビューグループ
        preview_group = QGroupBox("プレビュー")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(350)
        self.preview_label.setMinimumWidth(350)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(False)  # スケーリングを無効化してアスペクト比を保持
        
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("プレビュー更新")
        self.preview_button.clicked.connect(self.updatePreview)
        
        self.add_button = QPushButton("Kritaに追加")
        self.add_button.clicked.connect(self.addToKrita)
        
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.preview_button)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 初期プレビュー更新（UIの構築を完了させてから実行）
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(200, self.updatePreview)
        
        # さらに確実にするため、showEventでも更新
        self._initial_preview_done = False
    
    def onFontFamilyChanged(self, font_family):
        """フォントファミリーが変更された時のイベントハンドラー"""
        self.font_family = font_family
        
        # フォント名からウェイトを自動検出して設定
        detected_weight = self.detectFontWeight(font_family)
        self.font_weight = detected_weight
        
        # ウェイトコンボボックスの選択を更新
        for i in range(self.font_weight_combo.count()):
            if self.font_weight_combo.itemData(i) == detected_weight:
                self.font_weight_combo.setCurrentIndex(i)
                break
        
        # プレビューを自動更新
        self.updatePreview()
    
    def onFontWeightChanged(self, index):
        """フォントウェイトが変更された時のイベントハンドラー"""
        self.font_weight = self.font_weight_combo.itemData(index)
        # デバッグ情報を出力（開発時のみ）
        if hasattr(self, '_debug_mode') and self._debug_mode:
            print(f"フォントウェイト変更: {self.font_weight}")
        # プレビューを自動更新
        self.updatePreview()
    
    def showEvent(self, event):
        """ダイアログが表示された時のイベント"""
        super().showEvent(event)
        if not self._initial_preview_done:
            # 初期プレビューがまだ完了していない場合、更新
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self.updatePreview)
            self._initial_preview_done = True
        
    def logToFile(self, message):
        """デバッグ情報をファイルに出力"""
        try:
            import os
            import datetime
            
            # ログファイルのパス
            log_file = os.path.join(os.path.expanduser("~"), "krita_plugin_debug.log")
            
            # タイムスタンプ付きでログを出力
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_message)
                
        except Exception as e:
            print(f"ログファイル出力エラー: {e}")
    
    def selectColor(self):
        color = QColorDialog.getColor(self.text_color, self)
        if color.isValid():
            self.text_color = color
            self.color_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            # プレビューを自動更新
            self.updatePreview()
    
    def updatePreview(self):
        try:
            # 現在の設定を取得
            text = self.text_input.toPlainText()
            font_size = self.font_size_spin.value()
            line_spacing = self.line_spacing_spin.value() / 100.0
            char_spacing = self.char_spacing_spin.value() / 100.0
            line_feed = self.line_feed_spin.value()
            font_family = self.font_family_combo.currentText()
            font_weight = self.font_weight_combo.currentData()
            force_monospace = self.force_monospace_check.isChecked()
            
            # デバッグ情報を出力（開発時のみ）
            if hasattr(self, '_debug_mode') and self._debug_mode:
                print(f"プレビュー更新: フォント='{font_family}', ウェイト={font_weight}, サイズ={font_size}")
            
            # テキスト方向を取得
            if self.direction_right_to_left.isChecked():
                text_direction = "right_to_left"
            else:
                text_direction = "left_to_right"
            
            # SVGを生成
            svg_content = self.generateVerticalTextSVG(
                text, font_size, line_spacing, char_spacing, line_feed, 
                font_family, font_weight, self.text_color, force_monospace, text_direction
            )
            
            # プレビュー用のQPixmapを生成（プレビューラベルのサイズに合わせる）
            pixmap = self.svgToPixmap(svg_content, 350, 350, text_direction)
            
            # プレビューラベルに設定
            self.preview_label.setPixmap(pixmap)
            
            # プレビューラベルを更新（強制的に再描画）
            self.preview_label.update()
            self.preview_label.repaint()
            
            # アプリケーションのイベントループを処理
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            # デバッグ情報を出力（開発時のみ）
            if hasattr(self, '_debug_mode') and self._debug_mode:
                print(f"プレビュー更新完了: テキスト='{text}', ピクセマップサイズ={pixmap.width()}x{pixmap.height()}")
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"プレビューの生成に失敗しました: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def generateVerticalTextSVG(self, text, font_size, line_spacing, char_spacing, line_feed, 
                               font_family, font_weight, text_color, force_monospace, text_direction="right_to_left"):
        """縦書きテキストのSVGを生成"""
        
        # デバッグ出力（開発時のみ）
        if hasattr(self, '_debug_mode') and self._debug_mode:
            print(f"SVG生成 - フォントファミリー: '{font_family}'")
            self.logToFile(f"SVG生成 - フォントファミリー: '{font_family}'")
        
        # テキストを行に分割
        lines = self.splitTextIntoLines(text, line_feed)
        
        # フォント設定（フォールバック対応）
        # カンマ区切りのフォント名から最初のフォントのみを使用
        primary_font = font_family.split(',')[0].strip()
        
        # フォントウェイトは引数で受け取った値を使用
        
        # SVGでのフォント指定を改善
        # フォント名にスペースが含まれている場合は引用符で囲む
        if ' ' in primary_font:
            svg_font_family = f'"{primary_font}"'
        else:
            svg_font_family = primary_font
        
        # フォールバック用のフォントリストも追加
        if primary_font not in ['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy']:
            svg_font_family += ', serif'  # フォールバック用
            
        # デバッグ出力（開発時のみ）
        if hasattr(self, '_debug_mode') and self._debug_mode:
            print(f"SVG生成 - プライマリフォント: '{primary_font}'")
            print(f"SVG生成 - SVG用フォント名: '{svg_font_family}'")
            self.logToFile(f"SVG生成 - プライマリフォント: '{primary_font}'")
            self.logToFile(f"SVG生成 - SVG用フォント名: '{svg_font_family}'")
        
        # SVGのサイズを計算（縦書きレイアウト用）
        max_line_length = max(len(line) for line in lines) if lines else 1
        svg_width = len(lines) * font_size * line_spacing + 100  # 行数 × 行間 + マージン
        svg_height = max_line_length * font_size + 100  # 最長行の文字数 × フォントサイズ + マージン
        
        # SVGルート要素を作成
        svg = ET.Element("svg")
        svg.set("width", str(svg_width))
        svg.set("height", str(svg_height))
        svg.set("xmlns", "http://www.w3.org/2000/svg")
        svg.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
        
        # 背景（透明）
        rect = ET.SubElement(svg, "rect")
        rect.set("width", "100%")
        rect.set("height", "100%")
        rect.set("fill", "none")
        
        # 一つのtext要素を作成（縦書き用）
        text_elem = ET.SubElement(svg, "text")
        
        # 縦書き用の属性を設定
        text_elem.set("text-rendering", "auto")
        text_elem.set("fill", text_color.name())
        text_elem.set("stroke-opacity", "0")
        text_elem.set("stroke", "#000000")
        text_elem.set("stroke-width", "0")
        text_elem.set("stroke-linecap", "square")
        text_elem.set("stroke-linejoin", "bevel")
        text_elem.set("letter-spacing", "0")
        text_elem.set("word-spacing", "0")
        text_elem.set("writing-mode", "vertical-rl")
        
        # style属性を設定
        style_parts = [
            "text-align: start",
            "text-align-last: auto",
            f"font-family: {svg_font_family}",
            f"font-size: {font_size}",
            f"font-weight: {font_weight}"
        ]
        
        if force_monospace:
            style_parts.append("font-variant-numeric: tabular-nums")
        
        text_elem.set("style", "; ".join(style_parts))
        
        # 各行のテキストをtspanで配置
        for i, line in enumerate(lines):
            if not line.strip():  # 空行はスキップ
                continue
                
            # テキスト方向に応じてX座標を計算
            if text_direction == "right_to_left":
                # 右から左：最後の行から最初の行へ
                x_coord = 50 + (len(lines) - 1 - i) * font_size * line_spacing
            else:
                # 左から右：最初の行から最後の行へ
                x_coord = 50 + i * font_size * line_spacing
            
            # 最初の文字のY座標
            y_coord = 50 + font_size
            
            # 行のテキストを一つのtspanにまとめる
            tspan = ET.SubElement(text_elem, "tspan")
            tspan.set("x", str(x_coord))
            tspan.set("y", str(y_coord))
            tspan.text = line
            
            # 次の行のためにdx属性で位置調整（縦書きでは行間を調整）
            if i < len(lines) - 1:  # 最後の行でない場合
                next_tspan = ET.SubElement(text_elem, "tspan")
                next_tspan.set("y", "0")
                next_tspan.set("dx", f"-{int(font_size * line_spacing)}")
                next_tspan.text = ""  # 空のtspanで位置調整
        
        # 生成されたSVGの内容をデバッグ出力（開発時のみ）
        svg_content = ET.tostring(svg, encoding='unicode')
        if hasattr(self, '_debug_mode') and self._debug_mode:
            print(f"生成されたSVG（最初の500文字）: {svg_content[:500]}")
            self.logToFile(f"生成されたSVG（最初の500文字）: {svg_content[:500]}")
        
        return svg_content
    
    def splitTextIntoLines(self, text, line_feed):
        """テキストを行に分割（改行文字と強制改行を考慮）"""
        lines = []
        current_line = ""
        char_count = 0
        
        for char in text:
            if char == '\n':
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                    char_count = 0
            else:
                current_line += char
                char_count += 1
                
                # 強制改行文字数に達した場合
                if char_count >= line_feed:
                    # 句読点や括弧の場合は改行しない
                    if char not in ['。', '、', '」', '』']:
                        lines.append(current_line)
                        current_line = ""
                        char_count = 0
        
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def svgToPixmap(self, svg_content, width, height, text_direction="right_to_left"):
        """SVGコンテンツをQPixmapに変換"""
        # 簡単なプレビュー用の実装
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # フォント設定
        font = QFont()
        font.setFamily(self.font_family_combo.currentText())
        font.setPointSize(self.font_size_spin.value())
        font_weight = self.font_weight_combo.currentData()
        font.setWeight(font_weight)
        painter.setFont(font)
        
        # デバッグ情報を出力（開発時のみ）
        if hasattr(self, '_debug_mode') and self._debug_mode:
            print(f"プレビュー描画: フォント='{self.font_family_combo.currentText()}', ウェイト={font_weight}, サイズ={self.font_size_spin.value()}")
        painter.setPen(self.text_color)
        
        # テキストを描画
        text = self.text_input.toPlainText()
        lines = self.splitTextIntoLines(text, self.line_feed_spin.value())
        
        # フォント設定
        font_size = self.font_size_spin.value()
        line_spacing = self.line_spacing_spin.value() / 100.0
        char_spacing = self.char_spacing_spin.value() / 100.0
        
        # 縦書きテキストの描画
        # プレビューエリアの中央に配置するように計算
        total_lines = len(lines)
        max_line_length = max(len(line) for line in lines) if lines else 1
        
        # プレビューエリアの中央を計算
        preview_center_x = width // 2
        preview_center_y = height // 2
        
        # テキスト全体のサイズを計算
        total_text_width = total_lines * font_size * line_spacing
        total_text_height = max_line_length * font_size
        
        # テキストの開始位置を中央から計算
        start_x = preview_center_x - total_text_width // 2
        start_y = preview_center_y - total_text_height // 2
        
        # 各行のX座標を計算（縦書きでは行が横に並ぶ）
        if text_direction == "right_to_left":
            # 右から左：最後の行から最初の行へ
            x_offset = start_x + total_text_width - font_size * line_spacing
        else:
            # 左から右：最初の行から最後の行へ
            x_offset = start_x
            
        for i, line in enumerate(lines):
            y_offset = start_y
            for char in line:
                if char.strip():
                    # 縦書きでは文字を縦に配置
                    # フォントサイズを基準にした描画位置
                    draw_x = int(x_offset + font_size // 2)  # 文字の中央に配置（整数に変換）
                    draw_y = int(y_offset + font_size)  # ベースライン位置（整数に変換）
                    painter.drawText(draw_x, draw_y, char)
                    
                    y_offset += font_size * char_spacing  # 次の文字は下に配置（文字間隔を適用）
            
            # 次の行のX座標を計算（行間を考慮）
            # 行間は文字の幅 + 余白として計算
            # 最小行間を確保するため、フォントサイズの1.5倍以上にする
            min_line_width = int(font_size * 1.5)
            calculated_line_width = int(font_size * line_spacing)
            actual_line_width = max(min_line_width, calculated_line_width)
            
            if text_direction == "right_to_left":
                # 右から左：次の行は左に移動
                x_offset -= actual_line_width
            else:
                # 左から右：次の行は右に移動
                x_offset += actual_line_width
        
        painter.end()
        return pixmap
    
    def addToKrita(self):
        """生成したSVGをKritaに追加"""
        try:
            # 現在の設定を取得
            text = self.text_input.toPlainText()
            font_size = self.font_size_spin.value()
            line_spacing = self.line_spacing_spin.value() / 100.0
            char_spacing = self.char_spacing_spin.value() / 100.0
            line_feed = self.line_feed_spin.value()
            font_family = self.font_family_combo.currentText()
            font_weight = self.font_weight_combo.currentData()
            force_monospace = self.force_monospace_check.isChecked()
            
            # テキスト方向を取得
            if self.direction_right_to_left.isChecked():
                text_direction = "right_to_left"
            else:
                text_direction = "left_to_right"
            
            # アクティブなドキュメントを取得
            doc = Krita.instance().activeDocument()
            if doc is None:
                QMessageBox.warning(self, "エラー", "アクティブなドキュメントがありません。")
                return
            
            # 方法1: Krita 5のaddShapesFromSvgを使用してテキストを追加
            success = self.addTextWithKrita5SVG(doc, text, font_size, line_spacing, char_spacing, line_feed, font_family, font_weight, self.text_color, force_monospace, text_direction)
            
            # 方法1が失敗した場合、クリップボード経由でフォールバック
            if not success:
                print("addShapesFromSvgが失敗したため、クリップボード経由でフォールバックします")
                self.logToFile("addShapesFromSvgが失敗したため、クリップボード経由でフォールバックします")
                success = self.addTextViaClipboard(doc, text, font_size, line_spacing, char_spacing, line_feed, font_family, font_weight, self.text_color, force_monospace, text_direction)
            
            # 結果をユーザーに通知
            if success:
                QMessageBox.information(self, "成功", "縦書きテキストがKritaに追加されました。")
            else:
                QMessageBox.warning(self, "警告", "SVGの追加に失敗しました。Krita 5のベクターレイヤー機能が必要です。")
                
        except Exception as e:
            QMessageBox.critical(self, "エラー", "Kritaへの追加に失敗しました: " + str(e))
    
    
    
    
    
    def addTextWithKrita5SVG(self, doc, text, font_size, line_spacing, char_spacing, line_feed, font_family, font_weight, text_color, force_monospace, text_direction="right_to_left"):
        """Krita 5のaddShapesFromSvgを使用してテキストを追加（最も確実な方法）"""
        try:
            print("=== addTextWithKrita5SVG 開始 ===")
            self.logToFile("=== addTextWithKrita5SVG 開始 ===")
            
            # PyQt5.QtSvgが利用可能かチェック
            if not QTSVG_AVAILABLE:
                print("PyQt5.QtSvg is not available, skipping SVG method")
                self.logToFile("PyQt5.QtSvg is not available, skipping SVG method")
                return False
            
            print("PyQt5.QtSvg is available")
            self.logToFile("PyQt5.QtSvg is available")
            
            # SVGを生成
            svg_content = self.generateVerticalTextSVG(
                text, font_size, line_spacing, char_spacing, line_feed, 
                font_family, font_weight, text_color, force_monospace, text_direction
            )
            print(f"SVG生成完了: {len(svg_content)} 文字")
            self.logToFile(f"SVG生成完了: {len(svg_content)} 文字")
            
            # 新しいベクターレイヤーを作成
            root = doc.rootNode()
            print("ドキュメントのルートノードを取得")
            self.logToFile("ドキュメントのルートノードを取得")
            
            vector_layer = doc.createVectorLayer("縦書きテキスト")
            print("ベクターレイヤーを作成")
            self.logToFile("ベクターレイヤーを作成")
            
            root.addChildNode(vector_layer, None)
            print("ベクターレイヤーをルートに追加")
            self.logToFile("ベクターレイヤーをルートに追加")
            
            # レイヤーをアクティブにする
            doc.setActiveNode(vector_layer)
            print("ベクターレイヤーをアクティブに設定")
            self.logToFile("ベクターレイヤーをアクティブに設定")
            
            # Krita 5のaddShapesFromSvgメソッドを使用
            try:
                print(f"vector_layer.hasattr('addShapesFromSvg'): {hasattr(vector_layer, 'addShapesFromSvg')}")
                self.logToFile(f"vector_layer.hasattr('addShapesFromSvg'): {hasattr(vector_layer, 'addShapesFromSvg')}")
                
                if hasattr(vector_layer, 'addShapesFromSvg'):
                    print("addShapesFromSvgメソッドが利用可能です")
                    self.logToFile("addShapesFromSvgメソッドが利用可能です")
                    
                    # SVGコンテンツをベクターレイヤーに追加
                    vector_layer.addShapesFromSvg(svg_content)
                    print("addShapesFromSvgを実行しました")
                    self.logToFile("addShapesFromSvgを実行しました")
                    
                    # レイヤーを更新
                    vector_layer.updateProjection()
                    doc.refreshProjection()
                    print("レイヤーとドキュメントを更新しました")
                    self.logToFile("レイヤーとドキュメントを更新しました")
                    
                    print("Krita 5のaddShapesFromSvgでSVGを追加しました - 成功")
                    self.logToFile("Krita 5のaddShapesFromSvgでSVGを追加しました - 成功")
                    return True
                else:
                    print("addShapesFromSvgメソッドが利用できません")
                    self.logToFile("addShapesFromSvgメソッドが利用できません")
                    return False
                    
            except Exception as svg_error:
                print(f"addShapesFromSvgエラー: {svg_error}")
                self.logToFile(f"addShapesFromSvgエラー: {svg_error}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"Krita 5 SVG追加エラー: {e}")
            self.logToFile(f"Krita 5 SVG追加エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def addTextViaClipboard(self, doc, text, font_size, line_spacing, char_spacing, line_feed, font_family, font_weight, text_color, force_monospace, text_direction="right_to_left"):
        """クリップボード経由でテキストを追加（フォールバック方法）"""
        try:
            print("=== addTextViaClipboard 開始 ===")
            self.logToFile("=== addTextViaClipboard 開始 ===")
            
            # SVGを生成
            svg_content = self.generateVerticalTextSVG(
                text, font_size, line_spacing, char_spacing, line_feed, 
                font_family, font_weight, text_color, force_monospace, text_direction
            )
            print(f"SVG生成完了: {len(svg_content)} 文字")
            self.logToFile(f"SVG生成完了: {len(svg_content)} 文字")
            
            # クリップボードにSVGをコピー
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(svg_content)
            print("SVGをクリップボードにコピーしました")
            self.logToFile("SVGをクリップボードにコピーしました")
            
            # ユーザーに手順を表示
            message = """SVGがクリップボードにコピーされました。

Kritaに追加する手順:
1. Kritaで Ctrl+V を押してペースト
2. または「編集」→「ペースト」を選択

注意: この方法では、Kritaのペースト機能を使用してSVGを追加します。"""
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "クリップボードにコピー完了", message)
            
            print("addTextViaClipboard 成功")
            self.logToFile("addTextViaClipboard 成功")
            return True
            
        except Exception as e:
            print(f"addTextViaClipboardエラー: {e}")
            self.logToFile(f"addTextViaClipboardエラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    
    
    
    
    
    
    
    

class RVerticalText(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("rVerticalText", "縦書きテキスト生成", "tools/scripts")
        action.triggered.connect(self.showVerticalTextDialog)

    def showVerticalTextDialog(self):
        dialog = VerticalTextDialog()
        dialog.exec_()

# 拡張機能をKritaに追加
Krita.instance().addExtension(RVerticalText(Krita.instance()))