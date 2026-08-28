# 呼气之窝 · 全栈指挥与面试实践手册

本文合并本仓库上几轮讨论的全部结论，供回家后继续练。  
对象：Spring 后端为主、Vue 会调接口、前端基础停在大一、日常大量用 Agent、痛点是**不会给前端任务写准提示词、不懂文件夹和数据流、做项目像开盲盒**。

名词细节见 [frontend-architecture-map.md](./frontend-architecture-map.md)。  
现有站点怎么跑见 [Agent.md](../Agent.md)。

---

## 1. 你的真实缺陷（不是「Vue API 记得少」）

开盲盒的原因只有三个，对应指挥 AI 时缺的三张图：

| 缺的图 | 表现 | AI 收到的提示词就会变成 |
|---|---|---|
| **层图** | 不知道这是样式问题、状态问题还是契约问题 | 「帮我修一下图库」「优化一下页面」 |
| **目录图** | 不知道这段代码该进哪个文件夹 | Agent 自己建 `utils/helpers/lib`，你事后才看见 |
| **数据流图** | 不知道数据从哪来、谁持有、谁只负责画 | 组件里直接 axios，筛选结果再抄进 Pinia |

你在后端其实会这三张图：Controller 不写 SQL、Service 不返回 HTTP 状态码、DTO 先于实现。前端不会，是因为从没把这套肌肉接到浏览器上。

**指挥 AI 的最小合格提示词，必须回答四句：**

1. 用户看见什么变化（验收）  
2. 代码放进哪个目录、哪个文件（位置）  
3. 数据从哪读、谁持有、谁展示、谁写入（流向）  
4. 不准做什么（边界）

缺任何一句，Agent 都会替你做架构决策——这就是盲盒。

---

## 2. 大一项目：当时短视在哪（压缩版）

不是写得丑，是把每一页当成海报，而不是会长大的系统。

1. **复制粘贴当架构** — 页头导航五份，`contact.html`「加入我们」链到 `about.html`。没有单一事实来源。  
2. **内容写死在 HTML，又半吊子做了数据库** — `about.html` 手贴 `<img>`，`main.py` 扫盘生成 JSON 却只给索引页用。数据层服务了错误的页面。  
3. **路径按「我在哪个文件夹」想** — 根页 `css/`，子页 `../css/`。`index.html` 跳 `demo.html`。后来加了 `fetch`，仍按双击 HTML 的心智走。  
4. **文件系统当 CMS** — 中文目录、emoji、QQ 截图文件名就是全部语义。  
5. **只为鼠标 + Windows + 自己的屏幕** — 全是 hover；宽高写死 px；Logo 的 CSS `transform` 和 JS `transform` 互抢。

做对了的：静态站选型、一份 CSS/一份 JS、开始写 `main.py`、栏目用文件夹分桶。重构时留人格和静态，不要上 Element Plus 把玩梗站做成后台。

对照现在的工作：管理端从组件库抄页面、`v-model` + axios，是另一种海报思维——海报换成了 `el-table`。

---

## 3. 文件夹存什么（背这一张，指挥时直接点名）

先认一个原则：**按角色分层，不按「我今天写的文件」乱放。**  
和 Spring 一一对应，不要发明第三套。

### 3.1 目标前端（Vue3 + Vite）— 你指挥 AI 时用这套

```text
src/
  app/            启动、挂路由、全局插件           ≈ 启动类 + 全局 Filter
  pages/          路由落地页：组合组件、决定拉什么数 ≈ Controller
  layouts/        页头 / 导航 / 页脚               ≈ 统一外壳（只一份）
  components/     可复用 UI，几乎不打 HTTP          ≈ dumb 视图
  composables/    有状态逻辑：取数、筛选、鉴权      ≈ Service
  api/            路径常量和 fetch/axios 封装       ≈ Feign / RestClient
  stores/         Pinia，真需要才建                ≈ 进程内 HashMap
  types/          DTO / interface                  ≈ Java record
  styles/         reset + 设计令牌（颜色间距圆角）   ≈ application.yml 里的常量
  assets/         要走打包器的图、字体
  router/         路由表                           ≈ @RequestMapping 清单
```

谁允许依赖谁（依赖只能朝下）：

```text
pages → layouts / components / composables / stores
composable → api / types
components → types（最多），禁止 → api
api → 无业务 UI
```

**Agent 违规信号（看见就纠偏，不要自己动手改完）：**

