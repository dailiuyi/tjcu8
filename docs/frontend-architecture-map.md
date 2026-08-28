# 后端转全栈：前端名词与架构地图（周末速通）

目标水平：**听得懂、分得清层、能做选择、能指挥 Agent**。  
不是这周末手写一遍 Vue 源码，也不是背组件库 API。

你已经有的肌肉：分层、DTO、依赖方向、单一事实来源、什么该进数据库什么不该。  
前端架构就是把这套肌肉接到浏览器上。Agent 写得出代码，画不出这张图——图要在你脑子里。

---

## 0. 先建立总图（所有名词都挂在这上面）

一次页面访问，真实经过的层：

```text
用户手势 / URL
    ↓
浏览器
  ├─ 网络栈（HTTP、缓存、Cookie、CORS）
  ├─ HTML 解析 → DOM
  ├─ CSS 解析 → CSSOM
  ├─ 合成渲染树 → 布局 layout → 绘制 paint → 合成 composite
  └─ JS 引擎（调用栈、事件循环、微任务）
    ↓
你交给浏览器的「产物」
  HTML + CSS + JS（可能还有图片、字体）
    ↓
构建工具在开发/上线时做的变换
  Vite / 打包 / 转译 / 拆包 / 环境变量
    ↓
源码（你和 Agent 编辑的东西）
  路由、页面、组件、composable、样式、类型
    ↓
数据
  ├─ URL（路由参数、query）        ← 可分享的状态
  ├─ 组件内存（ref / props）       ← 页面局部
  ├─ 客户端全局（Pinia，慎用）     ← 跨页且瞬时
  ├─ 浏览器存储（cookie / storage）← 跨刷新
  └─ 服务器（Spring API）          ← 跨用户、要鉴权、要写入
```

后端对照：

| 前端这层 | 约等于 |
|---|---|
| 浏览器 | JVM + 容器，你控不了版本，只能适配 |
| 产物 HTML/CSS/JS | 打出来的 jar 里的 class + 静态资源 |
| Vite | Maven + Spring DevTools + 打 fat jar |
| 组件 | 带模板的一小块 Controller + 一小块视图 |
| composable | `@Service` / Domain Service |
| 路由 | `@RequestMapping` + 转发规则 |
| Pinia | 进程内单例缓存，不是数据库 |
| Spring API | 真正的持久化与权限边界 |

**架构能力的定义：** 来了一个需求，你能指出它该落在上图哪一层，以及为什么不落在别层。Agent 的价值是填那一层的代码，不是替你选层。

---

## 1. 浏览器运行时（不懂这里，后面全是咒语）

### 名词

**DOM（Document Object Model）**  
HTML 被解析后的树。JS 改的是这棵树，不是「改文件」。`document.querySelector` 就是在树上找节点。

**CSSOM**  
CSS 被解析后的规则树。和 DOM 合在一起才知道每个节点长什么样。

**渲染树 / layout / paint / composite**  
- layout（回流 reflow）：算几何，宽高位置  
- paint（重绘）：画颜色边框文字  
- composite：图层交给 GPU 拼起来  

改 `color` 通常只 paint；改 `width` 往往 reflow，更贵。这就是「为什么动画优先用 `transform` / `opacity`」的根。

**回流 vs 重绘**  
回流改几何，重绘改外观。大一那个 `.poem:hover { transform: scale(1.05) }` 用 transform 是对的；如果写成改 `margin`，就会回流。

**视口 viewport**  
浏览器可见区域。`width=device-width` 的 meta 就是在声明「别按桌面宽度缩放这块手机屏」。没有它，移动端 CSS 全白写。

**文档流 normal flow**  
块级元素自上而下、行内从左到右。`position: absolute / fixed`、`float`、flex/grid 的子项，是在改或离开文档流。大一满屏 `div` + 偶尔 `position: absolute` 做预览图，就是没建立「先流后脱离」的模型。

**事件循环 event loop**  
JS 单线程。调用栈跑完，再清空微任务（Promise.then、queueMicrotask），再画一帧，再取宏任务（setTimeout、事件回调）。  
`requestAnimationFrame`（大一 Logo 旋转用的）对齐的是「下一帧绘制前」，不是 setTimeout。

**微任务 / 宏任务**  
Promise 回调是微任务，`setTimeout(0)` 是宏任务。`async/await` 本质是 Promise。和 Java 线程池不是一类东西：这里没有真正的并行 JS（Web Worker 除外）。

**同源策略 same-origin policy**  
协议 + 域名 + 端口 一致才同源。这是浏览器的安全内核，不是 Spring 注解。

