# 公共布局契约

五个正式页面的页头、导航和页脚由 `scripts/site_layout.py` 统一定义，`scripts/generate-shared-layout.py` 将它们写入完整静态 HTML。页面中的 `shared-header` 与 `shared-footer` 注释是生成边界，不应手工修改边界内内容。

这种方案相当于 Spring 服务端模板中的公共 layout：`site_layout.py` 是模板与路由配置，生成器是渲染阶段，HTML 是可直接部署的产物。它不依赖浏览器端 JavaScript，也不要求服务器支持 SSI，因此 GitHub Pages 与 Nginx 使用同一套文件。

修改站点名称、主导航、页脚或页面当前导航时，先更新 `scripts/site_layout.py`，再运行：

```powershell
python scripts/generate-shared-layout.py
python scripts/check-site.py
```

页面自己的 `<main>` 内容仍留在对应 HTML 中。不要把正文搬入布局生成器，也不要手工复制公共导航。
