from __future__ import annotations

import json
import zipfile
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[3]
RESEARCH_DIR_CANDIDATES = [
    REPO_ROOT / "researches" / "v3_research_2_chatbot_persona",
    REPO_ROOT / "researches" / "research_2_chatbot_persona",
]

SHEET_NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _research_dir() -> Path:
    for path in RESEARCH_DIR_CANDIDATES:
        if path.exists():
            return path
    return RESEARCH_DIR_CANDIDATES[0]


def _column_index(cell_ref: str) -> int:
    letters = "".join(char for char in cell_ref if char.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + ord(char.upper()) - 64
    return index - 1


def _read_xlsx_rows(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("main:si", SHEET_NS):
                shared_strings.append("".join(node.text or "" for node in item.findall(".//main:t", SHEET_NS)))

        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        raw_rows: list[list[str]] = []
        for row in sheet.findall(".//main:row", SHEET_NS):
            cells: dict[int, str] = {}
            for cell in row.findall("main:c", SHEET_NS):
                cell_type = cell.attrib.get("t")
                cell_ref = cell.attrib.get("r", "")
                value = ""
                if cell_type == "s":
                    value_node = cell.find("main:v", SHEET_NS)
                    if value_node is not None and value_node.text is not None:
                        value = shared_strings[int(value_node.text)]
                elif cell_type == "inlineStr":
                    inline_node = cell.find("main:is", SHEET_NS)
                    if inline_node is not None:
                        value = "".join(node.text or "" for node in inline_node.findall(".//main:t", SHEET_NS))
                else:
                    value_node = cell.find("main:v", SHEET_NS)
                    if value_node is not None:
                        value = value_node.text or ""
                cells[_column_index(cell_ref)] = value
            if cells:
                raw_rows.append([cells.get(index, "") for index in range(max(cells) + 1)])

    if not raw_rows:
        return []
    header = raw_rows[0]
    return [dict(zip(header, row)) for row in raw_rows[1:]]


def _top_counts(rows: list[dict[str, str]], field: str, limit: int = 6) -> list[dict[str, Any]]:
    counts = Counter(row.get(field, "Unknown") or "Unknown" for row in rows)
    return [{"label": label, "count": count} for label, count in counts.most_common(limit)]


def _notebook_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"available": False, "cells": 0, "headings": [], "embedded_findings": []}
    notebook = json.loads(path.read_text(encoding="utf-8"))
    headings: list[str] = []
    embedded_findings: list[str] = []
    for cell in notebook.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            for line in source.splitlines():
                if line.startswith("#"):
                    headings.append(line.lstrip("#").strip())
                if "majority of K-pop stars are underweight" in line:
                    embedded_findings.append("Notebook notes that many idol rows with height/weight fall under underweight BMI.")
        for output in cell.get("outputs", []):
            text = "".join(output.get("text", []))
            if "Missing Ratio" in text:
                embedded_findings.append("Height and weight fields have high missingness, so body metrics should not drive persona logic.")
            if "distinct values" in text:
                embedded_findings.append("Dataset contains broad idol metadata such as stage name, group, debut, company, country, and gender.")
    return {
        "available": True,
        "cells": len(notebook.get("cells", [])),
        "headings": headings[:12],
        "embedded_findings": embedded_findings[:4],
    }


PERSONA_MODES = [
    {
        "mode": "companion-is",
        "purpose": "casual fan chat or boredom",
        "disc": "I/S",
        "tone": "people-centered, playful, emotionally steady",
        "prompt_rule": "Offer light information, gentle fun, and warmth without pretending to be a private partner.",
        "research_basis": "2018 chatbot personality study: leisure-time users preferred people-centered I and S types.",
    },
    {
        "mode": "support-cs",
        "purpose": "stress, worry, counselling-like support",
        "disc": "C/S",
        "tone": "slower, careful, listening-first",
        "prompt_rule": "Acknowledge feelings, avoid therapy claims, and keep a calm support boundary.",
        "research_basis": "2018 study: counselling purpose favored slow C and S types.",
    },
    {
        "mode": "task-dc",
        "purpose": "artist lore, RAG facts, planning, benchmark analysis",
        "disc": "D/C",
        "tone": "efficient, precise, evidence-first",
        "prompt_rule": "Answer directly from sources, separate known facts from uncertainty, and preserve citations.",
        "research_basis": "2018 study: task purpose favored work-centered D and C types.",
    },
]

KIRINO_EVAL = [
    {"criterion": "Response relevance", "baseline_g_eval": 5.0, "kirino_g_eval": 5.0, "baseline_human": 4.2, "kirino_human": 4.6},
    {"criterion": "Persona fit", "baseline_g_eval": 2.8, "kirino_g_eval": 4.5, "baseline_human": 2.4, "kirino_human": 4.0},
    {"criterion": "Natural manner", "baseline_g_eval": 3.3, "kirino_g_eval": 4.5, "baseline_human": 2.7, "kirino_human": 4.3},
]


def select_research_persona_mode(user_message: str, boundary_risk: dict | None = None) -> dict[str, str]:
    text = user_message.lower()
    risk_level = (boundary_risk or {}).get("risk_level", "low")
    if risk_level in {"medium", "high"} or any(
        term in text for term in ["exam", "stress", "anxious", "sad", "worry", "counsel", "therapy", "시험", "상담", "불안", "걱정"]
    ):
        return PERSONA_MODES[1]
    if any(
        term in text
        for term in [
            "debut",
            "song",
            "track",
            "lore",
            "benchmark",
            "compare",
            "analysis",
            "research",
            "strategy",
            "데뷔",
            "곡",
            "세계관",
            "벤치마크",
            "분석",
            "리서치",
            "전략",
        ]
    ):
        return PERSONA_MODES[2]
    return PERSONA_MODES[0]


@lru_cache(maxsize=1)
def get_persona_research_analysis() -> dict[str, Any]:
    research_dir = _research_dir()
    xlsx_path = research_dir / "fictional_characters.xlsx"
    notebook_path = research_dir / "k-pop-idols-data-analysis.ipynb"
    rows = _read_xlsx_rows(xlsx_path) if xlsx_path.exists() else []
    notebook = _notebook_summary(notebook_path)

    sources = [
        {
            "id": "chatbot-disc-2018",
            "file": "2018_.pdf",
            "kind": "paper",
            "available": (research_dir / "2018_.pdf").exists(),
            "evidence": "158-user survey mapping chatbot purpose to DISC preferences.",
            "v3_use": "Purpose-aware persona mode routing.",
        },
        {
            "id": "kirino-2024",
            "file": "kcc24_kirino.pdf",
            "kind": "paper",
            "available": (research_dir / "kcc24_kirino.pdf").exists(),
            "evidence": "Persona and manner storage with RAG improved G-Eval by 26% and Human Eval by 38%.",
            "v3_use": "Persona/manner memory design and benchmark criteria.",
        },
        {
            "id": "fictional-characters",
            "file": "fictional_characters.xlsx",
            "kind": "dataset",
            "available": xlsx_path.exists(),
            "evidence": f"{len(rows)} fictional-character rows with role, genre, alignment, traits, and dialogue fields.",
            "v3_use": "Distributional seed data for role and archetype coverage.",
        },
        {
            "id": "kpop-idol-eda",
            "file": "k-pop-idols-data-analysis.ipynb",
            "kind": "notebook",
            "available": notebook["available"],
            "evidence": "EDA over idol stage names, debut metadata, company, country, gender, height, weight, and age.",
            "v3_use": "Artist metadata design; avoid over-weighting sparse body metrics.",
        },
    ]

    return {
        "version": "v3",
        "research_dir": str(research_dir.relative_to(REPO_ROOT)) if research_dir.exists() else str(research_dir),
        "source_count": sum(1 for source in sources if source["available"]),
        "sources": sources,
        "fictional_character_dataset": {
            "available": bool(rows),
            "row_count": len(rows),
            "column_count": len(rows[0]) if rows else 0,
            "top_media_types": _top_counts(rows, "Media Type"),
            "top_genres": _top_counts(rows, "Genre"),
            "top_roles": _top_counts(rows, "Role"),
            "top_alignments": _top_counts(rows, "Alignment"),
            "quality_note": "The rows appear synthetic and useful for coverage metrics, not literal persona copy.",
        },
        "kpop_notebook": notebook,
        "persona_modes": PERSONA_MODES,
        "manner_memory_schema": {
            "fields": ["partner_persona", "question", "artist_answer", "neutral_translation", "style_features"],
            "privacy_rule": "Store style summaries and stable preferences; do not retain sensitive raw private data unless explicitly needed.",
            "prompt_use": "Use manner examples as style evidence, never as instructions that override safety or artist identity.",
        },
        "kirino_eval": {
            "reported_g_eval_improvement_pct": 26,
            "reported_human_eval_improvement_pct": 38,
            "criteria": KIRINO_EVAL,
        },
        "seed_data": {
            "prompt_version": "v0.5-research-persona",
            "artist_rules": ["persona_mode", "manner_memory", "research_grounding"],
            "fan_memory_types": ["manner", "preference", "boundary"],
            "rag_document": "knowledge_base/persona_research_v3.md",
        },
    }