**CORS**  
跨源时浏览器拦响应（带 Origin 的请求）。后端加 `Access-Control-Allow-Origin` 是在**给浏览器看**，curl 从来不受 CORS 管。开发时 Vite proxy 把浏览器请求变成「同源 /api → 转发到 :8080」，所以开发环境可以假装没有跨域。

**Cookie / localStorage / sessionStorage**  
- Cookie：可随请求自动带给服务器；应标 `HttpOnly`（JS 读不到，防 XSS 偷 token）、`Secure`、`SameSite`  
- localStorage：域名下持久字符串，JS 可读，XSS 就能读  
- sessionStorage：标签页关了就没  

SPA 把 JWT 塞 localStorage 是常见图方便，安全上差一档。全栈默认更稳的是：**服务端 Session 或 HttpOnly Cookie**。

**XSS / CSRF**  
- XSS：恶意脚本进了你的页面（`innerHTML` 拼用户输入就是经典入口，大一索引页的 `innerHTML` 正好是这个形状）  
- CSRF：浏览器自动带 Cookie 的前提下，第三方站点替用户发请求。`SameSite=Lax/Strict`、CSRF token 是对策  

**CDN**  
把静态产物放到离用户近的节点。前端「上线」经常是：Nginx/CDN 托管 `dist/`，API 另走 `api.xxx.com`。

---

## 2. 结构 / 表现 / 行为（前端的三层，对应你大一揉在一起的那坨）

这是最老、也最重要的分层。Vue 没有取消它，只是把三层塞进一个 `.vue` 文件里。

| 层 | 语言 | 职责 | 大一的问题 |
|---|---|---|---|
| 结构 | HTML | 这是什么（标题、导航、图、段落） | 全是 `div`，意义在 class 名和文件夹名里 |
| 表现 | CSS | 它长什么样 | 一份 370 行全局表，颜色和宽度写死 |
| 行为 | JS | 它怎么动、怎么取数 | 和 CSS 抢同一个 `transform` |

### HTML 名词

**语义化 semantic HTML**  
`header nav main article figure footer button a` 不是审美，是给浏览器、屏幕阅读器、SEO 的类型系统。后端类比：别把所有表都叫 `data`。

**可访问性 a11y**  
键盘能用、对比度够、`alt` 是人话、按钮是 `button` 不是可点击的 `div`。全栈基本水平：不要求专家，要求不主动挖坑。

**表单与默认行为**  
`form` 提交会刷新页面（MPA 时代的默认）。SPA 里 `preventDefault` 后自己 `fetch`。

### CSS 名词

**盒模型 box model**  
每个元素 = content + padding + border + margin。`box-sizing: border-box` 让 width 包含 padding+border，现在是默认心智（要自己设或用 reset）。

**层叠 cascade / 继承 inheritance / 特异性 specificity**  
- 继承：字色、字号往下传；宽高不传  
- 特异性：`id` > `class` > `tag`；行内更高；`!important` 是逃逸舱  
- 层叠：同样特异性，后写的赢  

「我的样式为什么不生效」80% 是这三件事，不是 Vue 坏了。

**BFC（块格式化上下文）**  
一块独立排版区域。`overflow: auto`、`flex` 子项、`display: flow-root` 会创建。用来解释「margin 合并」「float 把父元素高度弄塌」。知道它存在即可，不必默写。

**flex vs grid**  
- flex：一维（一行或一列），导航、页头、按钮组  
- grid：二维（行和列同时），图集、整页骨架  

大一导航用 flex 是对的；图集也用 flex + 固定 `500px`，是该换成 grid 的地方。

**定位 position**  
`static`（默认，在流里）/ `relative`（占位但可偏移，给 absolute 当锚点）/ `absolute`（相对最近的非 static 祖先）/ `fixed`（相对视口）/ `sticky`（吸顶）。  
大一预览图 `position: absolute` + `pageX/pageY`，锚的是文档，不是组件，所以会和滚动较劲。

**层叠上下文 stacking context / z-index**  
`z-index` 不是全球整数大赛。`opacity < 1`、`transform`、`position`+`z-index` 都会开一个新上下文。子元素再高也出不去父级上下文。这是「我 z-index: 9999 怎么还被挡住」的答案。

**响应式 responsive / 断点 breakpoint / 移动优先 mobile-first**  
用 `@media (min-width: 768px)` 往上加桌面规则，而不是先写死桌面再到处 `max-width` 打补丁。  
`px` 是绝对像素；`rem` 相对根字号（做排版尺度）；`%` 相对父；`vw/vh` 相对视口。组件内部间距用 rem，栅格用 % 或 grid 分数。

**设计令牌 design token**  
颜色、间距、圆角、字号的命名变量。CSS 里就是 `:root { --color-brand: #246f27 }`。对标 `application.yml` 里的业务常量。组件库（Element Plus）内部也是一套 token，你「换主题」其实是在换 token。

