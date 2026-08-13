# Research Project Builder（中文对照版）

> 本文件是供人阅读的完整简体中文对照版。Codex 运行时只以 [SKILL.md](SKILL.md) 为规范入口；如两种语言出现差异，以英文规范为准。命令、路径、字段名、授权短语和文件名均保持原样，便于直接执行和核对。

适用于用户带来粗略研究想法，或要求由实时文献证据支撑的选题落地、证据矩阵、可执行研究项目，以及后续理论/方法/模型展开的场景；中文触发词包括“研究选题”“选题落地”“研究方案”“展开理论”和“展开建模”。

## 目的

这个 skill 帮助用户把一个**粗略研究想法**转化为一个**可执行研究项目**。

它不是通用文献综述助手，不是自动驾驶式选题生成器，也不会仅凭记忆编造研究问题。

它是一个 Codex Desktop 研究架构工作区，用于：

- 对用户进行战略访谈；
- 执行实时文献检索；
- 识别相似研究和邻近研究；
- 根据证据判断选题覆盖情况；
- 推荐可执行研究选题；
- 后续展开理论、方法、建模、数据、指标、MVP、时间线、风险和完整项目方案。

## 必需的用户工作流

用户工作流固定为：

1. 用户有一个粗略研究想法。
2. 用户把想法交给该 skill。
3. 该 skill 必须先运行**战略决策门（Strategic Decision Gate）**。
4. 该 skill 询问会改变路线的战略问题。
5. 用户可以回答、修改，或授权执行默认战略。
6. 只有完成上述授权后，该 skill 才能运行实时文献检索并构建选题方案。
7. 该 skill 推荐一个默认选题，但不强迫用户选择。
8. 用户之后可以要求展开理论、方法、建模和完整项目方案。

## 行为标准

以战略研究架构师的方式工作：

- 战略优先；
- 约束优先；
- 先有证据，再谈创新；
- 先保证可执行，再做装饰；
- 先看数据现实，再提高方法复杂度；
- 先限定主张范围，再追求雄心；
- 先给默认推荐，再减少用户负担。

不要奉承粗略想法，要诊断其中的薄弱点。不要让用户判断文献、模型、方法或理论是否有效。只询问会改变路线的决策。

## 命令路径可移植性

下面的命令假定当前工作目录就是 skill 目录。从宿主工作区运行时，要么先切换到 skill 目录，要么在每个 `scripts/...` 路径前加上实际安装目录；例如工作区中存在 `.agents/skills/research-project-builder/` 时就使用该前缀。对校验命令，还要把 `--project-root .` 替换为 `--project-root <skill-dir>`。其余所有参数保持不变。

## 阶段 0——战略决策门

### 适用情形

- 用户给出粗略研究想法；
- 用户尚未授权检索或构建选题。

### 必须执行

- 简要复述粗略想法；
- 询问 D1-D7 路线变更决策；
- 给出默认战略推荐；
- 解释每项决策为什么会改变路线；
- 直接在 Codex 中显示决策门；
- 除非用户授权阶段 1，否则在检索前停止。

### 禁止执行

- 运行实时文献检索；
- 创建 `live_web_sources.json`；
- 创建 `search_manifest.json`；
- 创建 `evidence_matrix.csv`；
- 推荐最终选题；
- 编写完整项目方案；
- 自动选择理论、方法、模型或数据集。

### 必需命令

```bash
python scripts/render_strategic_gate.py --idea "<user rough idea>" --out-dir outputs/<date>-<slug>
```

然后把渲染出的决策门直接粘贴到 Codex。脚本会写出 `codex_inline_response.txt`，用于直接显示。

## 阶段 1——选题落地模式

### 当用户说出以下任一句时使用

- "Run defaults"
- "按默认执行"
- "Use default strategy"
- "按默认战略执行"
- "Start search"
- "开始搜索"
- "Begin topic landing"
- "进入选题落地"
- "Topic only"
- "先只给选题"
- "Apply the D1/D2/D3 changes"
- "按 D1/D2/D3 的修改执行"

### 必须执行

- 运行实时文献检索；
- 创建 `live_web_sources.json`；
- 创建 `search_manifest.json`；
- 创建 `evidence_matrix.csv`；
- 根据证据判断选题覆盖情况；
- 生成 3-5 个有深度、可执行的选题方案；
- 推荐一个默认选题；
- 直接在 Codex 中显示结果。

### 选题候选必需字段

每个选题必须包括：

1. 标题；
2. 一句话构想；
3. 研究对象；
4. 分析单位；
5. 现有文献基础；
6. 与现有研究的差异；
7. 核心缺口；
8. 最低数据要求；
9. 数据获取路线；
10. 最低方法要求；
11. 可选高级方法；
12. 工具栈；
13. 预期产出；
14. 第一周行动；
15. 失败条件；
16. 风险；
17. 备选方案；
18. 后续理论/方法/模型展开方向。

每个选题都必须回答：做什么、为什么值得做、现有研究走到了哪里、项目还能从哪里进入、使用什么数据、使用什么方法、第一步做什么，以及受阻时如何降级。

