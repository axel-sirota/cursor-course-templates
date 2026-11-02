#!/usr/bin/env python3
"""Structure checker for a PRD workspace.

Usage:
    python3 scripts/check_prd.py <workspace-dir> [--strict]

Checks (default mode):
  - glossary.md exists
  - every prds/*.md has one H1, every required H2, every required NFR H3
  - every stories/<prd-slug>-*.md has its required sections, a full
    "As a ... I want ... so that ..." line, at least one acceptance
    criterion with Given, When and Then, an Epic and a Goal that exist
    in the PRD, and a row in the PRD User Stories index

Extra checks (--strict):
  - no "TODO:" markers left in PRDs or stories
  - every NFR subsection contains a number
  - every goal has an epic, every epic has a story

Exit code 0 = pass, 1 = failures found, 2 = bad usage.
Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_PRD_H2 = [
    "Problem",
    "Goals",
    "Non-goals",
    "Users",
    "Epics",
    "User Stories",
    "Non-functional Requirements",
    "Edge Cases",
    "Dependencies",
    "Rollout Plan",
    "Success Metrics",
    "Open Questions",
]

REQUIRED_NFR_H3 = [
    "Performance",
    "Security",
    "Privacy",
    "Accessibility",
    "Internationalization",
    "Observability",
]

REQUIRED_STORY_H2 = ["Story", "Acceptance Criteria", "Edge Cases", "INVEST Check"]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
STORY_LINE_RE = re.compile(r"^As an? .+?, I want .+? so that .+", re.MULTILINE)
GOAL_ID_RE = re.compile(r"\bG\d+\b")
EPIC_ROW_RE = re.compile(r"^\|\s*(E\d+)\s*\|(.*)$", re.MULTILINE)
STORY_EPIC_RE = re.compile(r"^\*\*Epic:\*\*\s*(E\d+)\b", re.MULTILINE)
STORY_GOAL_RE = re.compile(r"^\*\*Goal:\*\*\s*(G\d+)\b", re.MULTILINE)
GIVEN_RE = re.compile(r"\*\*Given\*\*")
WHEN_RE = re.compile(r"\*\*When\*\*")
THEN_RE = re.compile(r"\*\*Then\*\*")
TODO_RE = re.compile(r"\bTODO:")
DIGIT_RE = re.compile(r"\d")


@dataclass
class Section:
    level: int
    title: str
    line: int
    body: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(self.body)


def parse_sections(text: str) -> list[Section]:
    """Split markdown into heading sections, ignoring headings inside code fences."""
    sections: list[Section] = [Section(0, "", 0)]
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        match = None if in_fence else HEADING_RE.match(line)
        if match:
            sections.append(Section(len(match.group(1)), match.group(2).strip(), number))
        else:
            sections[-1].body.append(line)
    return sections


def h2_with_children(sections: list[Section], title: str) -> list[Section]:
    """Return the H2 section with this title plus every deeper section under it."""
    out: list[Section] = []
    inside = False
    for section in sections:
        if section.level == 2:
            inside = section.title.lower() == title.lower()
        elif section.level == 1:
            inside = False
        if inside:
            out.append(section)
    return out


def block_text(sections: list[Section]) -> str:
    return "\n".join(s.text for s in sections)


class Checker:
    def __init__(self, root: Path, strict: bool) -> None:
        self.root = root
        self.strict = strict
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def fail(self, path: Path, message: str) -> None:
        self.failures.append(f"FAIL {path.relative_to(self.root)}: {message}")

    def warn(self, path: Path, message: str) -> None:
        self.warnings.append(f"WARN {path.relative_to(self.root)}: {message}")

    def run(self) -> int:
        glossary = self.root / "glossary.md"
        if not glossary.is_file():
            self.failures.append("FAIL glossary.md: missing")

        prds = sorted((self.root / "prds").glob("*.md"))
        if not prds:
            self.failures.append("FAIL prds/: no PRD files found")

        stories = sorted((self.root / "stories").glob("*.md"))
        claimed: set[Path] = set()
        for prd in prds:
            own = [s for s in stories if s.name.startswith(prd.stem + "-")]
            claimed.update(own)
            self.check_prd(prd, own)

        for story in stories:
            if story not in claimed:
                self.fail(story, "no PRD matches this file name prefix")

        for line in self.warnings + self.failures:
            print(line)
        mode = "strict" if self.strict else "default"
        if self.failures:
            print(f"\n{len(self.failures)} failure(s) in {mode} mode.")
            return 1
        print(f"OK: {len(prds)} PRD(s), {len(stories)} story file(s) pass in {mode} mode.")
        return 0

    def check_prd(self, prd: Path, stories: list[Path]) -> None:
        text = prd.read_text(encoding="utf-8")
        sections = parse_sections(text)

        h1 = [s for s in sections if s.level == 1]
        if len(h1) != 1:
            self.fail(prd, f"expected exactly one H1, found {len(h1)}")

        h2_titles = [s.title.lower() for s in sections if s.level == 2]
        for title in REQUIRED_PRD_H2:
            if title.lower() not in h2_titles:
                self.fail(prd, f"missing required heading '## {title}'")

        nfr = h2_with_children(sections, "Non-functional Requirements")
        nfr_h3 = {s.title.lower(): s for s in nfr if s.level == 3}
        for title in REQUIRED_NFR_H3:
            sub = nfr_h3.get(title.lower())
            if sub is None:
                self.fail(prd, f"missing NFR heading '### {title}'")
            elif self.strict and not DIGIT_RE.search(sub.text):
                self.fail(prd, f"NFR '{title}' (line {sub.line}) has no measurable number")

        goals = set(GOAL_ID_RE.findall(block_text(h2_with_children(sections, "Goals"))))
        epics: dict[str, str | None] = {}
        for epic_id, rest in EPIC_ROW_RE.findall(block_text(h2_with_children(sections, "Epics"))):
            goal = GOAL_ID_RE.search(rest)
            epics[epic_id] = goal.group(0) if goal else None
            if goal is None:
                self.fail(prd, f"epic {epic_id} does not name a goal")
            elif goal.group(0) not in goals:
                self.fail(prd, f"epic {epic_id} points at {goal.group(0)}, not defined in Goals")

        if self.strict:
            for number, line in enumerate(text.splitlines(), start=1):
                if TODO_RE.search(line):
                    self.fail(prd, f"line {number} still has a TODO marker")
            linked_goals = {g for g in epics.values() if g}
            for goal in sorted(goals - linked_goals):
                self.fail(prd, f"goal {goal} has no epic")

        index = block_text(h2_with_children(sections, "User Stories"))
        used_epics: set[str] = set()
        for story in stories:
            epic = self.check_story(story, epics)
            if epic:
                used_epics.add(epic)
            if story.name not in index:
                self.fail(prd, f"User Stories index does not link {story.name}")

        if not stories:
            self.warn(prd, "no story files yet (expected in Phase 0, a failure in --strict)")
            if self.strict:
                self.fail(prd, "no story files")
        if self.strict:
            for epic in sorted(set(epics) - used_epics):
                self.fail(prd, f"epic {epic} has no story")

    def check_story(self, story: Path, epics: dict[str, str | None]) -> str | None:
        text = story.read_text(encoding="utf-8")
        sections = parse_sections(text)

        h1 = [s for s in sections if s.level == 1]
        if len(h1) != 1:
            self.fail(story, f"expected exactly one H1, found {len(h1)}")

        h2_titles = [s.title.lower() for s in sections if s.level == 2]
        for title in REQUIRED_STORY_H2:
            if title.lower() not in h2_titles:
                self.fail(story, f"missing required heading '## {title}'")

        if not STORY_LINE_RE.search(text):
            self.fail(story, "no 'As a <user>, I want <capability> so that <outcome>.' line")

        ac = h2_with_children(sections, "Acceptance Criteria")
        criteria = [s for s in ac if s.level == 3] or ac[:1]
        complete = 0
        for criterion in criteria:
            body = criterion.text
            missing = [
                word
                for word, rx in (("Given", GIVEN_RE), ("When", WHEN_RE), ("Then", THEN_RE))
                if not rx.search(body)
            ]
            if missing:
                label = criterion.title or "Acceptance Criteria"
                self.fail(story, f"'{label}' (line {criterion.line}) lacks **{'**, **'.join(missing)}**")
            else:
                complete += 1
        if complete == 0:
            self.fail(story, "no complete Given/When/Then acceptance criterion")

        epic_match = STORY_EPIC_RE.search(text)
        goal_match = STORY_GOAL_RE.search(text)
        if not epic_match:
            self.fail(story, "missing '**Epic:** E<n>' line")
        if not goal_match:
            self.fail(story, "missing '**Goal:** G<n>' line")
        epic = epic_match.group(1) if epic_match else None
        if epic and epic not in epics:
            self.fail(story, f"epic {epic} is not in the PRD Epics table")
        elif epic and goal_match and epics.get(epic) != goal_match.group(1):
            self.fail(
                story,
                f"goal {goal_match.group(1)} does not match epic {epic} goal {epics.get(epic)}",
            )

        if self.strict:
            for number, line in enumerate(text.splitlines(), start=1):
                if TODO_RE.search(line):
                    self.fail(story, f"line {number} still has a TODO marker")
        return epic


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check PRD workspace structure.")
    parser.add_argument("workspace", type=Path, help="folder that holds prds/, stories/, glossary.md")
    parser.add_argument("--strict", action="store_true", help="also fail on TODO and unmeasured NFRs")
    args = parser.parse_args(argv)

    root = args.workspace.resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    return Checker(root, args.strict).run()


if __name__ == "__main__":
    sys.exit(main())
