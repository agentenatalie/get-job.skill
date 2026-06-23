# scripts

## generate_resume.py

把结构化的简历内容（JSON）渲染成统一专业模板的 docx。这是 Phase 2「简历重写」定稿后的出件工具——内容由 skill 按 `references/resume-rewrite-framework.md` 改好，脚本只负责排版。

### 依赖

```bash
pip3 install python-docx
```

### 用法

```bash
python3 generate_resume.py <input.json> [-o output.docx]
```

例：
```bash
python3 generate_resume.py my_resume.json -o 张三_某公司_产品实习.docx
```

### 模板视觉规格（已固定在脚本里）

- 字体：Aptos + 微软雅黑（现代无衬线，兼顾中英文）
- 页边距：窄边距（A4，适合一页装下）
- 姓名：18pt 居中加粗，使用克制品牌色
- 联系方式：一行居中，弱化为灰色
- 求职意向：顶部定位头段落（`objective` 字段）
- section 标题：12pt 加粗 + 品牌色底部分隔线
- 经历条目：标题加粗 + 时间右对齐 tab，下挂 `•` bullet；副标题弱化为灰色斜体
- 技能区：「类别：内容」加粗类别名

### 输入 JSON 结构

见同目录 `sample_resume.json`。骨架：

```json
{
  "name": "姓名",
  "contact": "电话 | 邮箱 | 城市",
  "objective": "求职意向定位头（见 resume-rewrite-framework.md 的 Step 3）",
  "sections": [
    {
      "title": "教育背景",
      "entries": [
        {"title": "学校 — 学位", "meta": "时间", "subtitle": "方向", "bullets": []}
      ]
    },
    {
      "title": "核心经历",
      "entries": [
        {"title": "公司 — 项目名", "meta": "时间/地点", "subtitle": "职位", "bullets": ["要点1", "要点2"]}
      ]
    },
    {
      "title": "技能",
      "type": "skills",
      "items": [
        {"category": "类别名", "content": "技能列表"}
      ]
    }
  ]
}
```

字段说明：
- `entries[].title` 建议填写；缺失时脚本会用占位标题并输出 warning；`meta`（右对齐时间/地点）、`subtitle`（职位/方向）、`bullets` 可选
- section 加 `"type": "skills"` 时用 `items`（`{category, content}` 或纯字符串列表），否则用 `entries`
- 经历可少量、自然地加入迁移叙事（见改简历框架），脚本不强制
- 脚本会自动移除 bullet 开头误泄漏的 `迁移句:`、`迁移说明:`、`可迁移性:` 标签，避免标签词直接出现在正式简历里

### 容错行为

脚本会尽量生成可检查的 docx，而不是遇到小缺口直接崩掉：
- 缺 `name` / `contact`：使用占位文本，并在 stderr 输出 warning
- 缺 `sections` 或结构错误：生成"信息待补"占位区
- section / entry / skill item 结构不合法：跳过该项并输出 warning
- bullet 不是数组：自动当作单条 bullet 处理

这些容错只保证排版工具不中断，不代表内容已完整；正式投递前仍要按 skill 的可靠性协议补齐缺口。

### 转 PDF（可选）

docx 转 PDF：
```bash
# macOS，需装 LibreOffice
soffice --headless --convert-to pdf <resume>.docx
# 或用环境里的 pdf / docx skill
```
