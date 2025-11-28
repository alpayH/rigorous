import json
import os
import sys
from pathlib import Path
from typing import Dict, List

from pypdf import PdfReader
from questionary import Choice, checkbox

from .desk_review_agent import RiskHeuristicAgent


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MANUSCRIPT_DIR = DATA_DIR / "manuscripts"
DEFAULT_MANUSCRIPT = MANUSCRIPT_DIR / "test_paper.pdf"
JOURNAL_DIR = DATA_DIR / "journal_profiles"


def load_journal_profile(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


EVIDENCE_SIGNALS = [
    "data availability",
    "code availability",
    "methods",
    "clinical trial",
    "clinical impact",
    "translational impact",
    "ethics statement",
    "conflict of interest",
    "competing interest",
    "author contributions",
]

def parse_pdf(path: Path) -> str:
    print(f"\U0001F4C4 Loading {path}...")
    reader = PdfReader(str(path))
    total_pages = len(reader.pages)

    extracted_content: List[str] = []

    intro_pages = min(3, total_pages)
    for idx in range(intro_pages):
        text = reader.pages[idx].extract_text() or ""
        extracted_content.append(f"--- [Page {idx + 1} (Intro)] ---\n{text}")

    print("   [Parser] Scanning full document for evidence blocks...")
    for idx in range(intro_pages, total_pages):
        text = reader.pages[idx].extract_text() or ""
        text_lower = text.lower()
        if any(signal in text_lower for signal in EVIDENCE_SIGNALS):
            extracted_content.append(f"--- [Page {idx + 1} (Evidence Match)] ---\n{text}")

    print(
        f"   [Parser] Reduced {total_pages} pages to {len(extracted_content)} relevant segments."
    )
    return "\n".join(extracted_content)


def resolve_manuscript() -> Path:
    """Use the default placeholder or fall back to the first PDF found."""
    if DEFAULT_MANUSCRIPT.exists():
        return DEFAULT_MANUSCRIPT

    pdf_candidates = sorted(MANUSCRIPT_DIR.glob("*.pdf"))
    if not pdf_candidates:
        return DEFAULT_MANUSCRIPT  # triggers the helpful error downstream
    return pdf_candidates[0]


def available_profiles() -> List[Choice]:
    choices: List[Choice] = []
    for profile_path in sorted(JOURNAL_DIR.glob("*.json")):
        with profile_path.open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)
        title = f"{metadata.get('name', profile_path.stem)} ({profile_path.name})"
        choices.append(Choice(title=title, value=profile_path))
    return choices


def prompt_for_profiles() -> List[Path]:
    choices = available_profiles()
    if not choices:
        print("❌ No journal profiles found in data/journal_profiles/")
        return []

    if not sys.stdin.isatty():
        return [choices[0].value]

    selection = checkbox(
        "Select one or more journals to evaluate:",
        choices=choices,
        validate=lambda picked: True if picked else "Select at least one journal",
    ).ask()
    return selection or []


def available_manuscripts() -> List[Choice]:
    choices: List[Choice] = []
    for pdf_path in sorted(MANUSCRIPT_DIR.glob("*.pdf")):
        title = f"{pdf_path.name}"
        choices.append(Choice(title=title, value=pdf_path))
    return choices


def prompt_for_manuscripts() -> List[Path]:
    if not MANUSCRIPT_DIR.exists():
        MANUSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    choices = available_manuscripts()
    if not choices:
        # Fall back to default placeholder to trigger error later
        return [DEFAULT_MANUSCRIPT]

    if not sys.stdin.isatty():
        return [choices[0].value]

    selection = checkbox(
        "Select one or more manuscripts to evaluate:",
        choices=choices,
        validate=lambda picked: True if picked else "Select at least one manuscript",
    ).ask()
    return selection or []


if __name__ == "__main__":
    selected_manuscripts = prompt_for_manuscripts()
    selected_profiles = prompt_for_profiles()

    if not selected_manuscripts:
        raise SystemExit("No manuscript selected. Exiting.")

    if not selected_profiles:
        raise SystemExit("No journal selected. Exiting.")

    agent = RiskHeuristicAgent()

    for pdf_path in selected_manuscripts:
        resolved_pdf = pdf_path if pdf_path.exists() else resolve_manuscript()

        if not resolved_pdf.exists():
            print("❌ Please add a PDF to data/manuscripts/ (default name: test_paper.pdf)")
            continue

        print(f"\n=== Parsing manuscript {resolved_pdf.name} ===")
        text = parse_pdf(resolved_pdf)

        for profile_path in selected_profiles:
            profile = load_journal_profile(profile_path)
            print(f"\n=== Evaluating against {profile['name']} ===")
            result = agent.analyze(text, profile)
            print("\n📝 AGENT 2 REPORT:")
            print(json.dumps(result, indent=2))
