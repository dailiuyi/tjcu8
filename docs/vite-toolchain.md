# Vite 工具链

## 模块边界

Vite 接管开发服务器、Vue SFC 编译和生产构建，但五个 HTML 仍是独立页面入口，不使用 Vue Router。用 Spring 类比，仓库根目录是源码工程，`dist/` 是唯一可部署制品，类似构建后生成的 JAR。

`vite.config.js` 将 `index.html` 和 `pages/` 下四个页面声明为多页面入口。`base: './'` 让同一份产物同时适配根域名和 GitHub Pages 子路径。JavaScript 与 CSS 生成带哈希文件；原图片目录和 JSON 数据按现有路径复制，以继续满足图片索引契约。静态 fallback 与 Vue Header 组件中的图片都标记为 `vite-ignore`，避免为同一批大型图片再生成哈希副本；JavaScript、Vue 运行时和 CSS 仍正常打包。

## 常用命令

```powershell
npm ci
npm run dev
npm run build
npm run check:dist
npm run preview
```

`npm run dev` 在源码上提供开发服务器。`npm run build` 清理并生成 `dist/`。`npm run check:dist` 比较构建前后的页面文字，检查五个页面、所有本地引用、71 条图片记录和原图片是否完整。`npm run preview` 只预览生产产物。

## 部署契约

GitHub Actions 使用 Node 24 和 `npm ci`，在源码检查通过后构建一次 `dist/`。GitHub Pages 与阿里云部署下载同一个短期构建产物；任何部署都不能再次直接打包仓库根目录。GitHub Pages 的发布源必须设置为 `GitHub Actions`，不能同时启用 legacy 分支发布。