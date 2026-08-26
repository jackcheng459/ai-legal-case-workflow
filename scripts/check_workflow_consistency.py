#!/usr/bin/env python3
"""Validate version, routing and progressive-disclosure invariants."""

from __future__ import annotations

import re
import sys
from pathlib import Path


CURRENT_VERSION = "v2.6.0"
REQUIRED_REFERENCES = {
    "appeal-workflow.md",
    "appeal-templates.md",
    "appeal-quality-checklist.md",
    "appeal-case-examples.md",
    "stages-1-2-analysis.md",
    "stages-3-5-litigation.md",
    "stages-6-7-delivery.md",
    "templates.md",
    "quality-checklist.md",
    "tooling-and-fallbacks.md",
    "usage-and-faq.md",
}
SCENARIO_INVARIANTS = {
    "T1": {"route": ("A0–A4",), "required": ("结果影响", "闭环"), "forbidden": "只写“原判错误”"},
    "T2": {"route": ("A0–A5",), "required": ("逐项回应",), "forbidden": "未收到上诉状即假想理由"},
    "T3": {"route": ("双轨", "A0–A6"), "required": ("交叉一致性",), "forbidden": "合并成单一上诉轨道"},
    "T4": {"route": ("A0 阻断",), "required": ("一审终审",), "forbidden": "生成普通上诉状"},
    "T5": {"route": ("A3",), "required": ("未提交原因", "逾期风险"), "forbidden": "自动称为有效新证据"},
    "T6": {"route": ("受控 A0–A4",), "required": ("十日期限", "费用"), "forbidden": "扩展为全部裁定救济"},
    "T7": {"route": ("A1–A3",), "required": ("区分不同处理规则",), "forbidden": "直接承诺发回重审"},
    "T8": {"route": ("A0 + 专项闸门",), "required": ("三十日期间", "送达专项核验"), "forbidden": "套用境内十五日或十日结论"},
    "T9": {"route": ("A1–A5",), "required": ("来源角色", "原文定位", "核验状态"), "forbidden": "把诉辩主张写成法院认定"},
    "T10": {"route": ("A1–A5",), "required": ("统计截止时间", "公式", "来源"), "forbidden": "只因数字相同就跨时点复用"},
    "T11": {"route": ("A1–A6",), "required": ("更正传播", "过期版本"), "forbidden": "只修改当前文书"},
    "T12": {"route": ("A4",), "required": ("权威基准", "人工修改"), "forbidden": "退回较早 AI 草稿覆盖律师版本"},
    "T13": {"route": ("A3–A5",), "required": ("原审状态", "同一性", "范围差异", "现行法"), "forbidden": "整组材料贴单一新证据标签"},
    "T14": {"route": ("A0–A6",), "required": ("法源版本", "现行原文", "效力"), "forbidden": "用旧版条文冒充现行法"},
    "T15": {"route": ("A1–A6",), "required": ("全文冲突扫描", "虚假完成"), "forbidden": "有关键冲突仍称全部已核验"},
    "T16": {"route": ("A4/A6",), "required": ("源文件冻结", "文本等价", "视觉验证"), "forbidden": "只验证文件能打开"},
    "T17": {"route": ("A5", "waiting_external"), "required": ("裁判入口证据", "产出类型分离"), "forbidden": "无可核验裁判仍进入 A6"},
    "T18": {"route": ("A5", "hearing_live"), "required": ("必要分析在前", "总结性结论在后"), "forbidden": "先给结论再补分析"},
    "T19": {"route": ("A5",), "required": ("记录来源分层", "单一庭审偏差与待办记录", "律师复核"), "forbidden": "把律师笔记当正式笔录或自动认定立场变化的法律效果"},
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def parse_scenario_rows(text: str) -> dict[str, dict[str, str]]:
    """Parse T1-T19 from the five-column acceptance table."""
    rows: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not re.match(r"^\| T\d+ \|", stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 5:
            continue
        scenario_id, scenario, route, required, forbidden = cells
        rows[scenario_id] = {
            "scenario": scenario,
            "route": route,
            "required": required,
            "forbidden": forbidden,
        }
    return rows


def extract_h2_section(text: str, heading: str) -> str:
    """Return one level-two Markdown section without later sections."""
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    section = text[start + len(marker):]
    next_heading = re.search(r"\n## ", section)
    return section[: next_heading.start()] if next_heading else section


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    skill_path = root / "SKILL.md"
    readme_path = root / "README.md"
    changelog_path = root / "CHANGELOG.md"
    faq_path = root / "references" / "usage-and-faq.md"

    errors: list[str] = []
    for path in (skill_path, readme_path, changelog_path, faq_path):
        require(path.is_file(), f"missing required file: {path.relative_to(root)}", errors)
    if errors:
        return report(errors)

    skill = skill_path.read_text(encoding="utf-8")
    readme = readme_path.read_text(encoding="utf-8")
    changelog = changelog_path.read_text(encoding="utf-8")
    faq = faq_path.read_text(encoding="utf-8")

    frontmatter = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
    require(frontmatter is not None, "SKILL.md frontmatter is missing or malformed", errors)
    if frontmatter:
        fm = frontmatter.group(1)
        require("name: ai-legal-case-workflow" in fm, "frontmatter name mismatch", errors)
        require("description:" in fm, "frontmatter description missing", errors)
        require(not re.search(r"^version:", fm, re.MULTILINE), "version must not appear in frontmatter", errors)

    line_count = len(skill.splitlines())
    char_count = len(skill)
    require(line_count <= 300, f"SKILL.md has {line_count} lines; V2.6.0 budget is at most 300", errors)
    require(char_count <= 10623, f"SKILL.md has {char_count} characters; V2.6.0 budget is at most 10623", errors)

    for version_file, text in (("README.md", readme), ("CHANGELOG.md", changelog), ("usage-and-faq.md", faq)):
        require(CURRENT_VERSION in text, f"{version_file} does not mention {CURRENT_VERSION}", errors)

    require("procedure: first_instance" in skill, "first-instance quick-start route missing", errors)
    require("procedure: second_instance" in skill, "second-instance quick-start route missing", errors)
    require("start_stage" in skill and "end_stage" in skill, "first-instance stage parameters missing", errors)
    require("start_phase" in skill and "end_phase" in skill, "second-instance phase parameters missing", errors)
    require("A0" in skill and "A6" in skill, "second-instance A0-A6 route incomplete", errors)
    for marker in ("fact_id", "source_role", "authoritative_base_path", "correction_cascade"):
        require(marker in skill, f"V2.6.0 hard-gate marker missing from SKILL.md: {marker}", errors)

    references_dir = root / "references"
    missing_refs = sorted(name for name in REQUIRED_REFERENCES if not (references_dir / name).is_file())
    require(not missing_refs, f"missing references: {', '.join(missing_refs)}", errors)
    for name in REQUIRED_REFERENCES:
        require(f"references/{name}" in skill, f"SKILL.md loading table does not consume references/{name}", errors)

    appeal_examples = (references_dir / "appeal-case-examples.md").read_text(encoding="utf-8")
    appeal_workflow = (references_dir / "appeal-workflow.md").read_text(encoding="utf-8")
    appeal_templates = (references_dir / "appeal-templates.md").read_text(encoding="utf-8")
    appeal_quality = (references_dir / "appeal-quality-checklist.md").read_text(encoding="utf-8")
    tooling = (references_dir / "tooling-and-fallbacks.md").read_text(encoding="utf-8")
    for marker, text, source in (
        ("snapshot_cutoff", appeal_templates, "appeal-templates.md"),
        ("submission_status", appeal_templates, "appeal-templates.md"),
        ("expanded_or_more_complete_copy", appeal_workflow, "appeal-workflow.md"),
        ("critical_fact_conflicts", appeal_quality, "appeal-quality-checklist.md"),
        ("规范化文本", tooling, "tooling-and-fallbacks.md"),
        ("hearing_context: live", appeal_workflow, "appeal-workflow.md"),
        ("record_status: lawyer_notes", appeal_workflow, "appeal-workflow.md"),
        ("second_instance_decision_path", appeal_workflow, "appeal-workflow.md"),
        ("decision_event", appeal_workflow, "appeal-workflow.md"),
        ("artifact_type", appeal_workflow, "appeal-workflow.md"),
        ("庭审偏差与待办记录", appeal_workflow, "appeal-workflow.md"),
        ("材料与限制 → 必要分析 → 总结性结论", appeal_templates, "appeal-templates.md"),
        ("没有可核验二审裁判却进入 A6", appeal_quality, "appeal-quality-checklist.md"),
    ):
        require(marker in text, f"V2.6.0 regression marker missing from {source}: {marker}", errors)
    fact_table_header = "| issue_id | fact_id | source_role | 命题或原文 | 材料与页码 | event_time | fact_status | 反向材料 | 下游文书 |"
    require(
        fact_table_header in appeal_templates,
        "appeal-templates.md A1 fact table must use fact_id in its fixed header",
        errors,
    )
    require(
        "assertion_id" not in appeal_templates,
        "appeal-templates.md still contains deprecated assertion_id",
        errors,
    )
    hearing_delta_header = "| 事件或变化 | 现场来源 | 与庭前底稿的差异 | 对当前争点的影响 | 是否需律师确认 | 庭后动作 |"
    require(
        hearing_delta_header in appeal_templates,
        "appeal-templates.md must use one lightweight hearing delta and action table",
        errors,
    )
    scenario_rows = parse_scenario_rows(appeal_examples)
    for scenario, expected in SCENARIO_INVARIANTS.items():
        require(scenario in scenario_rows, f"appeal scenario {scenario} missing from acceptance table", errors)
        if scenario not in scenario_rows:
            continue
        row = scenario_rows[scenario]
        for column in ("route", "required"):
            for marker in expected[column]:
                require(
                    marker in row[column],
                    f"appeal scenario {scenario} {column} invariant missing: {marker}",
                    errors,
                )
        require(
            row["forbidden"] == expected["forbidden"],
            f"appeal scenario {scenario} forbidden behavior mismatch: {row['forbidden']}",
            errors,
        )

    failure_example = extract_h2_section(appeal_examples, "示例六：工具失败后的降级与恢复")
    require(bool(failure_example), "second-instance failure receipt example missing", errors)
    for marker in ("attempts:", "degraded_method:", "resume_from:", "completion_blocker:"):
        require(marker in failure_example, f"second-instance failure receipt missing: {marker}", errors)

    combined = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.md") if ".git" not in path.parts)
    require("——" not in combined, "prohibited double em dash found in Markdown", errors)
    require("SkillHub 评分优化规则" in (root / "CONTRIBUTING.md").read_text(encoding="utf-8"), "SkillHub quality rule missing", errors)

    if errors:
        return report(errors)
    print(
        f"PASS: workflow consistency, {CURRENT_VERSION}, "
        f"SKILL.md {line_count} lines/{char_count} characters, T1-T19 present"
    )
    return 0


def report(errors: list[str]) -> int:
    print("Workflow consistency validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
