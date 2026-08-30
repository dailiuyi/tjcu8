"""Validate local site references and the generated image index."""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from site_layout import (
    PAGE_CONFIGS,
    SHARED_FOOTER_TEXT,
    current_navigation_href,
    expected_navigation,
)

CONTRACT_VERSION = 1
IMAGE_FIELDS = {"id", "src", "album", "caption", "alt"}
SUPPORTED_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png"}
IGNORED_SOURCE_DIRECTORIES = {"dist", "node_modules"}

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
IMAGE_ROOT = REPOSITORY_ROOT / "image"
INDEX_PATH = REPOSITORY_ROOT / "pages" / "json" / "image_index.json"
CSS_ROOT = REPOSITORY_ROOT / "css"
CSS_ENTRY_PATH = CSS_ROOT / "style.css"
CSS_MODULES = (
    "base.css",
    "layout.css",
    "components.css",
    "pages.css",
    "responsive.css",
)
CSS_REQUIRED_MARKERS = {
    "base.css": ("body {", ".visually-hidden {"),
    "layout.css": (
        "[data-vue-shell] {",
        ".header {",
        ".logo:focus-visible {",
        ".navigation a {",
        "footer {",
    ),
    "components.css": (".box,", ".image-gallery {", ".body-text {"),
    "pages.css": (".link-list {", ".services-list {"),
    "responsive.css": (
        "@media (prefers-reduced-motion: reduce)",
        ".logo:hover img {",
        "@media (max-width: 768px)",
    ),
}
JS_ROOT = REPOSITORY_ROOT / "js"
SHARED_JS_ENTRY_PATH = JS_ROOT / "script.js"
SHARED_JS_MODULE_PATH = JS_ROOT / "logo-animation.js"
SHARED_LAYOUT_JS_PATH = JS_ROOT / "shared-layout.js"
SHARED_LAYOUT_CONFIG_PATH = JS_ROOT / "shared-layout" / "config.js"
SHARED_LAYOUT_COMPONENT_PATHS = (
    JS_ROOT / "components" / "SiteHeader.vue",
    JS_ROOT / "components" / "SiteFooter.vue",
)
IMAGE_INDEX_JS_ENTRY_PATH = JS_ROOT / "image-index.js"
IMAGE_INDEX_JS_IMPORTS = (
    "./image-index/data.js",
    "./image-index/gallery.js",
    "./image-index/preview.js",
)
IMAGE_INDEX_JS_REQUIRED_MARKERS = {
    "./image-index/data.js": (
        "export function validateImageIndex",
        "export async function loadImageIndex",
        "image.src.startsWith('../image/')",
    ),
    "./image-index/gallery.js": (
        "export function renderGallery",
        "export function showGalleryError",
        "link.rel = 'noopener noreferrer'",
        "link.setAttribute('aria-controls', 'preview')",
    ),
    "./image-index/preview.js": (
        "export function createPreviewController",
        "function bindLink",
        "link.addEventListener('mouseenter'",
        "link.addEventListener('mousemove'",
        "link.addEventListener('mouseleave'",
        "link.addEventListener('focus'",
        "link.addEventListener('blur'",
        "link.addEventListener('keydown'",
    ),
}


PAGE_TITLES = {
    page_name: config["title"] for page_name, config in PAGE_CONFIGS.items()
}
PAGE_LAYOUTS = {
    page_name: {
        "links": expected_navigation(page_name),
        "current": current_navigation_href(page_name),
    }
    for page_name in PAGE_CONFIGS
}


class ReferenceParser(HTMLParser):
    """Collect local href and src attributes from an HTML document."""

    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if name in {"href", "src"} and value:
                self.references.append((tag, name, value))