**样式策略（必须能选，不要混用三种）**

| 策略 | 是什么 | 何时 |
|---|---|---|
| 全局 CSS | 一份 style.css | 小站、token、reset |
| scoped CSS | Vue SFC 里 `<style scoped>`，编译成属性选择器 | 默认首选 |
| CSS Modules | `Button.module.css`，类名被哈希 | React 圈常见 |
| Tailwind / UnoCSS | 工具类写在 markup 上 | 速度快，易变成「不会 CSS 只堆 class」 |
| CSS-in-JS | JS 里写样式 | 这站和 Vue 主流都不必上 |

架构命令：一个项目认一种组件样式方案 + 一份全局 token。Agent 最爱同时加 Tailwind 和 scoped 和内联 style——要拦。

**预处理器 Sass/Less**  
变量、嵌套、mixin。CSS 原生变量和嵌套已经吃掉大部分需求。新项目不是必选项。知道「老项目可能有 `.scss`」即可。

### JS 语言名词（和 Java 的错位）

**ES Module（`import` / `export`）**  
文件级模块，静态可分析，才能 tree-shaking。对标 Java 的 `import`，但文件 = 模块，没有 package 强制结构。

**CJS（CommonJS，`require`）**  
Node 老模块。前端打包器经常两边都要懂。浏览器不直接跑 `require`。

**闭包 closure**  
函数记得定义时的词法环境。大一 `rotateLogo` 能读到外面的 `isRotating`，就是闭包。Java 匿名类/lambda 捕获变量是亲戚。

**`this`**  
由调用方式决定，不是由定义位置决定（箭头函数除外，箭头捕获词法 this）。Vue 3 Composition API 几乎不碰 `this`，这是它相对 Options API 对后端同学友好的原因之一。

**Promise / async await / fetch**  
异步的统一货币。`fetch` 返回 Promise，HTTP 4xx 默认**不抛错**（和 axios 不同），只看 `response.ok`。这是后端同学第一天就会踩的坑。

**事件冒泡 bubbling / 捕获 capturing / 委托 delegation**  
点击子元素，事件往上冒到父。委托：在父上听，靠 `event.target` 分辨是哪个子。大列表不要给每一项绑监听。

**`key`（Vue 列表）**  
diff 算法用来认「这是同一个节点」。用 index 当 key，删除中间项时会认错人。对标数据库主键，不是数组下标。

---

## 3. 应用形态（架构第一问：页面怎么到用户眼前）

来一个产品，先选这个，再选框架。

| 名词 | 含义 | 类比 | 这个窝用不用 |
|---|---|---|---|
| **MPA** 多页应用 | 每个 URL 服务器回一整页 HTML | 传统 JSP / Thymeleaf | 大一实际就是 MPA（好几个 html） |
| **SPA** 单页应用 | 先回一个壳，以后路由在浏览器切，数据走 API | 前后端分离的管理后台 | Vue 重做后的默认形态 |
| **CSR** 客户端渲染 | JS 在浏览器里生成 DOM | 浏览器当模板引擎 | SPA 的默认 |
| **SSR** 服务端渲染 | 服务器跑一遍组件，先吐 HTML，再在浏览器「激活」 | Thymeleaf 但是组件还能接着交互 | SEO、首屏；这站不必 |
| **hydration 水合** | SSR 出来的 HTML 被 JS 认领，接上事件 | class 加载完，Spring 把 bean 接上 | SSR 配套名词 |
| **SSG** 静态生成 | 构建时把页面渲染成 HTML 文件 | 编译期把 JSP 跑完 | 内容几乎不变的站很合适 |
| **ISR / 增量生成** | SSG 但过期后后台再生成 | 带 TTL 的页面缓存 | 先不用管 |
| **Islands 岛屿架构** | 整体是静态 HTML，只有几个小岛是交互组件 | 页面大部分 JSP，一小块 React | 概念知道即可 |
| **渐进增强** | 先让 HTML 能用，再叠加 JS | 服务降级 | 表单、链接本应如此 |

**Nuxt / Next**  
在 Vue/React 上把 CSR/SSR/SSG 的选择做成框架约定。全栈基本水平：知道它们解决「渲染策略 + 路由 + 目录约定」，不是「Vue 的升级版」。这周末不必上。

**Hydration mismatch**  
服务器渲出来的 HTML 和浏览器第一轮虚拟 DOM 对不上。常见原因：用了 `Date.now()`、`window`、随机数。SSR 时才会遇到。

架构口诀：

- 内容型、更新少、要分享链接 → 先想 MPA 或 SSG  
- 登录后重度交互、表格表单 → SPA + API  
- 既要 SEO 又要交互 → SSR（Nuxt），成本明显高于 SPA  