- `components/PhotoGrid.vue` 里出现 `axios` / `fetch`  
- 为了筛选上了 `stores/album.ts`  
- 新建 `utils.js` 塞所有东西  
- 页面里复制了一份页头而不是用 `layouts/`  
- 出现 `any`、把密钥写进 `VITE_`  
- 顺手加了 Element Plus / Tailwind（本项目未批准）

### 3.2 现有仓库（大一静态站）— 对照，别混

```text
index.html              跳转壳，不是真首页
demo.html               真首页
css/style.css           全站唯一样式（全局，无分层）
js/script.js            Logo 彩蛋
pages/*.html            各海报页
pages/json/             生成的图片清单
pages/main.py           扫 image/ 的脚本
image/                  静态图，文件夹名 = 栏目
```

第 1 遍重构仍可以先静态，但**意识上**已经按 3.1 的角色想：导航只存在一份，内容是 JSON，页面是投影。

### 3.3 若接 Spring（第 3 遍才需要）

```text
PhotoController     GET 列表 / POST 上传
领域对象            Album, Photo（id, album, caption, objectKey）
uploads/ 或对象存储 文件本体
Security            写接口要登录；读可以公开
```

前端 `api/` 只认识 HTTP 契约，不认识表。

---

## 4. 数据怎么走（把盲盒变成流水线）

每次功能先在纸上画这一条，再写提示词。缺这一条，Agent 一定会把数据塞进最方便的那个文件。

### 4.1 状态从短命到长命（选一层，不要跳）

```text
1. 组件 ref              弹窗开没开、输入框的字
2. props 父→子           相册数组交给 PhotoGrid
3. URL query/params      当前专辑、页码（可分享、可刷新）
4. provide/inject        主题、当前用户（别滥用）
5. Pinia                 跨页且瞬时；不是数据库
6. cookie / storage      跨刷新；token 优先 HttpOnly Cookie
7. Spring + DB           跨用户、权限、审计、写入
```

口诀：**能分享的放 URL；能丢的放组件；要算账的放后端。**

### 4.2 读路径（图库：用户打开 /gallery?album=luoshifen）

```text
浏览器 URL
  → Vue Router 把 query.album 交给 GalleryPage（pages/）
  → 页面调用 useAlbums()（composable）
  → useAlbums 调 api/photos.ts
       ├─ 第 2 遍：读 src/data/albums.json（或 /content/*.json）
       └─ 第 3 遍：GET /api/albums/luoshifen/photos
  → 返回 Photo[]（types/Photo）
  → 页面用 computed 按 query 过滤（不要再存一份 filtered）
  → 把 photos 当 props 传给 PhotoGrid（components/）
  → PhotoGrid 只负责画，点击 emit('select', photo)
  → 页面打开 Lightbox（仍是 props + emit）
```

对照 Spring：Router ≈ 映射，Page ≈ Controller，composable ≈ Service，api ≈ Feign，component ≈ 模板碎片。

### 4.3 写路径（登录后上传，第 3 遍）

```text
Join/Admin 页表单
  → 页面校验类型和大小（体验，不是安全）
  → api.postPhoto(formData)
  → Vite 开发 proxy /api → localhost:8080
  → Spring 鉴权、存文件、写 DB
  → 返回 Photo DTO
  → 前端让列表失效再拉一次（或插入返回值）
  → 401：跳登录；4xx：页面展示 message（fetch 默认不抛，必须看 ok）
```

安全边界：**前端校验可绕过；权限只在 Spring。** 路由守卫只是少闪一下。

### 4.4 本仓库现在实际怎么走（反面教材，要能讲）

```text
关于页：HTML 里写死 src → 浏览器直接拉 /image/...
索引页：fetch pages/json/image_index.json
          JSON.path 还是 Windows 反斜杠
          文件名当展示文案
main.py：扫盘覆盖 JSON，说明文字保不住
```

面试若问「你怎么看旧项目」，就讲这条流：内容、元数据、展示混在一起，所以改一张图要改 HTML，生成脚本和主页面还不是同一数据源。

### 4.5 一张图的字段（DTO，提示词里要写出来）

```ts
interface Photo {
  id: string
  src: string        // URL 正斜杠，不是 Windows 路径
  album: string      // luoshifen | nailong | tuanjian | ...
  caption: string    // 给人看的一句
  alt: string        // 无图时的话，不是 "1"
}
```

没有这个 interface 就让 Agent 写页面 = 没有 DTO 就让人写 Controller。

---

## 5. 给 AI 的提示词怎么写（结束开盲盒的那一招）