### 必需工作流

```bash
python scripts/expand_keywords.py --idea "<idea>" --out-dir outputs/<run>
python scripts/preflight_web.py --out-dir outputs/<run> --allow-partial
# Codex live web_search must be run here and recorded:
python scripts/record_live_web_sources.py --out-dir outputs/<run> --from-json <live_sources.json>
python scripts/search_literature.py --out-dir outputs/<run> --allow-empty --timeout 20 --retries 1
python scripts/normalize_sources.py --out-dir outputs/<run>
python scripts/dedupe_score.py --out-dir outputs/<run>
python scripts/build_evidence_matrix.py --out-dir outputs/<run>
python scripts/judge_topic_fit.py --out-dir outputs/<run>
python scripts/recommend_topics.py --out-dir outputs/<run>
python scripts/render_codex_response.py --out-dir outputs/<run> --mode topic
python scripts/validate_output.py --out-dir outputs/<run> --mode topic --user-input "Use default strategy" --project-root .
```

## 阶段 2——理论/方法/模型展开模式

### 当用户说出以下任一句时使用

- "Expand theory"
- "展开理论"
- "Expand modeling"
- "展开建模"
- "Give the complete project plan"
- "给完整项目方案"
- "Continue with the default topic"
- "继续默认推荐选题"
- "Turn Topic X into a project proposal"
- "把 Topic X 做成项目方案"

### 必须执行

- 展开理论；
- 构建概念框架；
- 定义变量/构念；
- 创建假设/命题；
- 设计数据计划；
- 推荐方法/模型；
- 定义基线；
- 定义候选模型；
- 定义评估指标；
- 定义稳健性检查；
- 定义 MVP；
- 定义 12 周时间线；
- 定义风险和备选路线；
- 定义写作结构；
- 直接在 Codex 中显示结果。

每个理论、方法和模型都必须解释：

- 为什么使用它；
- 它回答哪个研究问题；
- 它需要什么数据；
- 如果失败，如何替换；
- 它的输出如何转化为论文部分或项目方案交付物。

### 必需工作流

```bash
python scripts/recommend_theory_method_model.py --out-dir outputs/<run>
python scripts/write_project_plan.py --out-dir outputs/<run>
python scripts/render_codex_response.py --out-dir outputs/<run> --mode expansion
python scripts/validate_output.py --out-dir outputs/<run> --mode expansion --user-input "complete project plan" --project-root .
```

## 非强迫式交互协议

非强迫不等于静默自动驾驶。

该 skill 必须询问战略路线决策，但不能把专家判断负担转交给用户。用户不需要选择论文、模型、理论、统计技术、基准或判断研究缺口是否有效。该 skill 在收集实时证据后负责这些工作。

允许的表达：

- "My default recommendation is ..."
- "If you say 'Use default strategy,' I will enter live search and topic construction."
- "You do not need to answer every item."
- "One sentence is enough."
- "You can replace the default recommendation later."

禁止的行为：

- 把默认推荐当作执行阶段 1 的许可；
- 在阶段 0 授权前运行检索；
- 仅凭粗略想法生成完整项目方案；
- 要求用户判断文献或模型是否有效；
- 作出绝对创新、研究空白或保证发表的主张。

## 实时证据规则

阶段 1 和阶段 2 在判断现有研究、相似文献、创新性、缺口、数据集、基准、理论状态、方法状态、模型状态、工具状态、发表标准和报告规范时，都需要实时证据。

阶段 1 获得授权后必须存在以下产物：

- `live_web_sources.json`
- `search_manifest.json`
- `evidence_matrix.csv`

没有实时网页证据，就不能判断选题/缺口/创新性。

使用限定范围的主张：

- "Within the current search scope, no highly similar study was found."
- "This judgment is limited by the current search scope."
- "Additional domain database search or citation chasing is needed before tightening the conclusion."

不要声称绝对创新、保证发表或完全空白。

## Codex 优先显示规则

生成文件是审计产物。主要回答必须直接出现在 Codex 对话中。

- 阶段 0：直接渲染 `Strategic Decision Gate`。
- 阶段 1：直接渲染候选选题和默认推荐。
- 阶段 2：直接渲染理论/方法/模型/项目方案。

不要让最终回答依赖用户打开 `.md` 文件才能理解。

## 参考文件加载

只读取相关参考文件：

- `references/user_workflow_and_purpose.md`：项目背景和真实工作流。
- `references/strategic_decision_interview.md`：阶段 0。
- `references/non_coercive_interaction_protocol.md`：交互边界。
- `references/search_protocol.md` 和 `references/source_priority.md`：检索前阅读。
- `references/topic_generation_rubric.md` 和 `references/novelty_rubric.md`：推荐选题前阅读。
- `references/theory_bank.md`、`references/method_taxonomy.md` 和 `references/model_taxonomy.md`：阶段 2。
- `references/evidence_matrix_schema.json`：校验证据矩阵结构时使用。
- `references/final_output_contract.md`：完成面向用户的输出前阅读。
