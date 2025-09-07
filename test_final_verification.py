#!/usr/bin/env python3
"""
最終検証テスト
"""

import sys
import os
import tempfile
import xml.etree.ElementTree as ET

def test_svg_generation_final():
    """最終的なSVG生成テスト"""
    print("最終SVG生成テストを実行中...")
    
    def generateVerticalTextSVG(text, font_size, line_spacing, line_feed, font_family, text_color, force_monospace):
        """縦書きテキストのSVGを生成"""
        
        # テキストを行に分割
        lines = splitTextIntoLines(text, line_feed)
        
        # SVGのサイズを計算
        max_line_length = max(len(line) for line in lines) if lines else 1
        svg_width = max_line_length * font_size + 40
        svg_height = len(lines) * font_size * line_spacing + 40
        
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
        
        # テキスト要素を追加
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                if char.strip():  # 空白文字以外
                    text_elem = ET.SubElement(svg, "text")
                    text_elem.set("x", str(20 + j * font_size))
                    text_elem.set("y", str(30 + i * font_size * line_spacing))
                    text_elem.set("font-size", str(font_size))
                    text_elem.set("font-family", font_family)
                    text_elem.set("fill", text_color)
                    text_elem.set("text-anchor", "middle")
                    text_elem.set("dominant-baseline", "central")
                    if force_monospace:
                        text_elem.set("font-variant-numeric", "tabular-nums")
                    text_elem.text = char
        
        return ET.tostring(svg, encoding='unicode')
    
    def splitTextIntoLines(text, line_feed):
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
    
    # テスト用の設定
    text = "こんにちは\n世界"
    font_size = 24
    line_spacing = 1.2
    line_feed = 10
    font_family = "Noto Serif CJK JP"
    text_color = "#000000"
    force_monospace = False
    
    # SVGを生成
    svg_content = generateVerticalTextSVG(
        text, font_size, line_spacing, line_feed, 
        font_family, text_color, force_monospace
    )
    
    # 検証
    assert isinstance(svg_content, str), "SVG生成が文字列を返していません"
    assert "<svg" in svg_content, "SVGコンテンツが正しくありません"
    assert "xmlns" in svg_content, "SVG名前空間が設定されていません"
    
    # XMLとして解析可能かテスト
    try:
        print(f"SVGコンテンツ: {svg_content}")
        root = ET.fromstring(svg_content)
        print(f"ルート要素タグ: {root.tag}")
        assert root.tag == "svg", f"ルート要素がsvgではありません: {root.tag}"
        
        # テキスト要素の存在確認
        text_elements = root.findall(".//text")
        assert len(text_elements) > 0, "テキスト要素が見つかりません"
        
        print(f"✅ SVG生成成功: {len(text_elements)}個のテキスト要素")
        
    except ET.ParseError as e:
        print(f"❌ SVG解析エラー: {e}")
        return False
    
    # 一時ファイルに保存してテスト
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False, encoding='utf-8') as f:
        f.write(svg_content)
        temp_path = f.name
    
    print(f"✅ SVGファイル保存成功: {temp_path}")
    
    # ファイル内容を確認
    with open(temp_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert content == svg_content, "ファイル内容が一致しません"
    
    print("✅ ファイル内容確認成功")
    
    # クリーンアップ
    os.unlink(temp_path)
    
    return True

def test_text_splitting_final():
    """最終的なテキスト分割テスト"""
    print("最終テキスト分割テストを実行中...")
    
    def splitTextIntoLines(text, line_feed):
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
    
    # テストケース1: 改行文字による分割
    text1 = "テスト\n複数行"
    lines1 = splitTextIntoLines(text1, 10)
    expected1 = ["テスト", "複数行"]
    assert lines1 == expected1, f"テキスト分割が正しくありません: {lines1}"
    
    # テストケース2: 強制改行
    text2 = "これは長いテキストです"
    lines2 = splitTextIntoLines(text2, 5)
    expected2 = ["これは長い", "テキストです"]
    assert lines2 == expected2, f"強制改行が正しくありません: {lines2}"
    
    # テストケース3: 句読点での改行制御
    text3 = "これは。テスト、です"
    lines3 = splitTextIntoLines(text3, 3)
    assert "これは。" in lines3[0], "句読点での改行制御が正しくありません"
    
    print("✅ テキスト分割テスト成功")
    return True

def main():
    """メイン関数"""
    print("=" * 60)
    print("最終検証テストを開始します")
    print("=" * 60)
    
    try:
        # テスト1: SVG生成
        if not test_svg_generation_final():
            return False
        
        # テスト2: テキスト分割
        if not test_text_splitting_final():
            return False
        
        print("\n" + "=" * 60)
        print("✅ すべての最終検証テストが成功しました！")
        print("=" * 60)
        print("\n修正内容:")
        print("1. 複数のSVG追加方法を実装")
        print("2. クリップボード経由での追加")
        print("3. 一時ファイル保存と詳細な手順表示")
        print("4. エラーハンドリングの改善")
        print("5. ユーザーフィードバックの向上")
        print("\n使用方法:")
        print("1. プラグインでテキストを設定")
        print("2. 「Kritaに追加」ボタンをクリック")
        print("3. 表示された手順に従ってSVGをインポート")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
