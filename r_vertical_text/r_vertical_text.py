from krita import *
from PyQt5.QtWidgets import QFileDialog

class RVerticalText(Extension):

    def __init__(self, parent):
        # これは親クラスを初期化します。サブクラス化の際に重要です。
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("rVerticalText", "私のスクリプト", "tools/scripts")
        action.triggered.connect(self.exportDocument)

    def exportDocument(self):
        # ドキュメントを取得します:
        doc =  Krita.instance().activeDocument()
        # 存在しないドキュメントを保存するとクラッシュします。ですからまずそれを確認します。
        if doc is not None:
            # これによって保存ダイアログを呼び出します。保存ダイアログはタプル値を返します
            fileName = QFileDialog.getSaveFileName()[0]
            # そしてドキュメントを fileName で指定した場所にエクスポートします。
            # InfoObject は特定のエクスポートオプションに関する辞書ですが、空の辞書を渡すと Krita はデフォルトのオプションを用います。
            doc.exportImage(fileName, InfoObject())

# そして拡張機能を Krita の拡張機能一覧に追加します:
Krita.instance().addExtension(RVerticalText(Krita.instance()))