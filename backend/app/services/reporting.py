from html import escape


def build_report_html(
    title: str,
    metadata: dict[str, str],
    sections: list[dict[str, str]],
) -> str:
    metadata_rows = "\n".join(
        f"<tr><th>{escape(key)}</th><td>{escape(value)}</td></tr>"
        for key, value in metadata.items()
    )
    section_html = "\n".join(
        f"<section><h2>{escape(section['heading'])}</h2><p>{escape(section['body'])}</p></section>"
        for section in sections
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
</head>
<body>
  <h1>{escape(title)}</h1>
  <table>{metadata_rows}</table>
  {section_html}
</body>
</html>"""
