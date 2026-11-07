# dsh-project-kit

把 [Claude-Code-Development-Kit](https://github.com/peterkrueck/Claude-Code-Development-Kit) 的 `/prime` 与 `/update-docs` 工作流移植为 **DeepSeek Harness** 技能。

在 DSH 里，`/` 菜单本身就是技能入口：输入 `/prime`，host 会找到同名技能并把指令正文注入给模型。所以原有的肌肉记忆不需要改变——参数也保留，`/prime --full`、`/prime api 加限流` 照常工作。

## 它解决什么

长周期项目里，agent 每次开工都要重新"认识"这个项目：它做什么、结构在哪、当前进展如何。全量读文档浪费上下文，不读又容易凭记忆瞎断言。

这套技能把这件事拆成两半：

- **`/prime`** —— 进项目先加载地图：spec 目录 + 开头的不变量 + 结构 Map，再按任务定向读具体章节。默认轻量（约 4–6k tokens），`--full` 才全量。
- **`/update-docs`** —— 架构真的变了才写文档。只写"现在是什么样"，激进删减过时内容，同一条事实只存一处。

## 安装

```bash
git clone https://github.com/<you>/dsh-project-kit.git
cd dsh-project-kit
./install.sh
```

默认用软链接装到 `~/.dsh/skills/`（用户级，所有项目可用），`git pull` 后即刻生效。

| 选项 | 作用 |
|---|---|
| `--copy` | 复制而不是软链（仓库搬家后不会失效） |
| `--project <dir>` | 装到 `<dir>/.dsh/skills/`（项目级，可随仓库共享） |
| `--force` | 覆盖已存在的同名技能 |
| `--uninstall` | 移除这两个技能 |
| `--help` | 用法 |

也可以手动把 `skills/` 下的两个目录复制到 `~/.dsh/skills/`。DSH 会热监听该目录，新技能无需重启。

## 用法

```bash
/prime                      # 轻量：spec 目录 + 开头不变量 + 结构 Map
/prime --full               # 全量（设计/架构评审时用）
/prime -p                   # 额外加载 progress.md（路线图与实时进度）
/prime --deploy             # 额外加载部署与基础设施文档
/prime api 给登录加限流        # 只读 api 相关章节
/update-docs                # 架构有变化才写；纯 bug 修复会直接说"没什么可写"
```

参数解析规则：`--full` / `-p|--progress` / `--deploy` 可出现在任意位置；剩下第一个能匹配 `spec.md` 的 `##` 标题或顶层目录的词视为模块；其余为任务描述。匹配不到模块就当任务文本，不会瞎猜。

## 文档约定

技能读写这几个文件：

```
docs/ai-context/
├── spec.md                       # 产品做什么：功能、接口契约、数据流
├── project-structure.md          # 文件树、技术栈、目录组织（## Map 是 /prime 读的部分）
├── progress.md                   # 已完成、在做、卡在哪
└── deployment-infrastructure.md  # 托管、账号、密钥、CI/CD
AGENTS.md                         # 项目规则、架构决策、编码约定
```

**新项目第一次用**：先 `/update-docs`，它会从现有代码生成这套文档；之后 `/prime` 才有东西可读。文档缺失时 `/prime` 会明确告诉你，并退化成 README + manifest + 顶层目录的粗略勘察，不会编造设计事实。

## 与上游的差异

不是直接搬文件，有四处必须改，否则在 DSH 上会失效或误导：

| 上游 | DSH 移植 | 原因 |
|---|---|---|
| frontmatter `user_invocable` | `user-invocable` | DSH 只认连字符；写错不报错，但整个技能会被静默丢弃 |
| `AGENTS.md` 是给 Codex 的只读"第二意见顾问"人设 | 技能把 `AGENTS.md` 当项目规则文件；同时加载 `CLAUDE.md` 时合并而非并存 | DSH 会同时把两者当项目指令加载，照搬会让 agent 以为自己只读 |
| 命令内含可编辑的 Module Map | 自动匹配 `spec.md` 的 `##` 标题或顶层目录 | 全局技能无法按项目配置，改为零配置推断 |
| Claude Code 的 `Read`/`Glob`/`@`-引用 | `read`（offset/limit）/ `glob`/`grep`，禁止 `cat` 整篇 | DSH 工具名与加载语义不同 |

除此之外，`/review-work`、`/deploy`、`/merge`、`/verify` 以及 review-on-stop 钩子**没有**移植——它们依赖 Claude Code 的子代理约定与 hooks 机制，需要单独适配。`/review-work` 尤其适合 DSH 的 `subagent` / `workflow` 并行评审模型。

## 仓库结构

```
skills/
├── prime/SKILL.md
└── update-docs/
    ├── SKILL.md
    └── references/doc-templates.md   # 首次生成 docs/ai-context 的骨架
install.sh
```

## 致谢与许可

工作流设计、方法论与文档模板来自 [peterkrueck/Claude-Code-Development-Kit](https://github.com/peterkrueck/Claude-Code-Development-Kit)（MIT）。本仓库是面向 DeepSeek Harness 的移植与改写，同样以 MIT 发布，详见 [LICENSE](LICENSE)。
