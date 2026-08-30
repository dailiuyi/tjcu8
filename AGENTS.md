# Repository Guidelines

## Project Structure & Module Organization

This is a Vite-powered multi-page static site; Vue is not installed yet. `index.html` is the homepage and four additional entries live in `pages/`. CSS enters through `css/style.css`; browser modules live in `js/`; media stays under `image/`, including existing Chinese paths. Python generators live in `scripts/` and produce shared HTML plus `pages/json/image_index.json`. `vite.config.js` builds the five pages into `dist/`, the only deployable directory. Architecture contracts live in `docs/`.

## Build, Test, and Development Commands

Run from the repository root:

```powershell
npm ci
npm run dev
python scripts/generate-shared-layout.py
python scripts/generate-image-index.py
python scripts/check-site.py
npm run check:js
npm run build
npm run check:dist
npm run preview
```

`npm run dev` serves source pages at `http://localhost:5173/`. Run generators after shared-layout or image changes. Source checks validate links, accessibility, data, and browser behavior. Build and dist checks verify the exact production artifact; preview serves it locally.

## Coding Style & Naming Conventions

Use UTF-8 and four-space indentation. Prefer semantic HTML; keep reusable CSS in its responsibility module and browser behavior in ES Modules. Use kebab-case CSS classes, camelCase JavaScript identifiers, and snake_case Python names. Root and `pages/` files require different relative paths. Keep `index.html` as the only homepage; never recreate `demo.html`. Preserve existing Chinese copy and visual personality unless explicitly asked to change them.

## Refactoring Workflow

Read `docs/refactoring-progress.md` first. Complete one page or functional module at a time, preserve unrelated files, verify source and `dist/`, update progress, and identify the next module. Do not introduce Vue or other dependencies outside an approved phase.

## Testing & Review

Before submitting, run all relevant commands above and inspect both wide and narrow viewports. UI pull requests need before/after screenshots; all PRs should describe behavior, verification, linked issues, and deployment impact. Keep commits focused with imperative subjects such as `Add Vite build pipeline`.

## Security & Deployment

Never commit credentials, keys, tokens, private data, logs, `node_modules/`, or `dist/`. GitHub Pages and `tjcu8.elma-gohan.xyz` must deploy the same CI-built `dist/` artifact. Preserve the isolated release layout in `docs/deployment.md`; never overwrite the root domain site.