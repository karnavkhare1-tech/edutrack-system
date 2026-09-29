"""Report Generator: Converts PROJECT_REPORT.md into a beautifully styled HTML file.

Allows easy single-click PDF export via browser 'Print -> Save as PDF' (Ctrl + P)
with proper print styles, page breaks, and cover page formatting.
"""

from pathlib import Path
import html
import re

BASE_DIR = Path(__file__).resolve().parent
REPORT_MD = BASE_DIR / "PROJECT_REPORT.md"
OUTPUT_HTML = BASE_DIR / "PROJECT_REPORT.html"


def convert_md_to_html():
    if not REPORT_MD.exists():
        print(f"Error: {REPORT_MD} not found.")
        return

    content = REPORT_MD.read_text(encoding="utf-8")

    # Simple clean markdown-to-HTML parser for standard elements
    lines = content.splitlines()
    html_lines = []
    in_code_block = False
    in_table = False
    table_header_done = False

    for line in lines:
        # Code blocks
        if line.startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                lang = line[3:].strip()
                html_lines.append(f'<pre class="code-block {lang}"><code>')
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(html.escape(line))
            continue

        # Tables
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c).issubset({"-", ":", " "}) for c in cells):
                # separator line
                table_header_done = True
                continue
            if not in_table:
                html_lines.append('<div class="table-container"><table>')
                in_table = True
                table_header_done = False

            tag = "th" if not table_header_done else "td"
            row_html = "".join(f"<{tag}>{html.escape(c)}</{tag}>" for c in cells)
            html_lines.append(f"<tr>{row_html}</tr>")
            continue
        elif in_table:
            html_lines.append("</table></div>")
            in_table = False
            table_header_done = False

        # Headers
        if line.startswith("# "):
            html_lines.append(f'<h1 class="report-title">{html.escape(line[2:])}</h1>')
        elif line.startswith("## "):
            html_lines.append(f'<h2 class="section-title">{html.escape(line[3:])}</h2>')
        elif line.startswith("### "):
            html_lines.append(f'<h3 class="subsection-title">{html.escape(line[4:])}</h3>')
        elif line.startswith("---"):
            html_lines.append('<hr class="divider"/>')
        elif line.startswith("- "):
            html_lines.append(f'<li>{html.escape(line[2:])}</li>')
        elif line.strip() == "":
            html_lines.append("<br/>")
        else:
            html_lines.append(f"<p>{html.escape(line)}</p>")

    if in_table:
        html_lines.append("</table></div>")
    if in_code_block:
        html_lines.append("</code></pre>")

    body = "\n".join(html_lines)

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EduTrack - Academic Project Report</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background: #ffffff;
        }}
        .report-title {{
            text-align: center;
            color: #0366d6;
            border-bottom: 3px solid #0366d6;
            padding-bottom: 12px;
            margin-bottom: 25px;
            font-size: 26px;
        }}
        .section-title {{
            color: #1a202c;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-top: 35px;
            font-size: 20px;
            page-break-after: avoid;
        }}
        .subsection-title {{
            color: #2d3748;
            margin-top: 20px;
            font-size: 16px;
            page-break-after: avoid;
        }}
        .code-block {{
            background: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 14px;
            overflow-x: auto;
            font-family: Consolas, "Courier New", monospace;
            font-size: 13px;
            line-height: 1.45;
            page-break-inside: avoid;
        }}
        .table-container {{
            margin: 15px 0;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th, td {{
            border: 1px solid #d1d5db;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background: #f3f4f6;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background: #f9fafb;
        }}
        .divider {{
            border: 0;
            border-top: 1px solid #e5e7eb;
            margin: 25px 0;
        }}
        li {{
            margin-bottom: 5px;
        }}
        @media print {{
            body {{
                padding: 0;
                max-width: 100%;
            }}
            .code-block, table {{
                page-break-inside: avoid;
            }}
            h2 {{
                page-break-before: auto;
            }}
        }}
    </style>
</head>
<body>
{body}
</body>
</html>
"""
    OUTPUT_HTML.write_text(html_document, encoding="utf-8")
    print(f"[Success] Generated styled report: {OUTPUT_HTML.resolve()}")
    print("[Tip] Open PROJECT_REPORT.html in your browser and press Ctrl+P -> 'Save as PDF' to generate your submission PDF!")


if __name__ == "__main__":
    convert_md_to_html()
