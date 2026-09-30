"""
EduTrack - Premium PDF Report Generator
Converts PROJECT_REPORT.md into a beautifully styled, print-ready HTML,
then saves it as PROJECT_REPORT_FINAL.html for browser PDF printing.
"""

from pathlib import Path
import html
import re

BASE_DIR = Path(__file__).resolve().parent
REPORT_MD = BASE_DIR / "PROJECT_REPORT.md"
OUTPUT_HTML = BASE_DIR / "PROJECT_REPORT_FINAL.html"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --primary: #1e3a5f;
    --accent: #2563eb;
    --accent-light: #dbeafe;
    --success: #059669;
    --text: #1a1a2e;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --bg-code: #f8fafc;
    --bg-table-head: #1e3a5f;
    --white: #ffffff;
    --shadow: 0 1px 3px rgba(0,0,0,0.1);
}

@page {
    size: A4;
    margin: 18mm 15mm 18mm 15mm;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 10.5pt;
    line-height: 1.7;
    color: var(--text);
    background: var(--white);
    max-width: 820px;
    margin: 0 auto;
    padding: 40px 50px;
}

/* ── COVER PAGE ── */
.cover-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 95vh;
    text-align: center;
    page-break-after: always;
    padding: 40px 30px;
}

.cover-logo-bar {
    width: 100%;
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    border-radius: 12px;
    padding: 28px 30px;
    margin-bottom: 36px;
}

.cover-logo-bar h1 {
    color: white;
    font-size: 22pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.cover-logo-bar p {
    color: rgba(255,255,255,0.85);
    font-size: 10pt;
    font-weight: 400;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.cover-badge {
    display: inline-block;
    background: var(--accent-light);
    color: var(--accent);
    border: 1px solid #93c5fd;
    border-radius: 20px;
    padding: 5px 18px;
    font-size: 9pt;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 20px;
}

.cover-title {
    font-size: 20pt;
    font-weight: 700;
    color: var(--primary);
    line-height: 1.3;
    margin-bottom: 8px;
}

.cover-subtitle {
    font-size: 11pt;
    color: var(--text-muted);
    margin-bottom: 40px;
}

.cover-divider {
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, #2563eb, #1e3a5f);
    border-radius: 2px;
    margin: 20px auto 36px auto;
}

.cover-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    width: 100%;
    max-width: 600px;
    margin-bottom: 36px;
}

.cover-info-card {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px;
    text-align: left;
}

.cover-info-card .label {
    font-size: 7.5pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--accent);
    margin-bottom: 4px;
}

.cover-info-card .value {
    font-size: 10.5pt;
    font-weight: 600;
    color: var(--primary);
}

.cover-info-card .value-sub {
    font-size: 8.5pt;
    color: var(--text-muted);
    margin-top: 2px;
}

.cover-footer {
    margin-top: auto;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    width: 100%;
    font-size: 8.5pt;
    color: var(--text-muted);
}

/* ── SECTION HEADINGS ── */
h1.report-title {
    font-size: 16pt;
    font-weight: 700;
    color: var(--primary);
    border-bottom: 3px solid var(--accent);
    padding-bottom: 10px;
    margin: 30px 0 20px 0;
    page-break-after: avoid;
}

