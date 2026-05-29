#!/usr/bin/env python3
"""
generate_resume.py — 把结构化简历内容渲染成统一专业模板的 docx。

复刻「实习.skill」案例使用的简历模板视觉规格：
- 字体 Arial（中英文统一），窄页边距（适合一页装下）
- 姓名大字号居中 + 联系方式行
- "求职意向"定位头段落
- section 标题带底部分隔线（如「教育背景」「核心经历」）
- 经历条目：标题加粗 + 时间右对齐，下挂 bullet

输入：一个 JSON 文件（结构见 resume_schema 注释 / scripts/sample_resume.json）
输出：docx 文件

用法：
    python3 generate_resume.py <input.json> [-o output.docx]
"""
import sys
import json
import argparse
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Arial"
NAME_SIZE = 18      # 姓名
SECTION_SIZE = 12   # section 标题
BODY_SIZE = 10      # 正文
RIGHT_TAB_CM = 17.0  # 时间右对齐 tab 位置（按窄边距 A4 正文宽度）


def set_font(run, size=BODY_SIZE, bold=False, color=None):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    # 中文字体也设为 Arial（eastAsia）
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), FONT)
    rfonts.set(qn('w:ascii'), FONT)
    rfonts.set(qn('w:hAnsi'), FONT)


def add_bottom_border(paragraph):
    """给段落加底部分隔线（section 标题用）。"""
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '2')
    bottom.set(qn('w:color'), '000000')
    p_bdr.append(bottom)
    p_pr.append(p_bdr)


def tight(paragraph, before=2, after=2):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.05


def add_name(doc, name):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(p, 0, 2)
    set_font(p.add_run(name), NAME_SIZE, bold=True)


def add_contact(doc, contact):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(p, 0, 6)
    set_font(p.add_run(contact), BODY_SIZE)


def add_objective(doc, objective):
    """求职意向定位头。"""
    p = doc.add_paragraph()
    tight(p, 2, 6)
    r = p.add_run("求职意向：")
    set_font(r, BODY_SIZE, bold=True)
    set_font(p.add_run(objective), BODY_SIZE)


def add_section(doc, title):
    p = doc.add_paragraph()
    tight(p, 8, 3)
    set_font(p.add_run(title), SECTION_SIZE, bold=True)
    add_bottom_border(p)


def add_entry(doc, title, meta=None, subtitle=None, bullets=None):
    """一条经历：标题(加粗) + 右对齐 meta(时间/地点)，可选副标题，下挂 bullets。"""
    p = doc.add_paragraph()
    tight(p, 4, 1)
    if meta:
        # 设置右对齐 tab
        pf = p.paragraph_format
        tab_stops = pf.tab_stops
        tab_stops.add_tab_stop(Cm(RIGHT_TAB_CM), WD_TAB_ALIGNMENT.RIGHT)
        set_font(p.add_run(title), BODY_SIZE, bold=True)
        set_font(p.add_run("\t" + meta), BODY_SIZE)
    else:
        set_font(p.add_run(title), BODY_SIZE, bold=True)

    if subtitle:
        sp = doc.add_paragraph()
        tight(sp, 0, 1)
        set_font(sp.add_run(subtitle), BODY_SIZE)

    for b in (bullets or []):
        bp = doc.add_paragraph(style=None)
        tight(bp, 0, 1)
        bp.paragraph_format.left_indent = Cm(0.5)
        set_font(bp.add_run("• " + b), BODY_SIZE)


def add_skills(doc, skills):
    """skills: list of {category, content} 或 list of str。"""
    for item in skills:
        p = doc.add_paragraph()
        tight(p, 1, 1)
        if isinstance(item, dict):
            set_font(p.add_run(item["category"] + "："), BODY_SIZE, bold=True)
            set_font(p.add_run(item["content"]), BODY_SIZE)
        else:
            set_font(p.add_run("• " + item), BODY_SIZE)


def build(data, out_path):
    doc = Document()
    # 窄页边距
    for s in doc.sections:
        s.top_margin = Cm(1.5)
        s.bottom_margin = Cm(1.5)
        s.left_margin = Cm(1.9)
        s.right_margin = Cm(1.9)
    # 默认样式字体
    normal = doc.styles['Normal']
    normal.font.name = FONT
    normal.font.size = Pt(BODY_SIZE)

    add_name(doc, data["name"])
    add_contact(doc, data["contact"])
    if data.get("objective"):
        add_objective(doc, data["objective"])

    for section in data["sections"]:
        add_section(doc, section["title"])
        if section.get("type") == "skills":
            add_skills(doc, section["items"])
        else:
            for e in section["entries"]:
                add_entry(
                    doc,
                    title=e["title"],
                    meta=e.get("meta"),
                    subtitle=e.get("subtitle"),
                    bullets=e.get("bullets"),
                )

    doc.save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="生成统一模板的 docx 简历")
    ap.add_argument("input", help="结构化简历 JSON 文件")
    ap.add_argument("-o", "--output", help="输出 docx 路径")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    out = args.output or args.input.rsplit(".", 1)[0] + ".docx"
    build(data, out)
    print(f"✓ 已生成简历：{out}")


if __name__ == "__main__":
    main()