### 5.1 标准任务包（复制填空）

```markdown
## 目标（用户可见）
- 打开 /gallery 能按专辑筛选图片；刷新后筛选还在。

## 层与位置（不准自行改分层）
- 页面：src/pages/GalleryPage.vue
- 列表 UI：src/components/PhotoGrid.vue（dumb，只收 props）
- 取数：src/composables/useAlbums.ts
- 契约：src/types/photo.ts
- 数据：先读 src/data/albums.json（不要上 Pinia，不要打真实后端）

## 数据流
- 当前专辑来自 route.query.album
- useAlbums() 返回全部 Photo[]
- 过滤用 computed，不另存 filteredList
- PhotoGrid 只接收 photos，点击 emit('select', photo)

## 验收
- 375 和 1280 宽度都能看
- 改 JSON 加一张图，刷新后出现，不改组件
- 直接打开 /gallery?album=luoshifen 应已选中该专辑

## 禁止
- 不准加 Element Plus / Tailwind / Pinia
- 不准在 components 里 fetch
- 不准 any；不准把密钥写入 VITE_
- 不准改无关页面

## 交付顺序
1. 先输出：将改动的文件列表 + Photo interface + 函数签名
2. 等我确认
3. 再写实现
4. 自己写验收步骤（我怎么点）
```

第 1 步单独发，是关键。Agent 一旦直接开写，你就又在开盲盒。岗位职责第 3 条「引导 AI 自行修正，而非直接替 AI 重写」的前提，就是你手里有这份契约可以对照。

### 5.2 坏提示词 vs 好提示词

坏：

> 用 Vue 把图库做一下，好看一点，参考现在的 about。

好：上面的任务包。差别不在礼貌，在**位置、流向、禁止、先契约**。

纠偏（Agent 把 axios 写进了 PhotoGrid）：

> PhotoGrid 出现了 fetch，违反「组件不打 HTTP」。不要重写整个页面。把请求移回 useAlbums，Grid 只留 props photos 和 emit select。先给出修改 diff 说明，再改文件。

仍不替它重写；指出层错误 + 范围 + 再交付顺序。

### 5.3 按问题类型选层（前端报错时你要先分类）

| 你看见的现象 | 多半是哪层 | 提示词里点名 |
|---|---|---|
| 样式不生效 / 挡不住 / 移动端挤爆 | CSS：特异性、层叠上下文、断点 | 只改 styles 或该组件 scoped，禁止改结构「试试 flex」乱打 |
| 刷新丢了筛选 | 状态放错，应进 URL | 从 ref 改到 query，不要上 Pinia |
| 开发能拉数，部署不能 | 环境 / 代理 / 相对路径 | 问 VITE_API_BASE、生产 Nginx、有没有用 file:// |
| 按钮连点创建两条 | 写入无幂等 | 后端去重 + 前端 disabled，两边都写进任务 |
| AI 加了一个新 UI 库 | 越权 | 回滚依赖，只用现有 token |
| 页面空白，控制台 CORS | 浏览器规则，不是 Spring「坏了」 | 开发走 proxy；不要让它乱加 @CrossOrigin 打补丁了事 |

分类错了，提示词再长也是盲盒。

### 5.4 审查清单（AI 交代码后，你按这个看，不按「能不能跑」）

- [ ] 文件是否落在指定目录  
- [ ] 依赖方向有没有被打破（组件 → api）  
- [ ] 状态是否落在约定的那一层  
- [ ] DTO 和界面字段是否一致  
- [ ] 失败态 / 空态 / 加载态有没有（只 happy path 就不算生产级）  
- [ ] 有没有密钥、有没有 `any`、有没有多余依赖  
- [ ] 你能否用它写的验收步骤点一遍  

生产级 ≠ 能跑。岗位职责第 2 条卡的就是这份清单。

### 5.5 验证（岗位职责第 4 条，你现在最空）

本仓库目前没有测试。最低配，今晚就能要求 Agent 做：

- 启动方式写进 README：`python -m http.server` 或 `npm run dev`  
- 关键路径手测步骤（打开 URL、点筛选、刷新）  
- 有 JS/TS 之后：给纯函数（过滤相册）写 Vitest，不当摆设  
- 配置脱敏：禁止提交密钥、`.env` 进 gitignore  

「AI 验证」= 让第二个 Agent **只读 diff，按审查清单打分**，不让原作者自己说通过。一面常问这个，先有流程比有工具重要。

---

## 6. 学习总路线（同一产品三遍，不要周末直接 vue create）

