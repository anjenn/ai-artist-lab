from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


DEFAULT_RESEARCH_FILES = [
    "v2_research1_google_scholar_general.md",
    "v3_persona_analysis.md",
    "v4_overall_technical_researches.md",
]


def _extract_summary(path: Path, max_lines: int = 8) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    headings = [line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")]
    evidence_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("-", "*")) and len(line.strip()) > 3
    ][:max_lines]
    return {
        "file": path.name,
        "title": headings[0] if headings else path.stem.replace("_", " "),
        "headings": headings[:8],
        "evidence_lines": evidence_lines,
    }


def build_research_index(
    *,
    research_dir: str | Path = "../researches",
    files: list[str] | None = None,
) -> dict[str, Any]:
    root = Path(research_dir)
    summaries = []
    missing = []
    for filename in files or DEFAULT_RESEARCH_FILES:
        path = root / filename
        if path.exists():
            summaries.append(_extract_summary(path))
        else:
            missing.append(filename)
    return {
        "version": "research_ingestion_v1",
        "research_dir": str(root),
        "files_indexed": len(summaries),
        "missing_files": missing,
        "summaries": summaries,
    }


def render_research_index(index: dict[str, Any]) -> str:
    lines = [
        "# Research Index",
        "",
        "Generated from local research notes. Use this as a compact routing artifact; source files remain authoritative.",
        "",
        f"- Version: `{index['version']}`",
        f"- Files indexed: {index['files_indexed']}",
    ]
    if index["missing_files"]:
        lines.append(f"- Missing files: {', '.join(index['missing_files'])}")
    for summary in index["summaries"]:
        lines.extend(
            [
                "",
                f"## {summary['title']}",
                "",
                f"Source: `{summary['file']}`",
                "",
            ]
        )
        if summary["headings"]:
            lines.append("Headings: " + "; ".join(summary["headings"][:6]))
            lines.append("")
        if summary["evidence_lines"]:
            lines.append("Evidence lines:")
            lines.extend(summary["evidence_lines"])
    return "\n".join(lines).strip() + "\n"


def regenerate_research_index(
    *,
    research_dir: str | Path = "../researches",
    output_path: str | Path = "../knowledge_base/research_index.md",
    files: list[str] | None = None,
) -> dict[str, Any]:
    index = build_research_index(research_dir=research_dir, files=files)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_research_index(index), encoding="utf-8")
    return index | {"output_path": str(output)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate compact research summaries for KB ingestion.")
    parser.add_argument("--research-dir", default="../researches")
    parser.add_argument("--output-path", default="../knowledge_base/research_index.md")
    parser.add_argument("--file", dest="files", action="append", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    index = build_research_index(research_dir=args.research_dir, files=args.files)
    rendered = render_research_index(index)
    if args.dry_run:
        sys.stdout.buffer.write(rendered.encode("utf-8"))
    else:
        output = Path(args.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print({"output_path": str(output), "files_indexed": index["files_indexed"], "missing_files": index["missing_files"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
