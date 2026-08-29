"""Shared page-shell contract for the static site."""

import posixpath

NAVIGATION_ITEMS = (
    ("home", "首页", "index.html"),
    ("about", "关于我们", "pages/about.html"),
    ("services", "服务", "pages/services.html"),
    ("contact", "加入我们", "pages/contact.html"),
)

PAGE_CONFIGS = {
    "index.html": {"title": "呼气之窝", "current": "home"},
    "pages/about.html": {"title": "呼气之窝 - 关于我们", "current": "about"},
    "pages/services.html": {"title": "呼气之窝 - 服务", "current": "services"},
    "pages/contact.html": {"title": "呼气之窝 - 加入我们", "current": "contact"},
    "pages/image-index.html": {"title": "呼气之窝 - 图片索引", "current": "services"},
}

SHARED_FOOTER_TEXT = (
    "© 2024 呼气之窝. 保留所有权利.",
    "版权所有,未经许可不得转载.",
    "收买h7不在版权考虑范围之内",
)


def relative_href(page_name, target_name):
    """Return a browser path from one generated page to a repository target."""
    page_directory = posixpath.dirname(page_name) or "."
    return posixpath.relpath(target_name, page_directory)


def expected_navigation(page_name):
    return tuple(
        (label, relative_href(page_name, target))
        for _, label, target in NAVIGATION_ITEMS
    )


def current_navigation_href(page_name):
    current_key = PAGE_CONFIGS[page_name]["current"]
    target = next(
        target for key, _, target in NAVIGATION_ITEMS if key == current_key
    )
    return relative_href(page_name, target)


def render_header(page_name):
    current_key = PAGE_CONFIGS[page_name]["current"]
    logo_href = relative_href(page_name, "image/logo.jpg")
    lines = [
        "    <!-- shared-header:start -->",
        '    <header class="header">',
        '        <button class="logo" type="button" aria-label="播放呼气之窝 Logo 动画">',
        f'            <img src="{logo_href}" alt="">',
        "            <span>呼气之窝</span>",
        "        </button>",
        '        <nav class="navigation" aria-label="主导航">',
        "            <ul>",
    ]
    for key, label, target in NAVIGATION_ITEMS:
        href = relative_href(page_name, target)
        current = ' aria-current="page"' if key == current_key else ""
        lines.append(
            f'                <li><a href="{href}"{current}>{label}</a></li>'
        )
    lines.extend(
        [
            "            </ul>",
            "        </nav>",
            "    </header>",
            "    <!-- shared-header:end -->",
        ]
    )
    return "\n".join(lines)


def render_footer():
    return "\n".join(
        [
            "    <!-- shared-footer:start -->",
            "    <footer>",
            "        <p>&copy; 2024 呼气之窝. 保留所有权利.</p>",
            "        <p>版权所有,未经许可不得转载.</p>",
            '        <p class="strikethrough">收买h7不在版权考虑范围之内</p>',
            "    </footer>",
            "    <!-- shared-footer:end -->",
        ]
    )
