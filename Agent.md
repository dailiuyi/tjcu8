# Agent.md — 呼气之窝 (tjcu8)

给后续 Agent 用的仓库说明。改页面、样式、图片索引之前先读这一份。

## 这是什么

纯静态中文站点，站点名「呼气之窝」，主题是天津商业大学（天商 / TJCU）校园群「↑8」的玩梗介绍页。无框架、无打包、无 npm、无测试。版权年份写在页脚：`© 2024 呼气之窝`。

语气是校园黑话 + 表情包。改文案时保持这个风格，不要改成正式官网口吻。

## 怎么跑

没有构建步骤。从仓库根目录起一个本地 HTTP 服务即可：

```bash
python -m http.server 8080
```

然后打开 `http://localhost:8080/`。`index.html` 会立刻跳到 `demo.html`。

不要用 `file://` 打开 `pages/one_services.html`：它用 `fetch('json/image_index.json')`，浏览器会拦 CORS。其它页面在 `file://` 下大多能看，但路径和预览行为不一致，验证时一律走 HTTP。

改完图片目录后，需要重建索引：

```bash
python pages/main.py
```

会覆盖 `pages/json/image_index.json`。

## 目录

```
index.html                 # 0 秒跳转到 demo.html，不要当真正首页改
demo.html                  # 真正首页
css/style.css              # 全站唯一样式表
js/script.js               # Logo 悬停旋转彩蛋
pages/
  about.html               # 关于我们（图集 + 段子）
  services.html            # 服务列表（服务二/三是占位）
  contact.html             # 加入我们（只放二维码）
  one_services.html        # 「服务一」图片索引页，动态读 JSON
  main.py                  # 扫 image/ 生成 image_index.json
  json/image_index.json    # 生成物，不要手改
image/                     # 全部静态图；子目录名就是栏目名
logs/                      # 未跟踪，可忽略
```

`image/` 子目录（路径里有中文和 emoji，改名会断 HTML 引用）：

| 目录 | 用途 |
|---|---|
| `螺狮粉/` | 关于页：学校附近打野/螺狮粉 |
| `奶龙/` | 关于页：奶龙相关 |
| `团建/` | 关于页：团建合影 |
| `win/` | 关于页：国际形势/学校问题截图 |
| `反动势力/` | 关于页：内部对线截图 |
| `我们的↑8/` | 索引里有，关于页目前没直接引用 |
| `我们的↑8/天商一角/` | 校园风景 |
| `我们的↑8/学校助学金以及奖学金/` | 奖助学金截图 |
| `我们的↑8/⬆️🧱黑历史/` | 黑历史截图 |
| `社团招新群/` | 招新群截图 |
| 根下 `logo.jpg` `background.png` `事迹1.jpg` `事迹2.jpg` `二维码.jpg` | 全站共用 |

## 路由与导航

四栏导航在每个 HTML 里手写一份，没有公共模板。

| 栏 | 根目录页（`demo.html`） | `pages/` 下的页 |
|---|---|---|
| 首页 | `demo.html` | `../demo.html` |
| 关于我们 | `pages/about.html` | `about.html` |
| 服务 | `pages/services.html` | `services.html` |
| 加入我们 | `pages/contact.html` | `contact.html` |

资源路径同样按层级分两套：

- 根页面：`css/style.css`、`js/script.js`、`image/...`
- `pages/` 页面：`../css/style.css`、`../js/script.js`、`../image/...`

加新页面时，先看它放哪一层，再抄对应那一套。不要混用。

已知偏差（改导航时顺手修，不要再复制）：

- `pages/contact.html` 的「加入我们」链到了 `about.html`，应该是 `contact.html`。
- `pages/about.html` 里 `7822D6BE196BA44E78AA33C946EC4244.jpg` 用了两次；`90B80353EAFFE85831F101AE7668998D.jpg` 在目录里但页面没用。

## 页面职责

**首页 `demo.html`**  
短诗 + `事迹1.jpg` / `事迹2.jpg`。诗的高潮句用 `.highlight`。

