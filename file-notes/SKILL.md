---
name: file-notes
description: 当你想记录或查看文件和文件夹的用途、备注时使用。
  当你想定期整理电脑文件标注时使用。
disable-model-invocation: true
---

# File Notes

记录文件和文件夹的用途和描述。下次看到这个文件夹，就知道它是干嘛的。

## 工具

配套的 Python 脚本在 skill 目录下：

```
file-notes.py lookup <路径>                  # 查询路径记录
file-notes.py add <路径>                      # 添加记录（交互式）
file-notes.py add <路径> --desc <描述>         # 添加记录（非交互式）
file-notes.py list                            # 列出所有记录
file-notes.py review                          # 审查待标注的路径
file-notes.py export                          # 导出记录
```

数据保存在 `~/.file-notes/data.json`。

## 流程

用户运行 `/file-notes` 时：

### 1. 了解意图

先问用户这次想做什么：

- **扫描指定路径下的子文件夹并记录** → 进入第 2 步
- **查询某个路径的记录** → `file-notes.py lookup <路径>`
- **列出所有记录** → `file-notes.py list`
- **导出记录** → `file-notes.py export`

### 2. 扫描路径并推理记录

当用户指定一个路径（如 `D:\Program Files (x86)`）：

1. 列出该路径下所有子文件夹
2. 对每个文件夹：
   - 优先根据文件夹**名称**推理它的用途（如 `Steam` → 游戏平台）
   - 名字不确定的，看文件夹内的文件（.exe、.dll、配置文件等）辅助判断
3. 调用 `file-notes.py add <路径> --desc <推理结果>` 写入 JSON
4. 全部完成后，展示一份汇总清单给用户

### 3. 主动查询

用户也可以随时查某个文件夹的记录：

```
file-notes.py lookup D:\某个文件夹
```

## 注意事项

- 不要替用户决定"能不能删"——只记录用途描述
- 推理来源标注要清晰（如"看名字推断：Steam 游戏平台"）
- 名字不明确的才看内容，避免过度扫描
