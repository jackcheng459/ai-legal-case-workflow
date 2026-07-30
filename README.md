# AI Legal Case Workflow

面向中国民事诉讼实务的 AI 辅助办案 Skill。

本技能将民事案件办理拆分为七个阶段，提供输入规则、执行步骤、输出模板和质量检查点。它同时支持原告方与被告方视角，适用于合同纠纷、侵权纠纷等民事一审、二审案件。

> 本项目用于辅助律师整理材料、形成分析候选和起草文书。它不能替代律师判断、法源核验、证据原件核对和最终定稿。

## 核心能力

| 阶段 | 主要任务 | 典型输出 |
|---|---|---|
| 1. 诉前分析 | 材料通读、时间线、争议焦点、时效与管辖分析 | 案件概要报告 |
| 2. 主体核查 | 工商、涉诉、信用、财产线索与保全评估 | 主体核查与保全报告 |
| 3. 起诉准备 | 诉讼请求、起诉状、证据目录、保全申请 | 起诉材料包 |
| 4. 反诉分析 | 请求权基础、举证满足度、不利证据与应对 | 反诉分析报告 |
| 5. 应诉准备 | 答辩、质证、法源研究、庭审发问与调解预研 | 应诉材料包 |
| 6. 庭审工作 | 庭前准备、庭审记录、庭后意见与调解更新 | 庭审文书包 |
| 7. 格式交付 | Markdown、Word、HTML、PDF 转换与归档 | 最终交付文件 |

## 仓库结构

```text
ai-legal-case-workflow/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── references/
    ├── templates.md
    └── quality-checklist.md
```

- `SKILL.md`：工作流入口、阶段规则和工具说明。
- `references/templates.md`：七个阶段的输出模板。
- `references/quality-checklist.md`：分阶段质量检查清单。

## 安装

### 方式一：克隆仓库

```bash
git clone https://github.com/jackcheng459/ai-legal-case-workflow.git
```

将 `SKILL.md` 与 `references/` 一起复制到目标 AI 工具的技能目录。两者必须保持相对路径不变。

常见目录示例：

```text
~/.codex/skills/ai-legal-case-workflow/
~/.claude/skills/ai-legal-case-workflow/
```

不同产品和版本的技能目录可能变化，请以对应产品的当前说明为准。

### 方式二：下载 ZIP

在 GitHub 仓库页面选择 `Code`，下载 ZIP 后解压到目标技能目录。

## 快速使用

向支持 Skill 的 AI 工具提供案件阶段、代理立场和材料路径。例如：

```text
请使用 ai-legal-case-workflow 处理一宗设备买卖合同纠纷。

role: defendant
case_stage: trial
materials_path: /path/to/redacted-case
start_stage: 1
end_stage: 5
output_formats: ["md"]
```

建议先用脱敏、低风险的小样本试跑一个阶段，确认输出结构和工具权限后再扩大范围。

## 输入要求

必需参数：

- `case_type`：案件类型。
- `case_stage`：当前阶段。
- `materials_path`：卷宗材料目录的绝对路径。

常用可选参数：

- `role`：`plaintiff` 或 `defendant`。
- `start_stage`、`end_stage`：限定执行阶段。
- `output_formats`：选择 `md`、`html`、`docx` 或 `pdf`。
- `parallel_enabled`：是否允许平台使用子代理协作。
- `enable_mcp_tools`：指定可用的法律或企业信息工具。

完整定义见 [SKILL.md](SKILL.md)。

## 工具与兼容性

本仓库是纯 Markdown Skill，不包含可执行脚本，也不会自动安装依赖。

工作流中出现的北大法宝、元典、企查查、PDF 处理、Word 生成和子代理工具，均依赖使用者所在平台的实际能力。工具名称和调用方式可能需要适配：

- 法条、案例和司法解释应通过当前可用的权威来源核验。
- 企业查询应先确认完整企业登记名称或统一社会信用代码。
- PDF、Word 和多代理工具不可用时，应明确降级状态，不得假装已执行。
- 任何自动生成的法律结论和正式文书都应由律师复核。

## 数据安全

使用真实案件材料前，应同时判断材料敏感度、链路可信度、任务必要性和授权范围。

| 等级 | 示例 | 使用边界 |
|---|---|---|
| 绿色 | 公开法律资料、虚构案例 | 可用于公开研究和普通测试 |
| 黄色 | 脱敏案件结构、内部工作流 | 限定范围，使用可审计链路 |
| 红色 | 合同原文、完整案情、真实身份组合、未公开策略 | 仅在任务必要、授权清楚、链路可信且有人工最终复核时处理 |
| 红线 | 涉密材料、合同明禁数据、账号密钥及其他刚性禁止材料 | 不得进入普通 AI 链路或公开仓库 |

不要在公开 Issue、Discussion、Pull Request 或示例文件中提交真实卷宗、身份证号、联系方式、银行账户、未公开策略或访问凭证。详见 [SECURITY.md](SECURITY.md)。

## 质量控制

每个阶段完成后至少检查：

- 材料是否完整读取，无法读取的文件是否明确记录。
- 事实是否能追溯到具体证据、页码或原始载体。
- 金额、日期、主体名称和证据编号是否前后一致。
- 法条和案例是否核实效力状态、案号、法院与裁判日期。
- 输出是否区分材料事实、当事人陈述、分析推论和策略建议。

完整清单见 [references/quality-checklist.md](references/quality-checklist.md)。

## 已知限制

- 不同 AI 平台的 Skill、MCP 和子代理接口并不统一，需要按实际环境适配。
- 本技能不直接访问付费法律数据库，也不附带任何数据库账号或 API 凭证。
- 诉讼费、司法政策、法院提交要求和工具接口可能变化，使用时应重新核验。
- 当前 `SKILL.md` 内容较长，后续版本将继续拆分执行规则与平台适配说明。

## 参与完善

欢迎提交模板修订、流程校正、平台兼容说明和脱敏示例。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 版本记录

版本信息统一记录在 [CHANGELOG.md](CHANGELOG.md)，不写入 `SKILL.md` frontmatter。

## 许可证状态

本仓库当前未声明开源许可证。公开可见不等于自动授权复制、修改、再发布或商业使用。需要复用或分发时，请先取得仓库权利人的明确许可。
