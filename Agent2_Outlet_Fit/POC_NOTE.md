# Proof of concept for the outlet fit agent

## Purpose

The main goal is to prototype an automated desk editor that evaluates whether a manuscript is a good fit for a specific outlet (for example, Nature Medicine vs. NeurIPS) before full peer review. The motivation is that, in real workflows, many technically solid papers are desk rejected not for lack of quality, but because they miss formal policies (data availability, ethics, impact statements) or do not fully match a journal’s scope, which wastes time for authors, reviewers, and editors.

In this proof of concept, the agent takes a PDF and a structured journal profile, checks only hard constraints such as scope, format and mandatory statements, and produces a clear REVIEW vs. REJECT decision with an explanation, similar to what a human desk editor would write. The broader idea is to show that outlet-specific rules can be represented and enforced by an LLM-based tool, as a first step toward a larger multi-agent pipeline that jointly models outlet policies, manuscript content and submission strategy.

## How to Run

```bash
cd Agent2_Outlet_Fit
python3 -m venv .venv && source .venv/bin/activate  # first run only
pip install -r requirements.txt
python -m src.agent2_outlet_fit.main
```

- Drop PDFs into `data/manuscripts/`
- Keep journal policies in `data/journal_profiles/` (Nature Medicine + NeurIPS JSON already provided).
- Store `OPENAI_API_KEY` in either `.env` at the repo root or inside `Agent2_Outlet_Fit/`.
