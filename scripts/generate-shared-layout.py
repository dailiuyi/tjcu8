"""Generate shared headers and footers without changing page-specific content."""

import re
from pathlib import Path

from site_layout import PAGE_CONFIGS, render_footer, render_header

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
HEADER_PATTERN = re.compile(r'    <header class="header">.*?</header>', re.DOTALL)
FOOTER_PATTERN = re.compile(r"    <footer>.*?</footer>", re.DOTALL)


def replace_generated_block(
    html, start_marker, end_marker, fallback_pattern, content
):
    if start_marker in html or end_marker in html:
        if html.count(start_marker) != 1 or html.count(end_marker) != 1:
            raise ValueError(
                f"expected one marker pair: {start_marker}, {end_marker}"
            )
        prefix, remainder = html.split(start_marker, 1)
        _, suffix = remainder.split(end_marker, 1)
        return f"{prefix}{content}{suffix}"

    updated, count = fallback_pattern.subn(content, html, count=1)
    if count != 1:
        raise ValueError(f"could not find initial block for {start_marker}")
    return updated


def generate_page(page_name):
    page_path = REPOSITORY_ROOT / page_name
    raw_html = page_path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw_html else "\n"
    html = raw_html.decode("utf-8")

    header = render_header(page_name).replace("\n", newline)
    footer = render_footer().replace("\n", newline)
    html = replace_generated_block(
        html,
        "    <!-- shared-header:start -->",
        "    <!-- shared-header:end -->",
        HEADER_PATTERN,
        header,
    )
    html = replace_generated_block(
        html,
        "    <!-- shared-footer:start -->",
        "    <!-- shared-footer:end -->",
        FOOTER_PATTERN,
        footer,
    )
    page_path.write_bytes(html.encode("utf-8"))


def main():
    for page_name in PAGE_CONFIGS:
        generate_page(page_name)
    print(f"Generated shared layout for {len(PAGE_CONFIGS)} pages.")


if __name__ == "__main__":
    main()
