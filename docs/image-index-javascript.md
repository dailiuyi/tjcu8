# 图片索引 JavaScript 架构

`js/image-index.js` 是组装入口，只负责取得页面元素、创建预览控制器、加载数据并处理顶层失败。页面以原生 ES Module 方式加载它，不需要 npm、打包器或框架。

模块职责对应常见后端分层：

- `image-index/data.js` 类似 Repository 与 DTO 校验层，负责请求并验证 JSON 契约，不访问 DOM。
- `image-index/gallery.js` 类似视图渲染器，只创建列表元素和页面状态，不发起请求。
- `image-index/preview.js` 类似有状态控制器，管理定位、加载/失败状态、延迟隐藏和键盘事件。
- `image-index.js` 类似应用服务或 composition root，只组装以上模块。

修改后运行：

```powershell
python scripts/check-site.py
node scripts/check-image-index-js.mjs
```

测试脚本只使用 Node 标准库，覆盖真实 JSON、空列表、错误状态、预览加载/失败和 Escape 隐藏。必须通过本地 HTTP 服务器预览页面；直接打开 `file://` 页面无法可靠加载 ES Module。
