# 图片索引数据契约

当前契约版本：**1**

## 所有权与生成方式

`pages/json/image_index.json` 由 `scripts/generate-image-index.py` 根据 `image/` 自动生成，不应手工编辑。页面消费者是 `js/image-index.js`。

## JSON 结构

```json
{
    "version": 1,
    "images": [
        {
            "id": "螺狮粉/1.jpg",
            "src": "../image/螺狮粉/1.jpg",
            "album": "螺狮粉",
            "caption": "1.jpg",
            "alt": "螺狮粉：1.jpg"
        }
    ]
}
```

## ImageRecord 字段

- `id`：图片相对 `image/` 的唯一路径，使用正斜杠，不以 `/` 开头。
- `src`：相对 `pages/image-index.html` 的可访问 URL，必须以 `../image/` 开头，只使用正斜杠。
- `album`：图片所在的顶层目录；直接位于 `image/` 的文件使用 `root`。
- `caption`：页面显示的文字，当前为包含扩展名的文件名。
- `alt`：预览图片的替代文本，当前由相册名和文件名组成。

## 不变量与兼容性

- 每条记录必须且只能提供以上五个非空字符串字段。
- `id` 和 `src` 必须唯一，不允许 Windows 反斜杠。
- 记录按 `id` 不区分大小写排序，确保重复生成结果稳定。
- 支持 `.gif`、`.jpeg`、`.jpg` 和 `.png`，扩展名判断不区分大小写。
- 删除或重命名字段属于破坏性变更，必须提升顶层 `version` 并同步更新消费者。