呼气之窝：内容型。正确可以是 SSG。用 SPA 重做是为了**练和工作同构的形态**，不是因为产品必须 SPA。你要能说出这句话，才算读懂形态。

---

## 4. Vue 3：它到底吃掉了哪一层

Vue 吃的是「把 DOM 当手工活」和「把一页当一份 HTML 文件」。它不吃 CSS 基本功，也不吃你对「数据放哪」的判断。

### 核心名词

**SFC（Single File Component，`.vue`）**  
一个文件里三段：`<template>` 结构、`<script>` 行为、`<style>` 表现。编译期拆开。这就是「组件是三层的绑定包」。

**Options API vs Composition API**  
- Options：`data / methods / computed` 分块，Vue 2 主流  
- Composition：`setup` + `ref` 等按功能组织，Vue 3 默认该走这条  

后端同学用 Composition 更顺：一个 composable 就是一个 Service 方法簇。

**响应式 reactivity**  
数据变 → 依赖它的视图更新。底层是 Proxy。你不再手写 `innerHTML`。

**`ref` / `reactive`**  
- `ref`：包一层 `.value` 的盒子，基本类型、对象都能装  
- `reactive`：对象的深层 Proxy，不能换整对象替换得那么自然  

入门一律 `ref` 就够。Agent 两种混用时，让它统一。

**`computed`**  
只读派生。过滤后的相册列表就该是 computed，不要再 `watch` 一份去赋值。对标：别把 SQL 查出来的结果再抄到另一个字段里用触发器同步。

**`watch` / `watchEffect`**  
有副作用时才用：请求、打日志、和第三方插件同步。派生数据用 computed。后端人常见病：什么都 watch。

**生命周期 lifecycle**  
`onMounted`（挂到 DOM 后，才能碰元素）、`onUnmounted`（清定时器、关连接）。对标 `@PostConstruct` / `@PreDestroy`。大一 `requestAnimationFrame` 若组件销毁了还在转，就是没对上 unmount。

**props / emit**  
- props：父 → 子的输入，对标方法参数，应当只读  
- emit：子 → 父的事件，对标回调 / 领域事件  

**单向数据流**  
数据往下，事件往上。子组件改 prop 是架构味。`v-model` 是「prop + emit」的语法糖（默认 `modelValue` + `update:modelValue`）。

**slots 插槽**  
父往子的「结构坑」里塞模板。对标策略模式：按钮样式在子，按钮文字/图标由父决定。layout 的 `<router-view>` 也是一种出口。

**provide / inject**  
跨多层下发（主题、当前用户），避免 props 打钻。对标上下文 / ThreadLocal，滥用会变成隐式全局。能 props 就 props。

**composable（`useXxx`）**  
把一段有状态逻辑抽成函数：`useAlbums()`、`useAuth()`。对标 Service。**不持有 DOM，不关心路由页面长什么样。** Agent 常把请求写进组件 `onMounted`——你要让它下沉到 composable。

**指令 directive**  
`v-if` / `v-for` / `v-model` / `v-show`。`v-if` 是销毁重建，`v-show` 是 CSS 隐藏。列表必须带 `key`。

**Teleport**  
把 DOM 挂到 `body`（弹层、Lightbox），逻辑仍在组件树里。大一预览图 `position:absolute` 乱飞，正式做法是 Teleport + 固定层。

**KeepAlive**  
缓存组件实例，切走不销毁。标签页很合适。别拿它当数据缓存。

**Suspense**  
等异步子组件。知道即可。

**虚拟 DOM Virtual DOM**  
用 JS 对象描述 UI，diff 后最小改真实 DOM。Vue 3 编译期还能静态提升、补丁打到具体节点。你不需要手写 diff；你需要知道：**`key` 错了，diff 就会认错人。**

---

## 5. 路由、状态、服务端状态（前端的「事务边界」）

### 路由 Vue Router

**路由 route**  
URL → 组件。对标 `@GetMapping("/about")`。

**`params` vs `query`**  
- `/album/luoshifen` 的 `luoshifen` 是 params，资源身份  
- `?sort=new` 是 query，筛选视图  

可分享的状态优先放 URL，不要只放内存。刷新还在、能发给别人，这就是「状态是不是一等公民」。

**嵌套路由 nested routes**  
layout 里 `<router-view>` 再套子 view。对标有 layout 的 Thymeleaf fragment。

**懒加载路由**  
`() => import('./Gallery.vue')`，拆成单独 chunk。对标按模块拆 jar，不过发生在浏览器下载。

**导航守卫 navigation guard**  
`beforeEach`：没登录去 /join。对标 Spring Security 过滤器链。真正鉴权仍在后端；前端守卫只是体验和少打无效请求。

