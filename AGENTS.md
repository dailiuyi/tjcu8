# Repository Guidelines

## Project Structure & Module Organization

This is a Vite multi-page site using Vue 3 for the shared page shell. `index.html` is the homepage and four additional entries live in `pages/`. Shared SFCs live in `js/components/`; page-shell props and hydration live in `js/shared-layout/` and `js/shared-layout.js`. CSS enters through `css/style.css`; other browser modules stay in `js/`; media stays under `image/`, including Chinese paths. Python generators produce static shell fallbacks and `pages/json/image_index.json`. Vite builds the five pages into `dist/`, the only deployable directory. Architecture contracts live in `docs/`.

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

`npm run dev` serves source pages at `http://localhost:5173/`. Run generators after layout or image changes. `check:js` includes Logo, gallery, and Vue SSR/fallback parity checks. Build and dist checks verify the production artifact; preview serves it locally.

## Coding Style & Naming Conventions

Use UTF-8 and four-space indentation. Prefer semantic HTML and props-driven Vue SFCs; keep reusable CSS in its responsibility module and browser behavior in ES Modules. Use PascalCase component files, kebab-case CSS classes, camelCase JavaScript identifiers, and snake_case Python names. Root and `pages/` files require different relative paths. Keep `index.html` as the only homepage; never recreate `demo.html`. Preserve existing Chinese copy and visual personality unless explicitly asked to change them.

## Refactoring Workflow

Read `docs/refactoring-progress.md` first. Complete one page or functional module at a time, preserve unrelated files, verify source and `dist/`, update progress, and identify the next module. Keep the five-page MPA and static fallback until a separately approved routing or rendering phase.

## Testing & Review

Before submitting, run all relevant commands above and inspect wide and narrow viewports. UI pull requests need screenshots; all PRs should describe behavior, verification, linked issues, and deployment impact. Keep commits focused with imperative subjects such as `Componentize shared page shell`.

## Security & Deployment

Never commit credentials, keys, tokens, private data, logs, `node_modules/`, or `dist/`. GitHub Pages and `tjcu8.elma-gohan.xyz` must deploy the same CI-built artifact. Preserve `docs/deployment.md`; never overwrite the root domain site.