h2.section-title {
    font-size: 13pt;
    font-weight: 700;
    color: var(--white);
    background: linear-gradient(135deg, var(--primary) 0%, #2563eb 100%);
    padding: 10px 18px;
    border-radius: 8px;
    margin: 36px 0 16px 0;
    page-break-after: avoid;
}

h3.subsection-title {
    font-size: 11pt;
    font-weight: 600;
    color: var(--primary);
    border-left: 4px solid var(--accent);
    padding-left: 12px;
    margin: 22px 0 10px 0;
    page-break-after: avoid;
}

h4.subsubsection-title {
    font-size: 10pt;
    font-weight: 600;
    color: var(--text);
    margin: 16px 0 8px 0;
}

/* ── PARAGRAPHS & LISTS ── */
p {
    margin-bottom: 10px;
    line-height: 1.7;
}

ul, ol {
    margin: 8px 0 12px 24px;
}

li {
    margin-bottom: 5px;
    line-height: 1.6;
}

strong {
    font-weight: 600;
    color: var(--primary);
}

em {
    font-style: italic;
    color: var(--text-muted);
}

/* ── CODE BLOCKS ── */
pre.code-block {
    background: var(--bg-code);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 16px 18px;
    overflow-x: auto;
    font-family: 'JetBrains Mono', Consolas, 'Courier New', monospace;
    font-size: 8.5pt;
    line-height: 1.55;
    margin: 12px 0 16px 0;
    page-break-inside: avoid;
    white-space: pre-wrap;
    word-break: break-word;
}

code {
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 8.5pt;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 4px;
    padding: 1px 5px;
    color: #1d4ed8;
}

/* ── TABLES ── */
.table-container {
    margin: 14px 0 18px 0;
    page-break-inside: avoid;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9pt;
}

th {
    background: var(--bg-table-head);
    color: var(--white);
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 8.5pt;
    letter-spacing: 0.3px;
}

td {
    padding: 9px 14px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}

tr:nth-child(even) td { background: #f8fafc; }
tr:last-child td { border-bottom: none; }

/* ── DIVIDER ── */
hr.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
}

/* ── HIGHLIGHT BOX ── */
.highlight-box {
    background: var(--accent-light);
    border-left: 4px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 14px 0;
    font-size: 9.5pt;
}

/* ── STATS GRID ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin: 20px 0;
}

.stat-card {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

.stat-card .stat-value {
    font-size: 20pt;
    font-weight: 700;
    color: var(--accent);
    display: block;
}

.stat-card .stat-label {
    font-size: 8pt;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 4px;
}

/* ── ARCHITECTURE DIAGRAM ── */
.arch-diagram {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
    page-break-inside: avoid;
}

.arch-layer {
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
    text-align: center;
}

.arch-layer h4 { font-size: 9pt; font-weight: 700; margin-bottom: 3px; }
.arch-layer p  { font-size: 8pt; opacity: 0.85; margin: 0; }

.layer-presentation { background: #1d4ed8; color: white; }
.layer-service       { background: #0891b2; color: white; }
.layer-model         { background: #059669; color: white; }
.layer-storage       { background: #7c3aed; color: white; }
.layer-utils         { background: #b45309; color: white; }

.arch-arrow {
    text-align: center;
    color: #94a3b8;
    font-size: 14pt;
    margin: 2px 0;
    line-height: 1;
}

/* ── GRADE BADGE ── */
.grade-table td:last-child { font-weight: 700; color: var(--success); }

/* ── TEST PASS BADGE ── */
.pass-badge {
    display: inline-block;
    background: #d1fae5;
    color: #065f46;
    border: 1px solid #6ee7b7;
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 8pt;
    font-weight: 600;
}

/* ── FOOTER ── */
.page-footer {
    border-top: 2px solid var(--accent);
    margin-top: 50px;
    padding-top: 16px;
    text-align: center;
    font-size: 8pt;
    color: var(--text-muted);
}

/* ── PRINT ── */
@media print {
    body { padding: 0; max-width: 100%; }
    .cover-page { min-height: 100vh; }
    pre.code-block, table, .arch-diagram, .stats-grid { page-break-inside: avoid; }
    h2.section-title { page-break-before: auto; }
}
"""

COVER_HTML = """
<div class="cover-page">
    <div class="cover-logo-bar">
        <h1>VELLORE INSTITUTE OF TECHNOLOGY</h1>
        <p>School of Computer Science and Engineering (SCOPE)</p>
    </div>

    <span class="cover-badge">Flipped Course Evaluation — Project Report</span>

    <h2 class="cover-title">EduTrack</h2>
    <p class="cover-subtitle">Student Academic Performance &amp; Attendance Monitoring System</p>
    <div class="cover-divider"></div>

    <div class="stats-grid" style="max-width:520px; margin-bottom:32px;">
        <div class="stat-card">
            <span class="stat-value">16</span>
            <span class="stat-label">Unit Tests Passed</span>
        </div>
        <div class="stat-card">
            <span class="stat-value">12</span>
            <span class="stat-label">Python Modules</span>
        </div>
        <div class="stat-card">
            <span class="stat-value">5</span>
            <span class="stat-label">Core Modules</span>
        </div>
    </div>

    <div class="cover-info-grid">
        <div class="cover-info-card">
            <div class="label">Student Name</div>
            <div class="value">Karnav Khare</div>
        </div>
        <div class="cover-info-card">
            <div class="label">Registration Number</div>
            <div class="value">26BMR10033</div>
        </div>
        <div class="cover-info-card">
            <div class="label">Program</div>
            <div class="value">B.Tech Mechanical Engineering</div>
            <div class="value-sub">AI &amp; Robotics (Megatronics)</div>
        </div>
        <div class="cover-info-card">
            <div class="label">Academic Year</div>
            <div class="value">2026 – 2027</div>
            <div class="value-sub">Semester 1</div>
        </div>
        <div class="cover-info-card">
            <div class="label">Course</div>
            <div class="value">CSE1001</div>
            <div class="value-sub">Problem Solving &amp; Programming with Python</div>
        </div>
        <div class="cover-info-card">
            <div class="label">Supervisor / Evaluator</div>
            <div class="value">Devendra Kumar Vedi</div>
            <div class="value-sub">SCOPE, VIT</div>
        </div>
    </div>

    <div class="cover-footer">
        EduTrack &nbsp;·&nbsp; Academic Project Report &nbsp;·&nbsp; VIT &nbsp;·&nbsp; 2026
    </div>
</div>
"""

ARCH_HTML = """
<div class="arch-diagram">
    <div class="arch-layer layer-presentation">
        <h4>🖥️ PRESENTATION LAYER</h4>
        <p>edutrack/cli/menu.py &nbsp;·&nbsp; main.py &nbsp;·&nbsp; demo.py &nbsp;·&nbsp; edutrack/web/</p>
    </div>
    <div class="arch-arrow">▼</div>
    <div class="arch-layer layer-service">
        <h4>⚙️ SERVICE / BUSINESS LOGIC LAYER</h4>
        <p>StudentService &nbsp;·&nbsp; CourseService &nbsp;·&nbsp; AttendanceService &nbsp;·&nbsp; AnalyticsService</p>
    </div>
    <div class="arch-arrow">▼</div>
    <div class="arch-layer layer-model">
        <h4>🏗️ DOMAIN MODEL LAYER</h4>
        <p>Person (Base) → Faculty &nbsp;·&nbsp; Student → CourseRecord &nbsp;·&nbsp; Course</p>
    </div>
    <div class="arch-arrow">▼</div>
    <div class="arch-layer layer-storage">
        <h4>💾 PERSISTENCE LAYER</h4>
        <p>DataStorage &nbsp;·&nbsp; JSON Serializer &nbsp;·&nbsp; CSV Exporter</p>
    </div>
    <div class="arch-arrow">▼</div>
    <div class="arch-layer layer-utils">
        <h4>🛡️ UTILITY / VALIDATION LAYER</h4>
        <p>RegEx Validators &nbsp;·&nbsp; Custom Exception Hierarchy</p>
    </div>
</div>
"""


def inline_format(text: str) -> str:
    """Apply inline markdown formatting: bold, italic, inline code."""
    text = html.escape(text)
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code: `text`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Math: $$...$$ or $...$ — strip delimiters, show plain
    text = re.sub(r'\$\$(.+?)\$\$', r'<em>\1</em>', text)
    text = re.sub(r'\$(.+?)\$', r'<em>\1</em>', text)
    return text


def convert_md_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    out = []
    in_code = False
    in_ul = False
    in_table = False
    table_header_done = False
    skip_cover = True  # we skip the raw cover-page code block and inject our own

    i = 0
    while i < len(lines):
        line = lines[i]

        # ── Skip original cover-page code block (lines 7-35 range) ──
        if skip_cover and line.strip() == "```" and i < 40:
            # find closing ```
            j = i + 1
            while j < len(lines) and not lines[j].strip() == "```":
                j += 1
            i = j + 1
            skip_cover = False
            out.append(ARCH_HTML)   # will be repositioned; placeholder here
            continue

        # ── Code fences ──
        if line.startswith("```"):
            if in_ul:
                out.append("</ul>"); in_ul = False
            if in_table:
                out.append("</table></div>"); in_table = False
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                lang = line[3:].strip()
                cls = f"code-block {lang}" if lang else "code-block"
                out.append(f'<pre class="{cls}"><code>')
                in_code = True
            i += 1
            continue

        if in_code:
            out.append(html.escape(line))
            i += 1
            continue

        # ── Tables ──
        if line.startswith("|") and "|" in line[1:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.match(r'^[-: ]+$', c) for c in cells if c):
                table_header_done = True
                i += 1
                continue
            if not in_table:
                if in_ul:
                    out.append("</ul>"); in_ul = False
                out.append('<div class="table-container"><table>')
                in_table = True
                table_header_done = False
            tag = "th" if not table_header_done else "td"
            row = "".join(f"<{tag}>{inline_format(c)}</{tag}>" for c in cells)
            out.append(f"<tr>{row}</tr>")
            i += 1
            continue
        elif in_table:
            out.append("</table></div>")
            in_table = False
            table_header_done = False

        # ── Close lists before headings / dividers ──
        if in_ul and (line.startswith("#") or line.startswith("---") or line.strip() == ""):
            out.append("</ul>"); in_ul = False

        # ── Headings ──
        if line.startswith("#### "):
            out.append(f'<h4 class="subsubsection-title">{inline_format(line[5:])}</h4>')
        elif line.startswith("### "):
            text = line[4:]
            # Inject architecture diagram after section 6 heading
            out.append(f'<h3 class="subsection-title">{inline_format(text)}</h3>')
        elif line.startswith("## "):
            out.append(f'<h2 class="section-title">{inline_format(line[3:])}</h2>')
        elif line.startswith("# "):
            out.append(f'<h1 class="report-title">{inline_format(line[2:])}</h1>')
        elif line.startswith("---"):
            out.append('<hr class="divider"/>')
        elif re.match(r'^- ', line):
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline_format(line[2:])}</li>")
        elif re.match(r'^\d+\. ', line):
            if not in_ul:
                out.append("<ol>"); in_ul = True
            out.append(f"<li>{inline_format(re.sub(r'^\d+\. ', '', line))}</li>")
        elif line.strip() == "":
            out.append("<br/>")
        else:
            out.append(f"<p>{inline_format(line)}</p>")

        i += 1

    if in_ul:   out.append("</ul>")
    if in_table: out.append("</table></div>")
    if in_code:  out.append("</code></pre>")

    return "\n".join(out)


def build_html(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>EduTrack – Project Report | Karnav Khare | 26BMR10033</title>
<style>{CSS}</style>
</head>
<body>

{COVER_HTML}

{body}

<div class="page-footer">
    EduTrack Academic Project Report &nbsp;·&nbsp; Karnav Khare (26BMR10033) &nbsp;·&nbsp;
    B.Tech Mechanical Engineering in AI &amp; Robotics (Megatronics) &nbsp;·&nbsp; VIT 2026–27
</div>

</body>
</html>"""


def main():
    if not REPORT_MD.exists():
        print(f"[Error] {REPORT_MD} not found.")
        return

    md_text = REPORT_MD.read_text(encoding="utf-8", errors="replace")
    body_html = convert_md_to_html(md_text)
    final_html = build_html(body_html)
    OUTPUT_HTML.write_text(final_html, encoding="utf-8")
    print(f"[✓] HTML generated: {OUTPUT_HTML}")
    print("[→] Opening in browser to save as PDF...")


if __name__ == "__main__":
    main()