### 状态该放哪（架构核心题，Agent 最容易放错）

从「活得短」到「活得长」：

```text
1. 组件自己的 ref          展开没、输入框的字        像局部变量
2. 父组件 props 下来        相册列表给 PhotoGrid      像方法参数
3. URL query/params        当前专辑、页码            像 GET 参数，可分享
4. provide/inject          主题、当前用户            像请求级上下文
5. Pinia                   跨页且瞬时：购物车、未保存草稿
6. Cookie / storage        跨刷新：token、草稿备份
7. Spring + DB             跨用户、要审计、要权限     像真正的表
```

**Pinia**（Vue 3 官方状态库，Vuex 的继任）  
全局 store。对标进程内单例 Map。**不是数据库。刷新就没（除非你自己 persist）。**  
规则：直到第 1–4 层放不下，才开 store。图库筛选条件用 URL 或页面 ref，不要为了「规范」上 Pinia。

**Vuex**  
老全局状态。新项目默认 Pinia。知道名字避免听会时迷路。

**服务端状态 vs 客户端状态**  
- 服务端状态：相册列表，真相在服务器，前端是缓存副本  
- 客户端状态：弹窗开没开，服务器不认识  

**TanStack Query / 你们生态里的 swrv 等**  
专门管服务端状态：请求、缓存、失效、重试。对标「带 TTL 的只读缓存 + 加载态」。表格后台很值；这站几个 GET 用 `fetch` + `ref` 就够。你要能**说出何时才需要它**。

**乐观更新 optimistic update**  
先改界面，请求失败再滚回。对标先改内存再提交，失败补偿。

---

## 6. 工程化（从源码变成浏览器能跑的东西）

后端同学最容易低估这一层，又最容易在 Agent 生成的 `package.json` 面前放弃思考。

### 包与运行时

**npm / pnpm / yarn**  
包管理器。对标 Maven。`package.json` = `pom.xml`。锁文件（`package-lock.json` / `pnpm-lock.yaml`）= 锁定传递依赖，必须提交。

**`dependencies` vs `devDependencies`**  
运行要的 vs 构建/测试要的。浏览器最终包会被打包器打进去，和 Java `provided` 不完全一样，但心智接近：Jest 不该进生产包。

**semver / peerDependency**  
`^3.5.0` 允许小版本。peer 是「宿主得自己提供 Vue」，对标「我是 Spring Boot starter，你得有 Spring」。

**`node_modules`**  
下载下来的世界。不要提交。对标本地 Maven 仓库。

**Node.js**  
跑工具链的运行时，不是浏览器。浏览器 API（`window`）在 Node 里没有，反之 `fs` 在浏览器没有。SSR 时两边都跑，所以不能乱碰 `window`。

### 构建

**Vite**  
开发时：原生 ESM + 极快的 dev server（底层 esbuild 预构建依赖）。  
生产时：用 Rollup 打包成少量 JS/CSS。  
对标：开发用 DevTools 热加载，上线打 jar。

**Webpack**  
上一代打包器，生态巨大。老项目常见。新 Vue 项目默认 Vite。知道「打包器」这个职位即可。

**esbuild / Rollup / Terser**  
- esbuild：Go 写的极快转译/压缩  
- Rollup：库和 Vite 生产打包，tree-shake 好  
- Terser：老牌压缩  

**HMR（Hot Module Replacement）**  
改一个组件只换这一块，状态尽量保住。对标 Spring DevTools 重启，但更细。

**转译 transpile**  
TS/新语法 → 目标浏览器能懂的 JS。不是运行时魔法，是编译。

**polyfill**  
给老浏览器补 API（`Promise`、`fetch`）。转译改语法，polyfill 补对象。现代内部系统往往可以不管 IE。

**Babel**  
老牌转译器。Vite + TS 多数场景已不需要你直接配 Babel。

**tree-shaking**  
删掉没 `import` 到的导出。前提是 ESM 静态结构。副作用模块会吓跑它。

**code splitting / 动态 import**  
按路由拆文件，用户先下首页。对标按需加载模块。

**source map**  
压缩后的行号映射回源码。生产开不开是安全/可调试的权衡。

**环境变量**  
Vite：`import.meta.env.VITE_API_BASE_URL`，只有 `VITE_` 前缀会进浏览器包。  
**绝不要**把 Spring 的密钥放进 `VITE_`——那会打进每个人的 JS。对标：前端 env 是 `public` 配置。

**path alias**  
`@/components/PhotoGrid.vue`。对标 Java 的包名，避免 `../../../../`。

**proxy（开发服务器代理）**  
`/api` → `http://localhost:8080`。浏览器以为同源。生产由 Nginx 反代或网关做同样的事。

