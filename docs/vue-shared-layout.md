# Vue 公共页面壳

## 组件职责

- `SiteHeader.vue`：站名、Logo、四项主导航和 `aria-current`。
- `SiteFooter.vue`：三行固定页脚文案。
- `shared-layout/config.js`：五个页面的当前导航与相对 URL props。
- `shared-layout.js`：查找两个 `data-vue-shell` 容器，以 `createSSRApp` hydration 组件，再启动既有 Logo 动画。

组件只接收 props，不读取 URL、不操作页面正文，也不负责图片索引。五页仍是 Vite 多页面应用，不引入 Vue Router。

## 渐进增强

生成器在每个挂载容器中保留与组件等价的 Header/Footer。浏览器可以先显示完整静态页面；Vue 加载后复用现有 DOM。缺少任一挂载容器时初始化安全退出，避免影响非正式页面或后续独立页面。

## 验证

```powershell
npm run check:js
npm run build
npm run check:dist
```

Vue 检查通过 Vite 的 SSR 模块加载编译 SFC，验证五页组件/fallback 等价、相对导航、当前页和未知页面边界。生产检查继续约束页面文字和本地资源。