import json
from typing import Any, Dict

from openai import OpenAI

from .config import Config


class RiskHeuristicAgent:
    """Desk-rejection heuristics designed to integrate with other agents."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=Config.require_api_key())
        self.model_name = Config.MODEL_NAME

    def analyze(self, manuscript_text: str, journal_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Return a JSON-ready dict describing review outcome."""
        journal_name = journal_profile.get("name", "Unknown Journal")
        strict_rules = journal_profile.get("strict_rules", [])
        print(f"   [Agent 2] Screening against {journal_name}...")

        prompt = f"""
        ROLE: Desk Editor for {journal_name}.
        TASK: Perform an immediate desk review based on these hard constraints:
        {json.dumps(strict_rules)}

        IMPORTANT PARSING NOTES:
        1. Nature-family outlets rarely label the Abstract explicitly—treat the leading bold paragraph as the Abstract.
        2. Data/Code Availability, Ethics, and other compliance statements typically appear near the end of the manuscript.
        3. Use the provided excerpt as complete evidence; do not assume missing context beyond this text.

        MANUSCRIPT EXCERPT:
        {manuscript_text}

        Respond strictly in JSON with the following schema:
        {{
            "decision": "REJECT" | "REVIEW",
            "confidence": float between 0 and 1,
            "fatal_violations": [string],
            "rationale": "string"
        }}
        """

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