| 遍 | 产物 | 补的图 |
|---|---|---|
| 第 1 遍 | 静态站：根路径、一份导航、CSS 变量、grid、移动端 | 结构/表现/行为 |
| 第 1.5 遍 | `content.json` 驱动关于页和图库，ES module | 数据流（无框架） |
| 第 2 遍 | Vue3 + Vite + Router，dumb/smart，TS 的 Photo | 目录图 + 组件边界 |
| 第 3 遍 | Spring 只接查询和登录上传 | 全栈边界 |

禁止第 1 遍就上 Element Plus。那会回到工作里的「会拼后台」。  
技术约束：第 1 遍禁止 Vue/React/Tailwind/组件库；打开方式必须是 HTTP。

---

## 7. 对那份岗位：周末后能否「马马虎虎」达到

先拆岗位，再给判断。它不是前端岗，是 **AI 协同开发岗**；一面会同时打「你会不会做」和「你会不会指挥」。

### 7.1 对照

| 职责/能力 | 周末读完名词之后 | 还差什么才算马马虎虎 |
|---|---|---|
| 1 用 AI 完成分配任务 | 后端任务：已接近。前端任务：仍会把层选错 | 用本文任务包在本仓库跑完 **一次「先契约后实现」闭环** |
| 2 审查到生产级，不是能跑就行 | 能抓住「放错文件夹、组件打 HTTP、密钥进 VITE_」 | 还审不了精致 CSS/无障碍；异常与空态要刻意练 | 
| 3 拆任务引导 AI 改，不替它重写 | 方法已经有（第 5 节） | 必须真的忍住不自己改；今晚练习 3 就是考这个 |
| 4 自动化验证 + AI 验证 | **未达标**。本项目零测试 | 至少补：手测步骤 + 一条纯函数测试 + 第二 Agent 审 diff |
| 熟悉至少一个主流栈 | Spring 算。前端 Vue 仍是「会调接口」 | 面试用 Spring 当主栈诚实说；前端讲层和数据流，不装熟组件库 |
| AI 工具实际经验 | 你有使用量 | 要能讲：规则文件（Agent.md）、先契约、审查清单、何时终止重试 |
| 结构 / 异常 / 脱敏 / 文档 | 大一项目是反面教材 | 把反面讲清楚是加分；正面要有一份 README 和脱敏意识 |
| 冷静拆解 | 性格项 | 用「先分类再提示词」代替连砸三次「再试试」 |

### 7.2 结论（直接）

- **若一面按这份 JD、主栈是 Java/Spring：** 周末后 + 今晚把第 10 节练习做完，**有可能马马虎虎过「会用 AI 干活、知道不能能跑就行」的叙事**。弱项一定会被问到：验证、生产级审查例子、前端别开盲盒。不要吹已经能审查任意前端 PR。  
- **若面试官把你当全栈、要你当场指挥 AI 改 Vue 图库：** 只读名词不够。至少要有一次本仓库的指挥闭环（练习 3）才能开口不虚。  
- **「生产级」三个字：** 现在还没有。标志是：空态/错态、配置脱敏、可重复验证、依赖没被 Agent 私自升级。这些不是再读一晚名词能冒出来的，是你在审查清单上打勾打出来的。

所以：这轮学习把你从「开盲盒」推到「能画出施工图」；岗位要的是「拿着施工图把 AI 收到生产级」。中间那一步必须靠今晚和这周的实践，不是靠继续收藏文章。

诚实说法（面试可用）：

> 后端 Spring 我能独立设计和审查。前端我过去会开盲盒，原因是没有层、目录和数据流。我现在用同一套 Spring 分层去约束 Vue：页面当 Controller，composable 当 Service，组件不打 HTTP，可分享状态放 URL。指挥 AI 我要求先出文件列表和 DTO 再写代码。验证还在补自动化，目前至少有手测步骤和第二 Agent 审 diff。

---

## 8. AI 协同岗一面会问什么

风格按你贴的标准：**和常见技术岗一面相似，每题展开聊。** 下面每题给「他们想听什么 / 你可以怎么讲 / 别踩的坑」。结合呼气之窝与 Spring 经历说，不要背定义。

### Q1 你平时怎么用 AI 写代码？从接到任务到合并，走一遍。

想听：有流程，不是「我跟它聊天」。  
讲：读现有 Agent.md / 规则 → 自己先写任务包（目标、位置、数据流、禁止、验收）→ 先要文件列表和签名 → 确认再实现 → 按审查清单看 diff → 跑验收 → 必要时第二 Agent 只读审查。  
坑：只说「我用 Cursor 很快」。

