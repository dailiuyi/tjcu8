# Repository Guidelines

## Project Structure & Module Organization

This is a static site without a package manager or bundler. `index.html` is the homepage; additional pages live in `pages/`, CSS modules through `css/style.css`, and browser modules in `js/`. Store media under `image/` and preserve Chinese directory names because links depend on them. `scripts/generate-image-index.py` generates `pages/json/image_index.json` under `docs/image-index-contract.md`. Deployment targets are GitHub Pages and an Alibaba Cloud personal server with a registered domain.

## Build, Test, and Development Commands

Run commands from the repository root:

```powershell
python -m http.server 8000
python scripts/generate-shared-layout.py
python scripts/generate-image-index.py
python scripts/check-site.py
node scripts/check-image-index-js.mjs
python -m json.tool pages/json/image_index.json
git diff --check
```

The first command serves the site at `http://localhost:8000/`; no build step is required. Run the corresponding generator after shared-layout or image changes. The checker validates references, layout, accessibility, and image data. `git diff --check` catches whitespace errors. Keep validation independent from the selected deployment target.

## Coding Style & Naming Conventions

Use UTF-8 and four-space indentation in HTML, CSS, JavaScript, Python, and JSON. Prefer semantic HTML and keep reusable styling in `css/style.css` rather than adding new inline styles. Use kebab-case CSS classes, camelCase JavaScript identifiers, and snake_case Python names. Relative links differ by location: root pages use `pages/about.html`, while files under `pages/` return home with `../index.html`. Do not recreate `demo.html`; keep `index.html` as the single homepage. Preserve existing Chinese copy and site personality unless a task explicitly changes content.

## Refactoring Workflow

Read `docs/refactoring-progress.md` before refactoring. Work one page or functional module at a time; preserve existing copy and behavior, verify it, update the progress file, and name the next module.

## Testing Guidelines

There is no test framework or coverage target. Before submitting, serve the site locally and check every navigation link, image, hover interaction, and JSON-backed gallery. Test at both narrow and wide viewport sizes. Include before/after screenshots for visible changes.

## Commit & Pull Request Guidelines

History uses short imperative subjects such as `Create index.html` and `Update index.html`. Keep commits focused and use a clear verb plus scope, for example `Update homepage navigation`. Pull requests should describe the behavior changed, list verification performed, link relevant issues, and include screenshots for UI work.

## Security & Configuration

Never commit credentials, SSH keys, tokens, private data, logs, or environment files. Server operations are authorized. Deploy only to `tjcu8.elma-gohan.xyz` using `deploy/nginx/tjcu8.conf` and the isolated release layout in `docs/deployment.md`; never overwrite the root site.