class AccessibilityParser(HTMLParser):
    """Collect page metadata, headings, and image alternatives."""

    def __init__(self):
        super().__init__()
        self.lang = None
        self.in_title = False
        self.title_parts = []
        self.main_labels = []
        self.headings = []
        self.images = []
        self.contact_sections = []

    def handle_starttag(self, tag, attributes):
        attribute_map = dict(attributes)
        classes = set(attribute_map.get("class", "").split())
        if tag == "html":
            self.lang = attribute_map.get("lang")
        elif tag == "title":
            self.in_title = True
        elif tag == "main":
            self.main_labels.append(attribute_map.get("aria-labelledby"))
        elif len(tag) == 2 and tag[0] == "h" and tag[1].isdigit():
            self.headings.append((int(tag[1]), attribute_map.get("id"), classes))
        elif tag == "img":
            self.images.append((attribute_map.get("src"), attribute_map.get("alt"), attribute_map.get("id")))
        if "contact-section" in classes:
            self.contact_sections.append((tag, attribute_map.get("aria-label")))

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    @property
    def title(self):
        return " ".join("".join(self.title_parts).split())


class ServicesStructureParser(HTMLParser):
    """Inspect the services page module boundaries."""

    def __init__(self):
        super().__init__()
        self.main_classes = []
        self.services_content = []
        self.service_items = []
        self.heading_ids = set()
        self.construction_notices = []
        self.nested_content_count = 0

    def handle_starttag(self, tag, attributes):
        attribute_map = dict(attributes)
        classes = set(attribute_map.get("class", "").split())

        if tag == "main":
            self.main_classes.append(classes)
        elif "content" in classes:
            self.nested_content_count += 1
        if "services-content" in classes:
            self.services_content.append(
                (tag, attribute_map.get("aria-labelledby"))
            )
        if "service-item" in classes:
            self.service_items.append(
                (tag, attribute_map.get("aria-labelledby"))
            )
        if tag in {"h2", "h3"} and attribute_map.get("id"):
            self.heading_ids.add(attribute_map["id"])
        if "construction-notice" in classes:
            self.construction_notices.append(
                (tag, attribute_map.get("aria-label"))
            )


class AboutStructureParser(HTMLParser):
    """Inspect the semantic content groups on the about page."""

    def __init__(self):
        super().__init__()
        self.main_classes = []
        self.about_content_count = 0
        self.image_group_count = 0
        self.body_text_sections = []
        self.legacy_layout_classes = []
        self.empty_paragraph_count = 0
        self.current_paragraph = None

    def handle_starttag(self, tag, attributes):
        attribute_map = dict(attributes)
        classes = set(attribute_map.get("class", "").split())

        if tag == "main":
            self.main_classes.append(classes)
        if "about-content" in classes:
            self.about_content_count += 1
        if "about-image-group" in classes:
            self.image_group_count += 1
        if classes.intersection({"contact", "box"}):
            self.legacy_layout_classes.extend(sorted(classes.intersection({"contact", "box"})))
        if "body-text" in classes:
            self.body_text_sections.append((tag, attribute_map.get("aria-label")))
        if tag == "p":
            self.current_paragraph = []

    def handle_data(self, data):
        if self.current_paragraph is not None:
            self.current_paragraph.append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self.current_paragraph is not None:
            if not "".join(self.current_paragraph).strip():
                self.empty_paragraph_count += 1
            self.current_paragraph = None


