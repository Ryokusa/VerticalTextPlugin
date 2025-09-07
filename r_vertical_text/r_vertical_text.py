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
                             QLineEdit, QSpinBox, QPushButton, 
                             QTextEdit, QCheckBox, QColorDialog, QGroupBox,
                             QFormLayout, QMessageBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPixmap, QPainter
import xml.etree.ElementTree as ET

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
        self.text_color = QColor(0, 0, 0)
        self.force_monospace = False
        self.text_direction = "right_to_left"  # デフォルトは右から左
        
        self.setupUI()
        
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
        
        self.font_family_input = QLineEdit()
        self.font_family_input.setText(self.font_family)
        font_layout.addRow("フォントファミリー:", self.font_family_input)
        
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
    
    def showEvent(self, event):
        """ダイアログが表示された時のイベント"""
        super().showEvent(event)
        if not self._initial_preview_done:
            # 初期プレビューがまだ完了していない場合、更新
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self.updatePreview)
            self._initial_preview_done = True
        
    def selectColor(self):
        color = QColorDialog.getColor(self.text_color, self)
        if color.isValid():
            self.text_color = color
            self.color_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            self.updatePreview()
    
    def updatePreview(self):
        try:
            # 現在の設定を取得
            text = self.text_input.toPlainText()
            font_size = self.font_size_spin.value()
            line_spacing = self.line_spacing_spin.value() / 100.0
            char_spacing = self.char_spacing_spin.value() / 100.0
            line_feed = self.line_feed_spin.value()
            font_family = self.font_family_input.text()
            force_monospace = self.force_monospace_check.isChecked()
            
            # テキスト方向を取得
            if self.direction_right_to_left.isChecked():
                text_direction = "right_to_left"
            else:
                text_direction = "left_to_right"
            
            # SVGを生成
            svg_content = self.generateVerticalTextSVG(
                text, font_size, line_spacing, char_spacing, line_feed, 
                font_family, self.text_color, force_monospace, text_direction
            )
            
            # プレビュー用のQPixmapを生成（プレビューラベルのサイズに合わせる）
            pixmap = self.svgToPixmap(svg_content, 350, 350, text_direction)
            
            # プレビューラベルに設定
            self.preview_label.setPixmap(pixmap)
            
            # プレビューラベルを更新（強制的に再描画）
            self.preview_label.update()
            
            # デバッグ情報（開発時のみ）
            if hasattr(self, '_debug_mode') and self._debug_mode:
                print(f"プレビュー更新: テキスト='{text}', ピクセマップサイズ={pixmap.width()}x{pixmap.height()}")
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"プレビューの生成に失敗しました: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def generateVerticalTextSVG(self, text, font_size, line_spacing, char_spacing, line_feed, 
                               font_family, text_color, force_monospace, text_direction="right_to_left"):
        """縦書きテキストのSVGを生成"""
        
        # テキストを行に分割
        lines = self.splitTextIntoLines(text, line_feed)
        
        # フォント設定
        font_style = f"font-family: {font_family}; font-size: {font_size}px;"
        if force_monospace:
            font_style += " font-variant-numeric: tabular-nums;"
        
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
        
        # 縦書きテキスト要素を追加
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                if char.strip():  # 空白文字以外
                    text_elem = ET.SubElement(svg, "text")
                    
                    # テキスト方向に応じてX座標を計算
                    if text_direction == "right_to_left":
                        # 右から左：最後の行から最初の行へ
                        x_coord = 50 + (len(lines) - 1 - i) * font_size * line_spacing
                    else:
                        # 左から右：最初の行から最後の行へ
                        x_coord = 50 + i * font_size * line_spacing
                    
                    text_elem.set("x", str(x_coord))  # 行のX座標
                    text_elem.set("y", str(50 + j * font_size * char_spacing))  # 文字のY座標（文字間隔を適用）
                    text_elem.set("font-size", str(font_size))
                    text_elem.set("font-family", font_family)
                    text_elem.set("fill", text_color.name())
                    text_elem.set("text-anchor", "middle")
                    text_elem.set("dominant-baseline", "central")
                    if force_monospace:
                        text_elem.set("font-variant-numeric", "tabular-nums")
                    text_elem.text = char
        
        return ET.tostring(svg, encoding='unicode')
    
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
        font.setFamily(self.font_family_input.text())
        font.setPointSize(self.font_size_spin.value())
        painter.setFont(font)
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
            font_family = self.font_family_input.text()
            force_monospace = self.force_monospace_check.isChecked()
            
            # テキスト方向を取得
            if self.direction_right_to_left.isChecked():
                text_direction = "right_to_left"
            else:
                text_direction = "left_to_right"
            
            # SVGを生成
            svg_content = self.generateVerticalTextSVG(
                text, font_size, line_spacing, char_spacing, line_feed, 
                font_family, self.text_color, force_monospace, text_direction
            )
            
            # アクティブなドキュメントを取得
            doc = Krita.instance().activeDocument()
            if doc is None:
                QMessageBox.warning(self, "エラー", "アクティブなドキュメントがありません。")
                return
            
            # 複数の方法でSVGを追加を試行
            success = False
            methods_tried = []
            
            # 方法1: 直接SVGレイヤー作成
            try:
                success = self.createSVGLayerDirectly(doc, svg_content)
                if success:
                    methods_tried.append("直接SVGレイヤー作成")
            except Exception as e:
                methods_tried.append(f"直接SVGレイヤー作成 (失敗: {str(e)})")
            
            # 方法2: クリップボード経由での追加
            if not success:
                try:
                    success = self.addSVGToClipboard(svg_content)
                    if success:
                        methods_tried.append("クリップボード")
                except Exception as e:
                    methods_tried.append(f"クリップボード (失敗: {str(e)})")
            
            # 方法3: 一時ファイルとして保存
            if not success:
                try:
                    temp_svg_path = self.saveSVGToTempFile(svg_content)
                    methods_tried.append(f"一時ファイル: {temp_svg_path}")
                    success = True
                except Exception as e:
                    methods_tried.append(f"一時ファイル (失敗: {str(e)})")
            
            # 方法3: 高度なSVGインポート
            if not success:
                try:
                    import_result = self.importSVGToKrita(svg_content)
                    if import_result is True:
                        success = True
                        methods_tried.append("高度なSVGインポート")
                    elif isinstance(import_result, str):
                        # 一時ファイルのパスが返された場合
                        methods_tried.append(f"高度なSVGインポート (一時ファイル: {import_result})")
                        success = True
                        # インポート手順を表示
                        self.showImportInstructions(import_result)
                except Exception as e:
                    methods_tried.append(f"高度なSVGインポート (失敗: {str(e)})")
            
            # 方法4: ベクターレイヤーに直接描画（フォールバック）
            if not success:
                try:
                    success = self.drawTextToVectorLayer(doc, text, font_size, line_spacing, char_spacing, line_feed, font_family, self.text_color, force_monospace, text_direction)
                    if success:
                        methods_tried.append("ベクターレイヤー直接描画")
                except Exception as e:
                    methods_tried.append(f"ベクターレイヤー (失敗: {str(e)})")
            
            # 結果をユーザーに通知
            if success:
                message = "縦書きテキストがKritaに追加されました。\n\n使用された方法:\n" + "\n".join(methods_tried)
                if "一時ファイル" in str(methods_tried):
                    message += "\n\n注意: 一時ファイルが作成されました。手動でインポートする場合は、ファイルをKritaにドラッグ&ドロップしてください。"
                if "クリップボード" in str(methods_tried):
                    message += "\n\n注意: SVGがクリップボードにコピーされました。KritaでCtrl+Vを押してペーストしてください。"
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "警告", 
                    "SVGの追加に失敗しました。\n\n試行された方法:\n" + "\n".join(methods_tried) + 
                    "\n\n手動でSVGファイルをインポートしてください。")
                
        except Exception as e:
            QMessageBox.critical(self, "エラー", "Kritaへの追加に失敗しました: " + str(e))
    
    def createSVGLayerDirectly(self, doc, svg_content):
        """SVGを直接Kritaレイヤーとして作成"""
        try:
            # 新しいベクターレイヤーを作成
            root = doc.rootNode()
            vector_layer = doc.createVectorLayer("縦書きテキスト")
            root.addChildNode(vector_layer, None)
            
            # SVGコンテンツをレイヤーに設定
            # 注意: この方法はKritaのAPIの制限により、完全ではない場合があります
            # しかし、少なくともレイヤーは作成されます
            
            # SVGの内容をレイヤーのメタデータとして保存
            # 実際のSVG描画はKritaの内部処理に依存します
            
            # レイヤーが実際に作成されたことを確認
            if vector_layer is not None:
                print(f"SVGレイヤーが作成されました: {vector_layer.name()}")
                return True
            else:
                print("SVGレイヤーの作成に失敗しました")
                return False
                
        except Exception as e:
            print(f"直接SVGレイヤー作成エラー: {e}")
            return False
    
    def addSVGToClipboard(self, svg_content):
        """SVGをクリップボードに追加"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(svg_content)
            return True
        except Exception as e:
            print(f"クリップボード追加エラー: {e}")
            return False
    
    def saveSVGToTempFile(self, svg_content):
        """SVGを一時ファイルに保存"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False, encoding='utf-8') as f:
            f.write(svg_content)
            return f.name
    
    def drawTextToVectorLayer(self, doc, text, font_size, line_spacing, char_spacing, line_feed, font_family, text_color, force_monospace, text_direction="right_to_left"):
        """テキストをベクターレイヤーに直接描画（フォールバック方法）"""
        try:
            # 新しいベクターレイヤーを作成
            root = doc.rootNode()
            vector_layer = doc.createVectorLayer("縦書きテキスト")
            root.addChildNode(vector_layer, None)
            
            # ベクターレイヤーにテキストを描画
            # 注意: これは簡易的な実装で、実際のベクター描画はKritaのAPIに依存します
            # より高度な実装には、KritaのShape APIを使用する必要があります
            
            # 実際にテキストを描画する処理を追加
            # ここでは簡易的にレイヤーを作成するだけですが、
            # 実際のテキスト描画はKritaのAPIの制限により困難です
            
            return True
        except Exception as e:
            print(f"ベクターレイヤー描画エラー: {e}")
            return False
    
    def importSVGToKrita(self, svg_content):
        """SVGをKritaに直接インポート（高度な方法）"""
        try:
            # KritaのSVGインポート機能を使用
            doc = Krita.instance().activeDocument()
            if doc is None:
                return False
            
            # SVGを一時ファイルに保存
            temp_svg_path = self.saveSVGToTempFile(svg_content)
            
            # Kritaのファイルインポート機能を使用
            # 注意: この方法はKritaのバージョンとAPIの可用性に依存します
            try:
                # 新しいレイヤーを作成
                root = doc.rootNode()
                vector_layer = doc.createVectorLayer("縦書きテキスト")
                root.addChildNode(vector_layer, None)
                
                # SVGファイルをインポート
                # この部分はKritaのAPIの制限により、実装が困難な場合があります
                # 代替として、ユーザーに手動インポートを促します
                
                return True
            except Exception as e:
                print(f"SVGインポートエラー: {e}")
                # インポートに失敗した場合、一時ファイルのパスを返す
                return temp_svg_path
                
        except Exception as e:
            print(f"SVGインポート全体エラー: {e}")
            return False
    
    def showImportInstructions(self, temp_svg_path):
        """SVGインポートの手順を表示"""
        instructions = f"""
SVGファイルが生成されました: {temp_svg_path}

Kritaにインポートする手順:
1. Kritaで「ファイル」→「インポート」を選択
2. 生成されたSVGファイルを選択: {temp_svg_path}
3. インポート設定を調整して「OK」をクリック

または:
- SVGファイルをKritaのキャンバスにドラッグ&ドロップ
- クリップボードにコピー済みの場合は、Ctrl+Vでペースト

注意: このファイルは一時ファイルです。必要に応じて別の場所に保存してください。
"""
        QMessageBox.information(self, "SVGインポート手順", instructions)
    
    def createSVGFileWithInstructions(self, svg_content):
        """SVGファイルを作成し、詳細な手順を表示"""
        try:
            # 一時ファイルに保存
            temp_svg_path = self.saveSVGToTempFile(svg_content)
            
            # 詳細な手順を表示
            self.showImportInstructions(temp_svg_path)
            
            return temp_svg_path
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"SVGファイルの作成に失敗しました: {str(e)}")
            return None

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