### Q2 给一个模糊需求「做个图库」，你的第一轮提示词写什么？

想听：第 5.1 节那种，不是「请用 Vue3 实现精美图库」。  
展开：你会先问清 URL 是否要带筛选、数据在 JSON 还是 API、有没有登录上传。需求不清时，提示词里的「先契约」会暴露你在选层。  
坑：一上来让它选技术栈。

### Q3 AI 已经能跑了，你怎么判断是不是生产级？

想听：第 5.4 清单，尤其失败态、脱敏、分层、范围。  
结合本项目：能列出图片 ≠ 生产级——Windows 路径、innerHTML、无空态、无测试、密钥意识都没有。  
坑：只说「我再让 AI review 一次」却说不出看什么。

### Q4 模型反复改不对，你怎么办？什么时候自己写，什么时候继续引导？

想听：职责 3。分类错误（第 5.3）→ 缩小范围 → 提供正确上下文（现有文件路径、DTO、反例）→ 限制「只改这两个文件」。  
自己写的时机：规则层/安全（鉴权、脱敏）连续三次仍错；或你自己也说不清契约——那时停下来补契约，不是开干。  
坑：要么永远手写，要么死循环「再试试」。

### Q5 如何防止 AI 改爆范围？（删了无关文件、升级了 Vue、加了 Tailwind）

想听：禁止项写进提示词；有 Agent.md；看 git diff 的文件列表先于看代码；lockfile 变更要单独解释。  
本仓库例子：不批准组件库却加了 Element Plus，直接打回，不要在它的基础上「顺便用用」。

### Q6 你怎么给 AI 正确的上下文？上下文不够或太多分别会怎样？

想听：最小充分集。给：目录约定、相关 DTO、将改的文件、禁止项。不给：整本 node_modules、无关的关于页段子、五份复制的页头。  
不够：它发明 `utils/request2.ts`。太多：它改错文件。  
规则文件（Agent.md）= 稳定上下文，比每轮粘贴强。

### Q7 前端这段代码（组件里 axios + 筛选放 store + any）有什么问题？你怎么让 AI 改？

想听：现场 review。答：打破依赖方向；筛选不该是全局状态，该是 URL 或 computed；any 丢掉契约。纠偏提示词见 5.2。  
这是本轮学习后最该能答的题，等于开不开盲盒的考试。

### Q8 CORS 报错，AI 给 Controller 加了 `@CrossOrigin(origins="*")`，你签不签？

想听：全栈边界。开发应用 Vite proxy；生产用网关/Nginx 同源反代；`*` 加 Cookie 时是错的。CORS 是浏览器规则，不是业务开关。  
坑：觉得能跑就合。

### Q9 密钥、token 应该放哪？AI 写了 `VITE_SECRET_KEY`。

想听：`VITE_` 会进每个人的 JS。密钥只在 Spring。JWT 若必须在前端，也优先 HttpOnly Cookie，而不是 localStorage（XSS 可被读）。  
生产级的「配置脱敏」就落在这题。

### Q10 怎么验证 AI 的交付？测试写不出业务怎么办？

想听：分层验证。纯函数（过滤、格式化）必须有单测；页面有手测步骤/E2E；契约可用快照或 OpenAPI。业务测不了时先测不变式：401 无 token 失败、空列表走空态、路径正斜杠。  
诚实：本项目还在补，但你知道最低配是什么。

### Q11 你熟悉的技术栈工程实践有哪些？AI 生成的 Spring 代码你看什么？

想听：主栈深度。分层、事务边界、空指针、N+1、DTO 不把 Entity 甩到前端、日志不打敏感信息。  
转前端：用同一套标准映射到 pages/composable/api。面试官在确认你不是「只会催 AI 的人」。

### Q12 让你给这个大一仓库写 Agent.md，你会写什么？

想听：规则文件意识。跑法、路径陷阱、不要改的风格、生成 JSON 的命令、已知 bug。仓库里已经有一份，你可以讲你会怎么改成「第 1 遍重构约束」。

### Q13 SPA / SSR / SSG 这个站该用哪个？AI 建议上 Nuxt，听不听？

想听：形态选择。内容站 SSG 更合适；上 SPA 是为了和工作同构练手；Nuxt 对这个体量过重。能拒绝 AI 的技术虚荣。

### Q14 你和 AI 谁对代码质量负责？