class LayoutParser(HTMLParser):
    """Collect the shared page shell used by every formal page."""

    def __init__(self):
        super().__init__()
        self.tag_counts = {"header": 0, "main": 0, "footer": 0}
        self.navigation_label = None
        self.navigation_links = []
        self.footer_paragraphs = []
        self.logo_controls = []
        self.vue_shells = []
        self.in_navigation = False
        self.in_footer = False
        self.current_link = None
        self.current_footer_paragraph = None

    def handle_starttag(self, tag, attributes):
        attribute_map = dict(attributes)
        classes = set(attribute_map.get("class", "").split())

        if attribute_map.get("data-vue-shell"):
            self.vue_shells.append(
                (
                    tag,
                    attribute_map.get("data-vue-shell"),
                    attribute_map.get("data-page-name"),
                )
            )
        if "logo" in classes:
            self.logo_controls.append(
                (
                    tag,
                    attribute_map.get("type"),
                    attribute_map.get("aria-label"),
                )
            )
        if tag in self.tag_counts:
            self.tag_counts[tag] += 1
        if tag == "nav" and "navigation" in attribute_map.get("class", "").split():
            self.in_navigation = True
            self.navigation_label = attribute_map.get("aria-label")
        elif self.in_navigation and tag == "a":
            self.current_link = {
                "href": attribute_map.get("href"),
                "aria_current": attribute_map.get("aria-current"),
                "text": [],
            }
        if tag == "footer":
            self.in_footer = True
        elif self.in_footer and tag == "p":
            self.current_footer_paragraph = []

    def handle_data(self, data):
        if self.current_link is not None:
            self.current_link["text"].append(data)
        if self.current_footer_paragraph is not None:
            self.current_footer_paragraph.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link is not None:
            self.current_link["text"] = " ".join(
                "".join(self.current_link["text"]).split()
            )
            self.navigation_links.append(self.current_link)
            self.current_link = None
        elif tag == "nav":
            self.in_navigation = False
        elif tag == "p" and self.current_footer_paragraph is not None:
            paragraph = " ".join("".join(self.current_footer_paragraph).split())
            self.footer_paragraphs.append(paragraph)
            self.current_footer_paragraph = None
        elif tag == "footer":
            self.in_footer = False


def relative_name(path):
    return path.relative_to(REPOSITORY_ROOT).as_posix()


def check_internal_references(errors):
    html_paths = sorted(
        path
        for path in REPOSITORY_ROOT.rglob("*.html")
        if not any(
            part in IGNORED_SOURCE_DIRECTORIES
            for part in path.relative_to(REPOSITORY_ROOT).parts
        )
    )
    reference_count = 0

    for html_path in html_paths:
        parser = ReferenceParser()
        try:
            parser.feed(html_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as error:
            errors.append(f"{relative_name(html_path)}: cannot read HTML: {error}")
            continue

        for tag, attribute, raw_value in parser.references:
            parsed = urlsplit(raw_value)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue

            decoded_path = unquote(parsed.path)
            if decoded_path.startswith("/"):
                target = REPOSITORY_ROOT / decoded_path.lstrip("/")
            else:
                target = html_path.parent / decoded_path

            reference_count += 1
            try:
                resolved_target = target.resolve()
                resolved_target.relative_to(REPOSITORY_ROOT)
            except (OSError, ValueError):
                errors.append(
                    f"{relative_name(html_path)}: {tag}[{attribute}] escapes the repository: "
                    f"{raw_value}"
                )
                continue

            if not resolved_target.is_file():
                errors.append(
                    f"{relative_name(html_path)}: {tag}[{attribute}] target does not exist: "
                    f"{raw_value}"
                )

    return len(html_paths), reference_count


def load_site_css(errors):
    expected_lines = ["/* 稳定入口按依赖从通用到覆盖加载。 */"]
    expected_lines.extend(
        f'@import url("{module_name}");' for module_name in CSS_MODULES
    )
    expected_entry = "\n".join(expected_lines)

    try:
        entry_css = CSS_ENTRY_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        errors.append(f"css/style.css: cannot read CSS entrypoint: {error}")
        return ""

    if entry_css.replace("\r\n", "\n").strip() != expected_entry:
        errors.append("css/style.css: imports must match the CSS module contract")

    module_contents = []
    for module_name in CSS_MODULES:
        module_path = CSS_ROOT / module_name
        try:
            module_css = module_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"css/{module_name}: cannot read CSS module: {error}")
            continue
        if "@import" in module_css:
            errors.append(f"css/{module_name}: nested imports are not allowed")
        for marker in CSS_REQUIRED_MARKERS[module_name]:
            if marker not in module_css:
                errors.append(
                    f"css/{module_name}: required responsibility marker is missing: "
                    f"{marker}"
                )
        module_contents.append(module_css)

    return "\n".join(module_contents)


