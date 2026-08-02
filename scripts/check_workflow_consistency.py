#!/usr/bin/env python3
"""Validate version, routing and progressive-disclosure invariants."""

from __future__ import annotations

import re
import sys
from pathlib import Path


CURRENT_VERSION = "v2.5.0"
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
    "T1": ("上诉理由链", "结果影响"),
    "T2": ("waiting_external", "不假想对方理由"),
    "T3": ("双轨", "交叉一致性"),
    "T4": ("小额诉讼", "生成普通上诉状"),
    "T5": ("原审未提交原因", "逾期风险"),
    "T6": ("三类可上诉裁定", "扩展为全部裁定救济"),
    "T7": ("遗漏请求", "承诺发回重审"),
    "T8": ("无中国境内住所", "三十日期间"),
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


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
    require(line_count <= 500, f"SKILL.md has {line_count} lines; expected at most 500", errors)

    for version_file, text in (("README.md", readme), ("CHANGELOG.md", changelog), ("usage-and-faq.md", faq)):
        require(CURRENT_VERSION in text, f"{version_file} does not mention {CURRENT_VERSION}", errors)

    require("procedure: first_instance" in skill, "first-instance quick-start route missing", errors)
    require("procedure: second_instance" in skill, "second-instance quick-start route missing", errors)
    require("start_stage" in skill and "end_stage" in skill, "first-instance stage parameters missing", errors)
    require("start_phase" in skill and "end_phase" in skill, "second-instance phase parameters missing", errors)
    require("A0" in skill and "A6" in skill, "second-instance A0-A6 route incomplete", errors)

    references_dir = root / "references"
    missing_refs = sorted(name for name in REQUIRED_REFERENCES if not (references_dir / name).is_file())
    require(not missing_refs, f"missing references: {', '.join(missing_refs)}", errors)
    for name in REQUIRED_REFERENCES:
        require(f"references/{name}" in skill, f"SKILL.md loading table does not consume references/{name}", errors)

    appeal_examples = (references_dir / "appeal-case-examples.md").read_text(encoding="utf-8")
    for scenario, markers in SCENARIO_INVARIANTS.items():
        require(scenario in appeal_examples, f"appeal scenario {scenario} missing", errors)
        for marker in markers:
            require(marker in appeal_examples, f"appeal scenario {scenario} invariant missing: {marker}", errors)

    combined = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.md") if ".git" not in path.parts)
    require("——" not in combined, "prohibited double em dash found in Markdown", errors)
    require("SkillHub 评分优化规则" in (root / "CONTRIBUTING.md").read_text(encoding="utf-8"), "SkillHub quality rule missing", errors)

    if errors:
        return report(errors)
    print(f"PASS: workflow consistency, {CURRENT_VERSION}, SKILL.md {line_count} lines, T1-T8 present")
    return 0


def report(errors: list[str]) -> int:
    print("Workflow consistency validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