唯一正确答案：你。AI 是生成器。岗位把审查写成核心职责，就是在筛「出了锅怪模型」的人。

### Q15 现场：把「关于页改成数据驱动」拆成任务列表（不要写代码）。

示例拆法（面试就说这个粒度）：

1. 定义 Photo / Album DTO  
2. 把现有图片收成 `content/albums.json`（正斜杠、caption）  
3. 关于页改为读取 JSON 渲染（先 Vanilla 或先 Vue 页面，二选一说死）  
4. `main.py` 改为 merge 而不是覆盖 caption  
5. 验收：新增一张图只改 JSON + 文件  
6. 禁止改导航视觉、禁止上组件库  

拆完再让 AI 做步骤 1 的契约。这就是职责 1 + 3。

---

## 9. 口述提纲（今晚对镜子讲，每题 90 秒）

1. **开盲盒是什么：** 我以前只说「做个图库」，文件夹和数据流由模型决定，所以每次结果不可复现。  
2. **我现在怎么指挥：** 四句话——验收、位置、流向、禁止；先文件列表和 DTO。  
3. **前端怎么分层：** pages ≈ Controller，composable ≈ Service，components 不打 HTTP，Pinia ≠ DB，可分享状态放 URL。  
4. **生产级：** happy path 不够；要空态错态、脱敏、diff 范围、能复述验收步骤。  
5. **这个旧项目：** 海报式 HTML、两套数据源、Windows 路径、hover-only；我会把它当反面教材讲，而不是当作品吹。

---

## 10. 今晚回家练习（做完才算这轮学习结束）

不要继续读。读不是闭环。下面三件是岗位职责的缩小版。

### 练习 1 — 画两张图（25 分钟，纸或白板）

1. 目录图：把 3.1 的树抄一遍，在旁边写「允许依赖谁」。  
2. 数据流：把 4.2 图库读路径画成箭头，从 URL 画到 `<img>`。  

合上文档能画出来，才算不是收藏。

### 练习 2 — 写提示词但先不发给 AI（30 分钟）

题目：把关于页改成数据驱动（不要 Vue，就当第 1.5 遍，读 JSON）。  
用 5.1 模板填满。写完用 5.4 清单自问：Agent 若把 innerHTML 拼进页面、若覆盖 caption、若用反斜杠，你的禁止项有没有挡住。

### 练习 3 — 指挥闭环（45～60 分钟，核心）

对任意 Agent（Cursor / Claude Code / 本环境）只发下面这段，**不要加需求：**

> 不要改业务代码。根据 docs/practice-playbook.md 第 3.1 和 4.5 节，输出：  
> 1）若用 Vue3 重做呼气之窝，src 目录树  
> 2）Photo 的 TypeScript interface  
> 3）图库筛选的数据流（谁读 URL，谁 fetch，谁持有，谁绘制）  
> 禁止实现组件。等我确认。

你要做的：对照本文挑错。目录多了 `utils/`、上了 Pinia、没有 `types/`、数据流从组件 fetch，都算它败、你胜——你得写出纠偏提示词（练习职责 3），仍不自己写代码。

过关：你能指出至少两处偏离，并且第二轮它按你的层改对了。

### 练习 4 — 面试（选做，30 分钟）

Q2、Q7、Q8、Q14 出声讲。录下来听有没有具体例子。没有呼气之窝或工作项目细节的，都是空话。

---

## 11. 文档与讨论对照（避免你以为「还有东西在聊天里」）

| 轮次 | 结论落点 |
|---|---|
| 探索仓库，写 Agent.md | `../Agent.md` |
| 大一短视与重构方向 | 本文 §2、§6 |
| 三遍实现转全栈 | 本文 §6；细节仍按那次回复的周历执行 |
| 周末名词速通 | `frontend-architecture-map.md` |
| 文件夹 / 数据流 / 提示词 / 岗位评估 / 面试 | 本文 §1、§3–§10 |
| 喂给 OpenClaw 的完整提示词 | `docs/openclaw-prompt.md` |

从今晚起，实践记录建议直接补在本文末尾「实践日志」，不要再散落聊天。

---

## 12. 实践日志（你来写）

### YYYY-MM-DD

- 练习 1：目录图 / 数据流 能否默画：
- 练习 2：提示词链接或粘贴：
- 练习 3：Agent 第一轮偏在哪；你的纠偏原话；第二轮是否按层改对：
- 仍开盲盒的瞬间（什么需求、缺了四句里的哪句）：
- 明天只练一件事：
