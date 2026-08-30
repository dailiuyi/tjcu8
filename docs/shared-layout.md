# 公共布局契约

五个正式页面的页头、导航和页脚由 Vue 组件与静态 fallback 共同维护。`js/components/SiteHeader.vue` 和 `SiteFooter.vue` 是浏览器端组件；`js/shared-layout/config.js` 提供页面、导航和页脚 props；`scripts/site_layout.py` 生成同结构 HTML，保证 JavaScript 尚未加载时导航和页脚仍可使用。

用 Spring 类比，Python 生成器相当于服务端首屏模板，Vue `createSSRApp` 在浏览器中 hydration 并接管同一个 View。页面中的 `shared-header`、`shared-footer` 注释及 `data-vue-shell` 是生成和挂载边界，不应手工修改。页面自己的 `<main>` 继续留在对应 HTML 中。

修改站名、导航、页脚或当前页规则时，必须同步组件 props 契约与 `scripts/site_layout.py`，然后运行：

```powershell
python scripts/generate-shared-layout.py
python scripts/check-site.py
npm run check:js
npm run build
npm run check:dist
```

`check-shared-layout-vue.mjs` 会通过 Vite 编译两个 SFC，逐页比较 Vue SSR 输出与静态 fallback。五个 HTML 仍是独立入口，不使用 Vue Router，也不把正文或图片索引业务搬进公共组件。