def check_shared_javascript(errors):
    for page_name in PAGE_CONFIGS:
        page_path = REPOSITORY_ROOT / page_name
        script_source = "js/script.js" if page_name == "index.html" else "../js/script.js"
        expected_script = f'<script type="module" src="{script_source}"></script>'
        try:
            page_html = page_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"{page_name}: cannot inspect shared script: {error}")
            continue
        if page_html.count(expected_script) != 1:
            errors.append(f"{page_name}: expected one shared ES Module entry")

    try:
        entry_source = SHARED_JS_ENTRY_PATH.read_text(encoding="utf-8")
        module_source = SHARED_JS_MODULE_PATH.read_text(encoding="utf-8")
        layout_source = SHARED_LAYOUT_JS_PATH.read_text(encoding="utf-8")
        layout_config = SHARED_LAYOUT_CONFIG_PATH.read_text(encoding="utf-8")
        component_sources = [
            path.read_text(encoding="utf-8")
            for path in SHARED_LAYOUT_COMPONENT_PATHS
        ]
    except (OSError, UnicodeError) as error:
        errors.append(f"shared JavaScript or Vue module cannot be read: {error}")
        return 0

    imports = tuple(re.findall(r"from\s+['\"]([^'\"]+)['\"]", entry_source))
    if imports != ("./logo-animation.js", "./shared-layout.js"):
        errors.append("js/script.js: imports must match the shared module contract")
    if "initializeSharedLayout();" not in entry_source:
        errors.append("js/script.js: Vue shared layout must be initialized")
    if "initializeLogoAnimation();" not in entry_source:
        errors.append("js/script.js: shared animation must be initialized")
    if any(
        marker in entry_source
        for marker in ("hoverTimer", "rotationSpeed", "requestAnimationFrame")
    ):
        errors.append("js/script.js: entrypoint contains animation implementation")

    layout_markers = (
        "import { createSSRApp } from 'vue'",
        "SiteHeader.vue",
        "SiteFooter.vue",
        "createHeaderProps(pageName)",
        "headerApp.mount(headerHost)",
        "footerApp.mount(footerHost)",
        "if (!headerHost || !footerHost)",
    )
    for marker in layout_markers:
        if marker not in layout_source:
            errors.append(
                f"js/shared-layout.js: required Vue marker is missing: {marker}"
            )

    for page_name in PAGE_CONFIGS:
        if f"'{page_name}'" not in layout_config:
            errors.append(
                f"js/shared-layout/config.js: page contract is missing: {page_name}"
            )
    for component_path, component_source in zip(
        SHARED_LAYOUT_COMPONENT_PATHS, component_sources
    ):
        if "<template>" not in component_source or "defineProps" not in component_source:
            errors.append(
                f"{relative_name(component_path)}: expected one props-driven SFC"
            )

    required_markers = (
        "export function initializeLogoAnimation",
        "if (!logo || !logoImage)",
        "startDelayMs = LOGO_START_DELAY_MS",
        "rotationSpeed = 2",
        "rotationSpeed += 0.5",
        "logo.addEventListener(eventName, listener)",
        "['mouseenter', startAnimation]",
        "['mouseleave', stopAnimation]",
        "['click', startAnimation]",
        "['blur', stopAnimation]",
        "['keydown', handleKeydown]",
        "event.key === 'Escape'",
        "prefers-reduced-motion: reduce",
        "handleMotionChange",
    )
    for marker in required_markers:
        if marker not in module_source:
            errors.append(
                f"js/logo-animation.js: required behavior marker is missing: {marker}"
            )

    return 4 + len(component_sources)


