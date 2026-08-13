# Research Project Builder（研究项目构建器）

[![CI](https://github.com/Roblis0n/research-project-builder/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/Roblis0n/research-project-builder/actions/workflows/smoke-test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version: 0.2.1](https://img.shields.io/badge/version-0.2.1-blue.svg)](CHANGELOG.md)

[English](README.md) · [简体中文](README.zh-CN.md) · [English Skill](SKILL.md) · [中文 Skill](SKILL.zh-CN.md)

![Research Project Builder：从粗略想法到可执行研究](assets/social-preview.png)

把一个粗略研究想法变成可执行、有证据支撑的研究项目，而且不把记忆中的“空白”伪装成真实研究缺口。

```text
粗略想法                    战略决策门                    实时证据                       可执行选题
“生成式 AI 与研究生   ->    D1-D7 路线决策          ->   实时网页来源 + 证据矩阵  ->   3-5 个边界清楚的方案，
科研生产力”                  用户明确授权                                                    1 个默认推荐
```

先过决策门，再检索；只有你明确授权后才进入检索；只有记录了实时网页证据，才能判断选题、研究缺口和创新性；只有形成暂定选题后，才展开理论、方法和模型。

## 安装

需要 Git、Python 3.10+，以及 Codex Desktop、Codex CLI 或 Codex IDE 扩展。以下两种范围二选一；不要同时安装两个同名 skill 副本。

### 用户级：所有仓库都可使用

macOS/Linux：

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Roblis0n/research-project-builder.git "$HOME/.agents/skills/research-project-builder"
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
git clone https://github.com/Roblis0n/research-project-builder.git "$HOME\.agents\skills\research-project-builder"
```

### 仓库级：只在当前仓库中使用

在目标仓库根目录执行。

macOS/Linux：

```bash
mkdir -p .agents/skills
git clone https://github.com/Roblis0n/research-project-builder.git .agents/skills/research-project-builder
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force ".agents\skills" | Out-Null
git clone https://github.com/Roblis0n/research-project-builder.git ".agents\skills\research-project-builder"
```

Codex 会自动检测 skill 变化；如果没有出现，重启 Codex。以上目录遵循 [Codex 官方 skill 加载范围](https://developers.openai.com/codex/skills#where-codex-loads-local-skills)。

### 构建独立 Codex 插件

仓库根目录是可直接安装的 canonical **skill**，不是可安装插件目录。
根目录的 `.codex-plugin/plugin.json` 只是构建输入；标准
`skills/research-project-builder/` 插件布局只存在于新鲜构建的发布产物中。

在仓库外的新同级目录构建产物：

```text
python scripts/build_plugin_package.py --output ../research-project-builder-release/research-project-builder
```

插件校验、归档和安装只能使用生成的
`../research-project-builder-release/research-project-builder/`。打包器拒绝仓库内部
输出和已存在目标，先在同一文件系统的临时同级目录完成全部构建，再原子重命名发布。
每次发布都使用新目标；不要复用 `dist/` 或旧打包目录。
产物字节只读取 Git 索引对象，不读取工作树中未暂存的草稿。运行打包器前，必须先暂存
所有准备发布的改动。
安装包同时包含规范运行入口 `SKILL.md` 和供人阅读的中文对照版
`SKILL.zh-CN.md`。

## 必须显式调用

本项目有意关闭隐式调用。请在 Codex 新任务中准确输入：

```text
$research-project-builder 请把这个粗略想法变成可执行的研究项目：生成式 AI 与研究生科研生产力。先运行战略决策门；在我明确授权默认策略或修改后的策略之前，不要检索。
```

skill 会先在 Codex 对话中展示七项决策门，然后停止。要授权 Stage 1，请明确回复，例如：

```text
按默认策略执行。
```

这句话只授权实时检索和选题落地，不授权 Stage 2。生成文件只是审计材料，主要结果必须直接展示在 Codex 对话里。

## 最终会得到什么

- **Stage 0 — 战略决策门：** 目标产出、不可改变的核心、数据现实、方法上限、创新与可行性的平衡、时间窗口、当前阶段。
- **Stage 1 — 证据支撑的选题落地：** 已记录的实时来源、结构化来源清单、证据矩阵、最相近与相邻研究、3-5 个可执行选题，以及 1 个不强迫用户选择的默认推荐。
- **Stage 2 — 可选展开：** 理论、构念、假设或命题、数据方案、基线、候选模型、指标、稳健性检查、MVP、12 周计划、风险、降级路线和写作结构。

Research Project Builder 的角色是战略研究架构师，不是自动选题生成器。它只让用户决定真正会改变路线的事项；不会让用户承担论文筛选、理论有效性、模型有效性或统计技术适配性的专家判断。

## 可复现实例

[实例指南](examples/README.md)把每个阶段对应到仓库中的示例或离线 fixture：

- [Stage 0 粗略输入](examples/stage0_input.md)；
- [实时网页来源记录样例](examples/live_web_sources.sample.json)；
- [Stage 1 输出结构](examples/stage1_mock_output.md)；
- [Stage 2 输出结构](examples/stage2_mock_output.md)；
- [离线 Stage 1 fixture](tests/fixtures/topic_output/)，包含直接展示文本、来源日志、证据矩阵和选题推荐。

### 生成并验证 Stage 0

在本仓库根目录执行：

```bash
python scripts/render_strategic_gate.py --idea "generative AI and graduate student research productivity" --out-dir outputs/stage0-demo
python scripts/validate_output.py --out-dir outputs/stage0-demo --mode stage0 --user-input "rough idea only" --project-root .
```

查看 `outputs/stage0-demo/codex_inline_response.txt` 可检查生成的审计文件。在真实 Codex 任务中，应把其中内容直接展示在对话中，并在检索前停止。合法的 Stage 0 不会生成 `live_web_sources.json`、`search_manifest.json` 或 `evidence_matrix.csv`。

### 验证离线 Stage 1 fixture

以下命令验证证据与授权契约，但不会把 fixture 中的记录冒充为当前文献检索：

```bash
python scripts/record_live_web_sources.py --out-dir tests/fixtures/topic_output --validate-only
python scripts/validate_output.py --out-dir tests/fixtures/topic_output --mode topic --user-input "Use default strategy" --project-root .
```

该 fixture 可重复、无需联网。它证明的是产物契约，不是当前的创新性或研究缺口状态。

## 工作流与命令说明

下文假定当前目录就是 skill 安装目录。如果从宿主工作区运行，应给 `scripts/` 加上真实安装前缀，例如 `.agents/skills/research-project-builder/scripts/`，并把 `--project-root` 设为该 skill 目录。

### Stage 0：检索前必须先过门

使用上面已经验证的 Stage 0 命令，然后把 `codex_inline_response.txt` 直接展示在 Codex 中。用户未明确授权 Stage 1 前，不得检索、构造选题或写完整方案。

### Stage 1：先有实时证据，后做选题判断

用户明确授权后，Codex 按以下顺序执行：

1. 用 `expand_keywords.py` 把粗略想法展开成可审计检索词。
2. 用 `preflight_web.py` 做网页检索预检。
3. 由 Codex 执行真实、当前的网页检索。
4. 在判断选题、缺口或创新性之前，用 `record_live_web_sources.py` 记录检索结果。
5. 用 `search_literature.py` 检索结构化学术 API；它只能补充，不能取代实时网页检索。
6. 归一化、去重、评分，并生成 `evidence_matrix.csv`。
7. 判断选题适配度，生成 3-5 个候选，渲染 Codex 直接回复，再验证输出。

Stage 1 必须存在 `live_web_sources.json`、`search_manifest.json` 和 `evidence_matrix.csv`。准确的来源记录格式见 [examples/live_web_sources.sample.json](examples/live_web_sources.sample.json)；真实运行时必须把其中的演示 URL 和元数据替换成当次实际检索到的来源。

### Stage 2：选题落地后才展开

Stage 2 必须已经有暂定选题和 Stage 1 证据。用户明确说“把默认选题展开成完整项目方案”等指令后，才授权理论、方法与模型展开。之后在同一运行目录上依次使用 `recommend_theory_method_model.py`、`write_project_plan.py`、`render_codex_response.py --mode expansion` 和 `validate_output.py --mode expansion`。

## 证据与安全边界

- Stage 0 永远先于检索。
- 默认推荐不等于授权；Stage 1 必须获得用户明确回复。
- 没有 `live_web_sources.json`，就不能给出最终选题、研究缺口、创新性、数据集、基准、理论现状、方法现状、模型现状或报告规范判断。
- 结构化 API 元数据不能取代 Codex 实时网页检索，也不能取代全文阅读。
- 所有创新性与缺口措辞都必须限定在已记录的检索范围内，绝不能声称“绝对空白”。
- 不保证发表。
- 不会仅凭一个粗略想法就写完整项目方案。
- 用户可见的主要结果直接显示在 Codex 中；文件只负责保留审计轨迹。

合格表述示例：“在本次检索范围内，尚未发现高度相似研究；在收紧结论前，还需要补充领域数据库检索或引文追踪。”

## User-Agent 配置

结构化学术 API 使用可识别的 User-Agent 通常更稳定。进行实时运行前，建议配置：

macOS/Linux：

```bash
export RPB_USER_AGENT="research-project-builder/0.2.1 (mailto:you@example.com)"
```

Windows PowerShell：

```powershell
$env:RPB_USER_AGENT = "research-project-builder/0.2.1 (mailto:you@example.com)"
```

如果未设置，脚本会使用内置的后备 User-Agent。

## 开发检查

```bash
python -c "import pathlib, py_compile; [py_compile.compile(str(path), doraise=True) for path in pathlib.Path('scripts').glob('*.py')]"
python -m unittest discover -s tests
```

测试全部离线运行。Stage 1 的证据行为通过仓库 fixture 检验，不调用网络。

## 仓库结构

```text
research-project-builder/
  SKILL.md                         # 工作流说明与阶段门
  AGENTS.md                        # 贡献者/代理执行规则
  agents/openai.yaml               # Codex 界面与调用策略
  assets/templates/                # 审计产物模板
  references/                      # 工作流与质量控制资料
  scripts/                         # 可执行辅助脚本
  examples/                        # 引导式示例
  tests/fixtures/topic_output/     # 可重复的 Stage 1 fixture
  tests/                           # 离线单元与契约测试
  .github/workflows/smoke-test.yml # CI
```

## 局限

- API 元数据可能缺少方法、样本、理论和局限信息。
- 实时检索质量受检索词广度、来源选择、访问权限和检索日期影响。
- 最终文献综述仍需阅读全文，结构化 API 不能替代这一步。
- 即使选题有证据支撑，也可能因数据不可得、伦理限制、测量薄弱或时间窗口不现实而失败。
- 生成的方案是执行脚手架，不是发表保证。

## 贡献与许可

策略优先的贡献要求见 [CONTRIBUTING.md](CONTRIBUTING.md)，许可见 [MIT License](LICENSE)。
