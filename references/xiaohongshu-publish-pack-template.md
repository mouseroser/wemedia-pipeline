# Xiaohongshu Publish Pack Template

用于 `wemedia` 在 Step 6 产出标准小红书发布包，交给 `main` 调 `xiaohongshu` skill 执行。

## 填写模板

```text
平台：xiaohongshu
内容ID：{{content_id}}
标题：{{title}}
正文：
{{body}}
#{{tag1}} #{{tag2}} #{{tag3}}
图片路径：
- {{image_path_1}}
- {{image_path_2}}
标签：{{tag_csv}}
可见性：{{visibility|默认=public}}
备注：{{notes|可选}}
```

## 最小可用要求
- 标题 ≤20字
- 正文建议 ≤1000字
- 图片路径至少 1 张，且必须是绝对路径
- 标签建议 ≤10 个

## 保存位置
`~/.openclaw/workspace/intel/collaboration/media/wemedia/xiaohongshu/{content_id}.md`
