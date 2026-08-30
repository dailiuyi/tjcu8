# 阿里云部署说明

正式站点为 `https://tjcu8.elma-gohan.xyz/`，由服务器上的 Nginx 独立托管，不覆盖 `elma-gohan.xyz` 根站点。

## 线上结构

- Nginx 配置：`/etc/nginx/conf.d/tjcu8.conf`
- 仓库配置源：`deploy/nginx/tjcu8.conf`
- 版本目录：`/var/www/tjcu8/releases/<release-id>`
- 当前版本：`/var/www/tjcu8/current` 软链接
- ACME Webroot：`/var/www/certbot`
- 证书目录：`/etc/letsencrypt/live/tjcu8.elma-gohan.xyz/`
- 首次部署备份：`/root/tjcu8-backups/<release-id>`
- 自动发布入口：`/usr/local/bin/deploy-tjcu8`
- 受限账号：`tjcu8-deploy`，无密码、无 sudo，仅管理 `/var/www/tjcu8`

发布包只应包含 Vite `dist/` 中的 `index.html`、`css/`、`js/`、`pages/` 和 `image/`。源码目录不直接上线。发布前运行生成器、源码契约检查、`npm run build` 和 `npm run check:dist`；上传后校验 SHA-256，再解压到新版本目录并原子切换 `current`。

## 验证与回滚

每次发布后检查 HTTPS 页面、静态资源、JSON、HTTP 301、证书、`nginx -t` 和根站点。回滚时让 `current.new` 指向上一个 release，再用 `mv -Tf` 替换 `current`，最后执行 `nginx -t && systemctl reload nginx`。

服务器连接信息和密钥只能放在受控终端或 GitHub Environment Secrets 中，禁止提交到仓库。

## 自动发布

`.github/workflows/static.yml` 的质量任务只构建一次 `dist/` 并上传为短期构建产物。GitHub Pages 和 `deploy-server` 下载同一产物，确保两个部署目标内容一致。`deploy-server` 只在质量门禁通过、事件不是 Pull Request 且仓库变量 `DEPLOY_ENABLED=true` 时运行；它打包 `dist/`、上传到 `incoming/`，再调用 `deploy-tjcu8` 校验 SHA-256、检查归档路径、创建 release、切换 `current` 并验证首页；验证失败会恢复上一个 release。

GitHub `production` Environment 保存 `SERVER_HOST`、`SERVER_PORT`、`SERVER_USER`、`SERVER_SSH_KEY` 和 `SERVER_KNOWN_HOSTS`，以及 `DEPLOY_PATH`、`SITE_URL` 两个非敏感变量。部署密钥不能登录 root，也没有 sudo 权限。