**`dist/`**  
`vite build` 的产物目录。对标 `target/*.jar`。上线上传的是它，不是 `src/`。

### 质量工具（名词级）

| 名词 | 干什么 |
|---|---|
| ESLint | 代码规则，对标 Checkstyle / SpotBugs |
| Prettier | 格式化，对标 Spotless |
| TypeScript | 类型，对标 Java 类型系统（结构性的，不是名义性的） |
| Vitest | 单元/组件测试，对标 JUnit |
| Playwright / Cypress | E2E，对标 Selenium |
| Storybook | 组件在隔离环境里展示，没有后端也能调 UI |

全栈基本水平：知道清单在，项目里至少 ESLint + TS（或 JSDoc）+ 锁文件。不是周末把测试金字塔搭完。

**TypeScript 对你的加成**  
接口 = DTO。`interface Photo { src: string; album: string }` 就是前端 Bean。`strict` 开起来后，props 类型 = 编译期校验。Agent 最爱 `any`——你的架构职责是禁止。

**结构化类型 vs Java 名义类型**  
TS 是「长得像就行」（duck typing + 结构）。Java 是「必须声明 implements」。所以 TS 里两个都叫 `{ id: string }` 的对象可以混用，这不是 bug。

---

## 7. 和 Spring 对接的那条缝（全栈真正开始的地方）

### 名词

**前后端分离**  
两个进程、两套部署、用 HTTP 契约说话。不是「两个 git 仓库」的同义词（也可以 monorepo）。

**BFF（Backend For Frontend）**  
为特定前端裁过的后端。移动端和 Admin 需要不同聚合时才值得。内部小站通常一个 Spring 就够。

**DTO / 契约 / OpenAPI**  
两边共用的形状。理想：一份 OpenAPI，Spring 实现，前端生成 client。最小：手写 TS interface，和 Java record 字段对齐。

**REST 在浏览器里的陷阱**  
- `fetch` 对 401/500 不抛异常  
- 错误体要约定（`{ code, message, details }` 或 RFC 7807 Problem Detail）  
- 列表要约定分页形状，别有的页 `{records,total}` 有的页直接数组  

**鉴权两种俗套路**

1. Cookie Session：Spring Security 默认思路，CSRF 要处理，SPA 也能用  
2. Bearer JWT：`Authorization` 头，前端存哪是难题  

全栈基本选择：内网管理系统 Cookie Session 往往更少坑；纯 API + 多客户端再 JWT。

**导航守卫 ≠ 安全**  
前端隐藏按钮不是权限。权限在 Spring 方法上。前端守卫只防「闪一下再跳登录」。

**上传**  
`multipart/form-data`。Nginx 要放 body 大小。前端要进度、类型校验、失败回滚。这是「配得上后端」的功能。

**WebSocket / SSE**  
双向推 vs 服务器单向推。知道有，本站用不到。

**幂等 / 重试**  
前端按钮连点、弱网重试。GET 可重试；POST 要幂等键或后端去重。这是全栈，不是「前端的事」。

---

## 8. 前端目录分层（给 Agent 的施工图）

后端你不会让 Agent 把 SQL 写进 Controller。前端同等约束：

```text
src/
  app/          启动、路由表、全局插件          ≈ Application 启动类 + Security 配置
  pages/        路由落地页，组合组件、拉数据     ≈ Controller
  layouts/      页头页脚壳                       ≈ 统一装饰器 / Filter 之后的外壳
  components/   可复用 UI，几乎不直接打 API      ≈ 公共视图碎片，Dumb
  composables/  有状态逻辑、请求、筛选           ≈ Service
  api/          HTTP 客户端、路径常量            ≈ Feign / RestClient
  stores/       Pinia（真需要才建）              ≈ 进程内缓存
  types/        DTO                              ≈ record / java bean
  styles/       reset + token                    ≈ 全局配置
  assets/       会走打包器的图和字体
```

**展示组件 vs 容器组件**  
- 展示（dumb）：只靠 props/slots 画画，emit 事件  
- 容器（smart）：知道 API、路由、store  

`PhotoGrid` 是 dumb，`GalleryPage` 是 smart。Agent 喜欢在 Grid 里直接 `axios.get`——打回。

**功能切片 vs 技术分层**  
上面是按技术角色分层（对 Spring 同学最顺）。另一种是按业务切：`features/album/` 里塞该功能的页面+组件+api。中型以上后台更合适。这站用技术分层就够。

**Feature-Sliced Design (FSD)**  
社区里一套更严的层：app / pages / widgets / features / entities / shared。名词知道，本项目不要上，过重。

**设计系统 / 组件库**  
按钮、输入框、间距、颜色的统一实现。Element Plus / Naive UI / Arco 是别人的设计系统。  
全栈基本水平：会用库，且知道**产品站不该被 Admin 库绑架**。呼气之窝用 Element Plus 是架构错误，不是效率。

