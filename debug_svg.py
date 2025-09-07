#!/usr/bin/env python3
"""
SVG生成のデバッグ
"""

import xml.etree.ElementTree as ET

def test_svg_generation():
    """SVG生成のテスト"""
    print("SVG生成テストを実行中...")
    
    # テキストを行に分割
    text = "テスト"
    lines = [text]  # 簡単なテスト
    
    # SVGのサイズを計算
    font_size = 24
    line_spacing = 1.2
    max_line_length = max(len(line) for line in lines) if lines else 1
    svg_width = max_line_length * font_size + 40
    svg_height = len(lines) * font_size * line_spacing + 40
    
    print(f"SVGサイズ: {svg_width} x {svg_height}")
    
    # SVGルート要素を作成
    svg = ET.Element("svg")
    svg.set("width", str(svg_width))
    svg.set("height", str(svg_height))
    svg.set("xmlns", "http://www.w3.org/2000/svg")
    svg.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    
    print("SVG要素作成完了")
    
    # 背景（透明）
    rect = ET.SubElement(svg, "rect")
    rect.set("width", "100%")
    rect.set("height", "100%")
    rect.set("fill", "none")
    
    print("背景要素作成完了")
    
    # テキスト要素を追加
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            if char.strip():  # 空白文字以外
                text_elem = ET.SubElement(svg, "text")
                text_elem.set("x", str(20 + j * font_size))
                text_elem.set("y", str(30 + i * font_size * line_spacing))
                text_elem.set("font-size", str(font_size))
                text_elem.set("font-family", "Arial")
                text_elem.set("fill", "#000000")
                text_elem.set("text-anchor", "middle")
                text_elem.set("dominant-baseline", "central")
                text_elem.text = char
                print(f"テキスト要素追加: {char}")
    
    print("テキスト要素作成完了")
    
    # SVGを文字列に変換
    svg_content = ET.tostring(svg, encoding='unicode')
    print(f"SVGコンテンツ長: {len(svg_content)}")
    print(f"SVGコンテンツ: {svg_content}")
    
    # XMLとして解析可能かテスト
    try:
        root = ET.fromstring(svg_content)
        print(f"ルート要素タグ: {root.tag}")
        print(f"ルート要素属性: {root.attrib}")
        
        # テキスト要素の存在確認（名前空間を考慮）
        text_elements = root.findall(".//{http://www.w3.org/2000/svg}text")
        print(f"テキスト要素数: {len(text_elements)}")
        
        for i, elem in enumerate(text_elements):
            print(f"テキスト要素{i}: {elem.text} at ({elem.get('x')}, {elem.get('y')})")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ SVG解析エラー: {e}")
        return False

if __name__ == "__main__":
    test_svg_generation()