def check_image_index_javascript(errors):
    page_path = REPOSITORY_ROOT / "pages" / "image-index.html"
    expected_script = '<script type="module" src="../js/image-index.js"></script>'

    try:
        page_html = page_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        errors.append(f"pages/image-index.html: cannot read module entry: {error}")
        return 0

    if page_html.count(expected_script) != 1:
        errors.append(
            "pages/image-index.html: expected one ES Module image-index entry"
        )

    try:
        entry_source = IMAGE_INDEX_JS_ENTRY_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        errors.append(f"js/image-index.js: cannot read module entry: {error}")
        return 0

    actual_imports = tuple(
        re.findall(r"from\s+['\"]([^'\"]+)['\"]", entry_source)
    )
    if actual_imports != IMAGE_INDEX_JS_IMPORTS:
        errors.append("js/image-index.js: imports must match the module contract")

    legacy_markers = (
        "function validateImageIndex",
        "function createImageLink",
        "function showPreview",
    )
    if any(marker in entry_source for marker in legacy_markers):
        errors.append("js/image-index.js: entrypoint contains module implementation")

    module_sources = {}
    for import_path in IMAGE_INDEX_JS_IMPORTS:
        module_path = JS_ROOT / import_path.removeprefix("./")
        try:
            module_source = module_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"js/{import_path.removeprefix('./')}: cannot read: {error}")
            continue
        module_sources[import_path] = module_source
        for marker in IMAGE_INDEX_JS_REQUIRED_MARKERS[import_path]:
            if marker not in module_source:
                errors.append(
                    f"js/{import_path.removeprefix('./')}: required responsibility "
                    f"marker is missing: {marker}"
                )

    data_source = module_sources.get("./image-index/data.js", "")
    gallery_source = module_sources.get("./image-index/gallery.js", "")
    preview_source = module_sources.get("./image-index/preview.js", "")
    if "document." in data_source or "window." in data_source:
        errors.append("js/image-index/data.js: data module must not access the DOM")
    if "fetch(" in gallery_source or "fetch(" in preview_source:
        errors.append("image-index view modules must not fetch data")
    if "document.createElement" in preview_source:
        errors.append("js/image-index/preview.js: preview module must not render the list")

    return len(module_sources)