**原子设计 Atomic Design**  
atom → molecule → organism → template → page。认识即可。实践中 dumb/smart + 目录约定更值钱。

---

## 9. 性能与体验（名词级，能做选择即可）

| 名词 | 含义 | 你要能说的一句话 |
|---|---|---|
| **LCP** | 最大内容绘制，首屏主图/标题出现 | 英雄图要压缩、别被 JS 挡住 |
| **INP** | 交互到下次绘制的延迟 | 别在点击处理器里干重活 |
| **CLS** | 布局抖动 | 图片写死宽高，别让图加载完把字挤下去 |
| **Core Web Vitals** | 上面三个的谷歌集合 | 对外站点才认真；内网后台知道即可 |
| **懒加载 lazy load** | `loading="lazy"` 或路由级拆包 | 图多必做 |
| **`srcset` / 响应式图** | 不同屏下载不同尺寸 | 大一原图 4000px 塞进 250px 槽就是反面教材 |
| **瀑布请求 waterfall** | 先 JS 再发现还要 JSON 再发现还要图 | SSR/SSG 或把关键数据内联可打掉 |
| **缓存头** | `Cache-Control`、文件名带 hash | Vite 产物带 hash，可长期缓存 |

---

## 10. 架构决策清单（以后每个需求先过一遍）

把这一节当成你对 Agent 的系统提示。需求进来，按顺序答，答完再让它写代码。

### A. 这是哪类状态？

1. 只是开没开、输到哪 → 组件 `ref`  
2. 要能分享 / 刷新还在 → URL  
3. 跨页但不要持久 → 才考虑 Pinia  
4. 跨用户 / 要权限 / 要审计 → Spring  

### B. 这是哪类 UI？

1. 只有这里用 → 写在页面里，别急着抽  
2. 两处以上、且 props 能说清 → `components/`  
3. 带请求、带规则 → 逻辑去 `composables/`，UI 仍 dumb  
4. 按钮输入框是否真的需要组件库？产品站先手写，Admin 再上库  

### C. 这是哪类样式？

1. 颜色间距圆角 → token（`:root` 或主题文件）  
2. 仅此组件 → scoped  
3. 全局 reset / 排版 → `styles/`  
4. 不要第三种方案「顺便」进来  

### D. 这是哪类渲染？

1. 内部工具、登录后 → SPA 够了  
2. 对外内容、几乎不变 → SSG 更好  
3. 对外且每人看到的不一样、又要 SEO → 再谈 SSR  

### E. 这配得上后端吗？

配：写入、权限、计费、审计、跨端一致  
不配：文案、主题色、导航顺序、一页短诗  

### F. 对 Agent 的约束句式（直接复制）

> 按 `pages / components / composables / api` 分层。  
> 页面组合，组件不打 HTTP。  
> 筛选结果用 computed，不上 Pinia。  
> 可分享状态放路由 query。  
> 样式只用 scoped + 已有 token，不准新增 Tailwind/组件库。  
> DTO 写 TypeScript interface，禁止 `any`。  
> 先给目录和接口契约，我确认后再写实现。

最后一句是架构师的牙：**先契约后实现**。和你 review Spring PR 时先看 Controller 签名是同一反射。

---

## 11. 周末怎么过（真正的速通日程）

假设你有两个完整白天。目标是「名词能讲给别人听」，不是把窝重构完。

### 周六上午（2.5h）— 浏览器 + 三层

1. 读本文 §0–§2。  
2. 打开现在的 `demo.html` + `style.css` + `script.js`，用总图给每一段代码贴层标签：这是结构 / 表现 / 行为 / 产物 / 源码。  
3. 口头回答：  
   - 为什么 `file://` 下 `fetch` JSON 会挂？（同源 + 不是 HTTP）  
   - Logo 的 CSS `transform` 和 JS `transform` 为什么打架？（同一绘制属性两个主人）  
   - `.header` 的 `z-index` 很大却仍可能被挡住？（层叠上下文）

### 周六下午（2.5h）— 形态 + Vue 把什么吃掉

1. 读 §3–§4。  
2. 对着本站四页导航，画两张图：MPA（现在） vs SPA（Vue Router 之后 URL 怎么变）。  
3. 把「关于页一张图」走一遍数据流，写在纸上：  
   `image 文件 → JSON 字段 → 谁 fetch → 哪个组件 props → 哪个 img src`  
4. 用 Spring 话说一遍：哪一段是 Entity，哪一段是 Service，哪一段是 Controller，哪一段是 Thymeleaf。

### 周日上午（2.5h）— 状态 + 工程化

