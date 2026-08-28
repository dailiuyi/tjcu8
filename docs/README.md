# 文档索引（回家后从这里进）

这是呼气之窝相关讨论的持久化入口。下一棒 Agent **先读本页**，再按表选文件。不要从聊天记录重建上下文。

## 交接到哪了（2026-08-28）

| 项 | 状态 |
|---|---|
| 学习文档 | 已进 `master`。结论都在 playbook，不必翻聊天 |
| 第 1 遍重构（静态站纠结构） | **没开始。** 禁止先改业务代码 |
| 练习 1～3 | **没做。** 回家主线 |
| 站点代码 | 仍是大一静态站原样 |
| 当前分支 | `master`，工作区干净，已与 `origin/master` 同步 |

**下一棒默认任务：** 把 [openclaw-prompt.md](./openclaw-prompt.md) 整段贴给 Agent，按 playbook 第 10 节从练习 1 开始。不要先 `vue create`，不要先修导航 bug。

## 仓库怎么用

- 远程：`https://github.com/1753262762/tjcu8.git`
- 干活分支：**`master`**（文档和站点都在这）。GitHub 默认分支也是 `master`。
- 另有孤立的 `main`：GitHub 网页上传的旧树，**没有 `docs/`，不要在 `main` 上继续。**
- 跑站点（必须 HTTP，不要 `file://`）：

```bash
python -m http.server 8080
```

打开 `http://localhost:8080/`。`index.html` 会立刻跳到 `demo.html`。

- 改完 `image/` 之后：`python pages/main.py`（会覆盖 `pages/json/image_index.json`，不要手改 JSON）

## 按今晚要干什么选文件

| 文件 | 干什么 |
|---|---|
| [practice-playbook.md](./practice-playbook.md) | **主文档。** 缺陷诊断、文件夹职责、数据怎么走、给 AI 的提示词模板、岗位评估、面试题与口述提纲、今晚练习 |
| [frontend-architecture-map.md](./frontend-architecture-map.md) | 名词地图。遇到不认识的词来这里反查，挂回总图 |
| [../Agent.md](../Agent.md) | 给编码 Agent 看的仓库说明书（现有静态站怎么跑、路径陷阱） |
| [openclaw-prompt.md](./openclaw-prompt.md) | **整段复制喂给 OpenClaw。** 回家继续练时用 |

阅读顺序（今晚 2～3 小时）：

1. `practice-playbook.md` 第 1、3、4、5 节（缺陷、目录、数据流、提示词）
2. 做第 10 节练习 1～3（画图、写提示词、不出手让 AI 只出契约）
3. 第 8、9 节面试题，挑 4 道出声讲
4. 词不懂再翻 `frontend-architecture-map.md`

## 已知坑（看见了也不要顺手改）

这些是反面教材，第 1 遍有契约再动：

- `pages/contact.html` 的「加入我们」链到了 `about.html`
- `image_index.json` 的 `path` 是 Windows 反斜杠
- 关于页手贴 `<img>`，索引页才读 JSON：两套数据源
- 页头导航在每个 HTML 里复制一份
- Logo 的 CSS `transform` 和 JS `transform` 互抢

## 下一棒禁止

- 练习没做完之前，禁止「先把站点重构了」
- 第 1 遍禁止 Vue / React / Tailwind / Element Plus / 任何组件库
- 禁止把玩梗文案改成官网口吻
- 禁止从 `main` 开新提交
- `logs/` 不要提交；密钥不准进前端

练习记录写在 `practice-playbook.md` 末尾「实践日志」，不要再散落聊天。