**关于我们 `pages/about.html`**  
按栏目堆文案和图片：螺狮粉 → 奶龙 → 团建 → win → 反动势力。每组图用 `.box` 包，栏目之间用 `<hr>`。图片 class 对应 CSS 宽度：`.image-luoshifen` 300px，`.image-nailong` / `.image-tuanjian` / `.image-win` / `.image-battle` 250px。

**服务 `pages/services.html`**  
三张 `.service-item` 卡片。服务一链到 `one_services.html`。服务二文案是「还没写」，服务三是占位吐槽，不是正式功能。页内有一段重复的 `footer` 样式，真正定义在 `css/style.css`。

**加入我们 `pages/contact.html`**  
只展示 `image/二维码.jpg`，class 为 `.qr-code`（390px）。

**图片索引 `pages/one_services.html`**  
页面加载后 `fetch('json/image_index.json')`，按 `images[].name` 生成链接列表，悬停用 `#preview` 跟鼠标预览。链接的 `href` 直接用 JSON 里的 `path`。页内另有一块预览图 CSS，不要删。

## 样式约定

全站只改 `css/style.css`，除非某一页必须覆盖（目前只有 `services.html` / `one_services.html` 有内联 footer/预览样式）。

视觉：

- 页头：绿渐变 `#246f27` → `#6fae6a`，白字
- 高亮 / 导航悬停：`#cddc39`
- 正文：微软雅黑 / 黑体 / 宋体，`#333`
- 背景：`body::before` 铺 `image/background.png`，opacity 0.7，fixed
- 卡片：白底半透明、圆角 8–10px、浅阴影

布局用 Flexbox，没有 CSS 变量、没有预处理器。class 名是语义化英文（`.poem` `.box` `.body-text` `.services-list`），图片尺寸 class 是拼音（`.image-luoshifen`）。新尺寸 class 继续跟这个模式。

Logo 悬停有两套动画叠在一起：

1. CSS：`.logo:hover img { transform: rotate(360deg); }`
2. JS：悬停 1 秒后 `requestAnimationFrame` 加速旋转，离开复位

改 Logo 交互时两处都要看，否则会互相覆盖。

## 图片索引流水线

`pages/main.py` 做的事：

1. 仓库根 = `pages/` 的上一级
2. `os.walk(image/)`，收 `.jpg` `.jpeg` `.png` `.gif`
3. 写成 `pages/json/image_index.json`，字段只有 `name` 和 `path`

`path` 现在是 Windows 反斜杠，形如 `"..\\image\\螺狮粉\\1.jpg"`。浏览器多数能吃，但不可靠。改生成脚本时改成正斜杠（`../image/...`），并同步重跑脚本。不要手改 JSON。

`one_services.html` 的 `fetch` 路径是相对当前页的 `json/image_index.json`，不要改成从根走。

## 改代码时注意

- 没有组件系统。改页头、导航、页脚要四个页面一起改：`demo.html`、`about.html`、`services.html`、`contact.html`。`one_services.html` 也有同一套页头页脚。
- 不要引入 React / Vue / 打包器，除非用户明确要求。
- 不要把中文路径改成拼音，除非同时改完所有 HTML `src` 和重跑 `main.py`。
- 新图放到对应 `image/` 子目录，再跑 `python pages/main.py`。只丢文件不跑脚本，索引页不会出现。
- 验证：至少打开首页、关于、服务、加入我们、服务一。服务一必须用 HTTP 服务，悬停链接应出预览图。
- 视口：页头是横向 flex，窄屏没有单独的移动导航。改布局时看一下窄宽度会不会挤爆。
- `logs/` 不是站点的一部分，不要提交。

## 不要做的事

- 不要把 `index.html` 改成真正首页却不改跳转，访客永远看不到。
- 不要在 `file://` 下声称「服务一坏了」——先确认是不是没起 HTTP 服务。
- 不要格式化式大扫 CSS（大量注释、重复属性是原样）。只改你被要求改的那一块。
- 不要把玩梗文案「纠正」成规范书面语。