def check_accessibility(errors, css):
    for page_name, expected_title in PAGE_TITLES.items():
        page_path = REPOSITORY_ROOT / page_name
        parser = AccessibilityParser()
        try:
            parser.feed(page_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as error:
            errors.append(f"{page_name}: cannot inspect accessibility metadata: {error}")
            continue

        if parser.lang != "zh-CN":
            errors.append(f"{page_name}: html lang must be zh-CN")
        if parser.title != expected_title:
            errors.append(f"{page_name}: title must be {expected_title!r}")
        if parser.main_labels != ["page-title"]:
            errors.append(f"{page_name}: main must reference page-title")

        page_headings = [heading for heading in parser.headings if heading[0] == 1 and heading[1] == "page-title" and "visually-hidden" in heading[2]]
        if len(page_headings) != 1 or not parser.headings or parser.headings[0][0] != 1:
            errors.append(f"{page_name}: expected one visually hidden h1 with id page-title")

        levels = [level for level, _, _ in parser.headings]
        if any(current > previous + 1 for previous, current in zip(levels, levels[1:])):
            errors.append(f"{page_name}: heading levels must not skip")

        for source, alt, image_id in parser.images:
            if alt is None:
                errors.append(f"{page_name}: image {source!r} is missing alt")
            elif source and source.endswith("logo.jpg") and alt != "":
                errors.append(f"{page_name}: repeated logo image must use empty alt")
            elif image_id == "preview-image" and alt != "":
                errors.append(f"{page_name}: dynamic preview must start with empty alt")
            elif not (source and source.endswith("logo.jpg")) and image_id != "preview-image" and not alt:
                errors.append(f"{page_name}: content image {source!r} needs descriptive alt")

        if page_name == "pages/contact.html" and parser.contact_sections != [("section", "联系方式")]:
            errors.append(f"{page_name}: contact content must be one labelled section")

    if len(set(PAGE_TITLES.values())) != len(PAGE_TITLES):
        errors.append("Page titles must be unique")

    if ".visually-hidden {" not in css:
        errors.append("CSS modules: visually-hidden utility is missing")
    if '.navigation a[aria-current="page"] {' not in css:
        errors.append("CSS modules: current navigation style is missing")


def check_services_structure(errors):
    page_name = "pages/services.html"
    page_path = REPOSITORY_ROOT / page_name
    parser = ServicesStructureParser()

    try:
        parser.feed(page_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        errors.append(f"{page_name}: cannot inspect services module: {error}")
        return

    if parser.main_classes != [{"content", "services-page"}]:
        errors.append(f"{page_name}: main must own the content and services-page layout")
    if parser.services_content != [("section", "services-title")]:
        errors.append(f"{page_name}: primary services content must be one labelled section")
    if len(parser.service_items) != 3:
        errors.append(f"{page_name}: expected exactly three service-item sections")

    service_labels = [
        label for tag, label in parser.service_items if tag == "section" and label
    ]
    if (
        len(service_labels) != len(parser.service_items)
        or len(service_labels) != len(set(service_labels))
        or not set(service_labels).issubset(parser.heading_ids)
    ):
        errors.append(
            f"{page_name}: every service item must reference its own heading"
        )

    if parser.construction_notices != [("aside", "施工状态")]:
        errors.append(f"{page_name}: construction status must be one labelled aside")
    if parser.nested_content_count:
        errors.append(f"{page_name}: redundant nested content wrappers are not allowed")


def check_about_structure(errors):
    page_name = "pages/about.html"
    page_path = REPOSITORY_ROOT / page_name
    parser = AboutStructureParser()

    try:
        parser.feed(page_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        errors.append(f"{page_name}: cannot inspect about page structure: {error}")
        return

    if parser.main_classes != [set()]:
        errors.append(f"{page_name}: main must not use a page-specific layout class")
    if parser.about_content_count != 1:
        errors.append(f"{page_name}: expected exactly one about-content container")
    if parser.image_group_count == 0:
        errors.append(f"{page_name}: expected explicit about-image-group containers")
    if parser.legacy_layout_classes:
        errors.append(f"{page_name}: legacy contact or box layout classes remain")
    if parser.empty_paragraph_count:
        errors.append(f"{page_name}: empty paragraphs must not be used for spacing")

    labels = [label for tag, label in parser.body_text_sections if tag == "section" and label]
    if len(labels) != len(parser.body_text_sections) or len(labels) != len(set(labels)):
        errors.append(
            f"{page_name}: every body-text block must be a uniquely labelled section"
        )


def check_page_layout(errors):
    for page_name, expected in PAGE_LAYOUTS.items():
        page_path = REPOSITORY_ROOT / page_name
        parser = LayoutParser()

        try:
            parser.feed(page_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as error:
            errors.append(f"{page_name}: cannot inspect shared layout: {error}")
            continue

        for tag, count in parser.tag_counts.items():
            if count != 1:
                errors.append(f"{page_name}: expected exactly one {tag}, found {count}")

        if parser.vue_shells != [
            ("div", "header", page_name),
            ("div", "footer", None),
        ]:
            errors.append(f"{page_name}: Vue layout hosts do not match the contract")

        if parser.logo_controls != [
            ("button", "button", "播放呼气之窝 Logo 动画")
        ]:
            errors.append(
                f"{page_name}: shared logo must be one labelled button"
            )

        if parser.navigation_label != "主导航":
            errors.append(
                f"{page_name}: shared navigation must use aria-label='主导航'"
            )

        actual_links = tuple(
            (link["text"], link["href"]) for link in parser.navigation_links
        )
        if actual_links != expected["links"]:
            errors.append(f"{page_name}: shared navigation links do not match the contract")

        current_links = [
            link["href"]
            for link in parser.navigation_links
            if link["aria_current"] == "page"
        ]
        invalid_current_values = [
            link["aria_current"]
            for link in parser.navigation_links
            if link["aria_current"] not in {None, "page"}
        ]
        if current_links != [expected["current"]] or invalid_current_values:
            errors.append(
                f"{page_name}: expected one aria-current='page' on "
                f"{expected['current']}"
            )

        if tuple(parser.footer_paragraphs) != SHARED_FOOTER_TEXT:
            errors.append(f"{page_name}: shared footer does not match the contract")

    return len(PAGE_LAYOUTS)


def load_image_index(errors):
    try:
        with open(INDEX_PATH, encoding="utf-8") as json_file:
            payload = json.load(json_file)
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{relative_name(INDEX_PATH)}: cannot load JSON: {error}")
        return None

    if not isinstance(payload, dict):
        errors.append(f"{relative_name(INDEX_PATH)}: top level must be an object")
        return None
    if set(payload) != {"version", "images"}:
        errors.append(
            f"{relative_name(INDEX_PATH)}: top-level fields must be version and images"
        )
    if payload.get("version") != CONTRACT_VERSION:
        errors.append(
            f"{relative_name(INDEX_PATH)}: version must be {CONTRACT_VERSION}"
        )
    if not isinstance(payload.get("images"), list):
        errors.append(f"{relative_name(INDEX_PATH)}: images must be an array")
        return None

    return payload["images"]


def check_image_index(errors):
    records = load_image_index(errors)
    if records is None:
        return 0, 0

    indexed_ids = []
    indexed_sources = []

    for position, record in enumerate(records):
        label = f"{relative_name(INDEX_PATH)}: images[{position}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        if set(record) != IMAGE_FIELDS:
            errors.append(f"{label} must contain exactly {sorted(IMAGE_FIELDS)}")
            continue
        if any(
            not isinstance(record[field], str) or not record[field]
            for field in IMAGE_FIELDS
        ):
            errors.append(f"{label} fields must be non-empty strings")
            continue

        image_id = record["id"]
        image_path = Path(image_id)
        expected_album = image_path.parts[0] if len(image_path.parts) > 1 else "root"
        expected_caption = image_path.name

        if "\\" in image_id or image_id.startswith("/"):
            errors.append(f"{label}.id must be a relative path using forward slashes")
        if image_path.is_absolute() or ".." in image_path.parts:
            errors.append(f"{label}.id must stay inside the image directory")
        if record["src"] != f"../image/{image_id}" or "\\" in record["src"]:
            errors.append(f"{label}.src must equal ../image/{{id}} and use forward slashes")
        if record["album"] != expected_album:
            errors.append(f"{label}.album must be {expected_album!r}")
        if record["caption"] != expected_caption:
            errors.append(f"{label}.caption must be {expected_caption!r}")
        expected_alt = f"{expected_album}：{expected_caption}"
        if record["alt"] != expected_alt:
            errors.append(f"{label}.alt must be {expected_alt!r}")

        indexed_ids.append(image_id)
        indexed_sources.append(record["src"])

    if len(indexed_ids) != len(set(indexed_ids)):
        errors.append(f"{relative_name(INDEX_PATH)}: image ids must be unique")
    if len(indexed_sources) != len(set(indexed_sources)):
        errors.append(f"{relative_name(INDEX_PATH)}: image sources must be unique")

    sorted_ids = sorted(indexed_ids, key=lambda value: (value.casefold(), value))
    if indexed_ids != sorted_ids:
        errors.append(f"{relative_name(INDEX_PATH)}: records are not sorted by id")

    actual_ids = {
        path.relative_to(IMAGE_ROOT).as_posix()
        for path in IMAGE_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    }
    indexed_id_set = set(indexed_ids)

    for image_id in sorted(actual_ids - indexed_id_set, key=str.casefold):
        errors.append(f"{relative_name(INDEX_PATH)}: local image is not indexed: {image_id}")
    for image_id in sorted(indexed_id_set - actual_ids, key=str.casefold):
        errors.append(f"{relative_name(INDEX_PATH)}: indexed image does not exist: {image_id}")
    if len(records) != len(actual_ids):
        errors.append(
            f"{relative_name(INDEX_PATH)}: record count {len(records)} does not match "
            f"local image count {len(actual_ids)}"
        )

    return len(records), len(actual_ids)


def main():
    errors = []
    html_count, reference_count = check_internal_references(errors)
    layout_count = check_page_layout(errors)
    check_about_structure(errors)
    check_services_structure(errors)
    css = load_site_css(errors)
    check_accessibility(errors, css)
    shared_javascript_module_count = check_shared_javascript(errors)
    javascript_module_count = check_image_index_javascript(errors)
    record_count, image_count = check_image_index(errors)

    if errors:
        print(f"Site check failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Site check passed: {html_count} HTML files, {reference_count} local references, "
        f"{layout_count} shared layouts, {shared_javascript_module_count} shared "
        f"JavaScript/Vue modules, {javascript_module_count} image-index JavaScript "
        f"modules, {record_count} index records, {image_count} local images."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