1. 读 §5–§6。  
2. 只做选择题，不要写代码：  
   - 当前专辑筛选放哪一层？  
   - 入群二维码放哪一层？  
   - 管理员上传新图放哪一层？  
3. 打开一个工作里的 Vue 项目 `package.json` + `vite.config`（没有就看任意 Vite 模板），把每个字段用本文名词标出来：依赖、脚本、proxy、alias。  
4. 找到工作项目里的一次 `axios.get`，问：它是服务端状态还是客户端状态？有没有错误体约定？401 谁处理？

### 周日下午（2h）— 全栈缝 + 指挥 Agent

1. 读 §7–§10。  
2. 选工作中最近一个需求，用 §10 的 A–E 写五句话决策（真的写下来）。  
3. 用 §10-F 的约束，让 Agent 只输出：目录树 + `Photo` 的 TS interface + 两个 API 路径。**不准它写组件实现。** 你 review 这张施工图。  
4. 自测：合上文档，默写总图，说出 20 个词各自在哪一层。不会的再翻索引。

---

## 12. 自测：这些你能用一句话说给同事，才算这周末过关

1. DOM 和虚拟 DOM 不是同一个东西。  
2. CORS 是浏览器规则，curl 不遵守。  
3. SPA / SSR / SSG 解决的是「HTML 在哪生成」，不是「用不用 Vue」。  
4. composable 不是组件，store 不是数据库。  
5. `computed` 是派生，`watch` 是副作用。  
6. 可分享状态优先放 URL。  
7. Vite 开发吃 ESM，上线打的是 `dist/`。  
8. `VITE_` 变量会进每个人的浏览器，密钥不能放。  
9. 前端路由守卫不是权限。  
10. 组件库是别人的设计系统，产品站可以不用。  
11. `fetch` 4xx 默认不抛。  
12. `key` 是列表的主键。  
13. scoped CSS 解决的是特异性隔离，不是「我会 CSS 了」。  
14. Token（设计令牌）和 JWT 不是一个词。  
15. 指挥 Agent 时，层和契约先于代码。

说不全就针对性重读对应节，不要回头去刷 20 小时 Vue 入门课——那会把你带回「会写页面」而不是「会选层」。

---

## 附录：名词索引（按字母，快速反查）

- **a11y** §2 — 可访问性  
- **alias** §6 — 路径别名 `@/`  
- **async/await** §2 — Promise 语法糖  
- **BEM**（补充）— 一种 class 命名：`block__element--modifier`，全局 CSS 时代用来防冲突；有 scoped 后重要性下降  
- **BFF** §7  
- **box model** §2  
- **cascade / specificity** §2  
- **CDN** §1  
- **code splitting** §6  
- **composable** §4  
- **computed / watch** §4  
- **CORS / 同源** §1  
- **CSR / SSR / SSG / hydration** §3  
- **CSRF / XSS** §1  
- **design token** §2  
- **dist** §6  
- **DOM / CSSOM** §1  
- **dumb / smart 组件** §8  
- **emit / props / slots** §4  
- **ESM / CJS** §2 §6  
- **ESLint / Prettier** §6  
- **event loop / 微任务** §1  
- **fetch vs axios** §2 §7  
- **flex / grid** §2  
- **HMR** §6  
- **HttpOnly Cookie** §1 §7  
- **KeepAlive / Teleport / Suspense** §4  
- **key** §2 §4  
- **layout / paint / reflow** §1  
- **MPA / SPA** §3  
- **navigation guard** §5  
- **npm / pnpm / package.json** §6  
- **Nuxt / Next** §3  
- **Pinia / Vuex** §5  
- **polyfill / transpile / Babel** §6  
- **provide/inject** §4  
- **proxy** §6  
- **reactivity / ref / reactive** §4  
- **responsive / rem / viewport** §1 §2  
- **Rollup / esbuild / Webpack / Vite** §6  
- **Sass** §2  
- **SFC / scoped** §4  
- **semver / peerDependency** §6  
- **source map** §6  
- **stacking context** §2  
- **TanStack Query / 服务端状态** §5  
- **tree-shaking** §6  
- **TypeScript 结构类型** §6  
- **v-model 是语法糖** §4  
- **Virtual DOM** §4  
- **Vite env `VITE_`** §6  
- **Vue Router params/query** §5  
- **Web Vitals LCP/INP/CLS** §9  

---

读完后的能力边界（防止自我膨胀）：

你现在应当能 **review Agent 的前端 PR：指出状态放错层、样式策略被污染、不该出现的组件库、密钥进了前端 env、页面组件里打了 HTTP**。  
你还不应当自称能从零手写一套设计系统或 SSR 框架。那是下一阶段，用呼气之窝第 1 遍重构去练手，不是用更多名词去堆。
