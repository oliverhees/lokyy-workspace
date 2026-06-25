"""Self-improvement / fact extraction (M2.3).

After a chat turn, ask the model to distil durable facts about the user from the
exchange. Output is JSON, parsed and validated (Pydantic) — never trusted raw.
Extracted facts are stored as memories (kind="fact") so future chats recall concise
knowledge instead of raw messages. Best-effort: any failure yields no facts and must
never break the chat.
"""
from __future__ import annotations

import json
import re

from pydantic import BaseModel, ValidationError

from app.core import llm

_MAX_FACTS = 5
_MAX_FACT_LEN = 200

_SYSTEM = (
    "Du extrahierst dauerhafte, wiederverwendbare Fakten ÜBER DEN NUTZER aus einem "
    "Gesprächsausschnitt — z. B. Name, Beruf/Tätigkeit, Vorlieben, Tools, Kontext, Ziele. "
    "Strikte Regeln: NUR explizit vom Nutzer Gesagtes, KEINE Vermutungen, keine flüchtigen "
    "Tagesdinge, nichts über den Assistenten. Wenn nichts Dauerhaftes vorkommt, gib eine leere "
    "Liste zurück. Antworte AUSSCHLIESSLICH als JSON: {\"facts\": [\"…\", …]} (kurze Aussagesätze)."
)


class ExtractedFacts(BaseModel):
    facts: list[str] = []


def _parse(text: str) -> list[str]:
    """Tolerantly pull the JSON object out of the model output and validate it."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return []
    try:
        data = ExtractedFacts.model_validate(json.loads(match.group(0)))
    except (json.JSONDecodeError, ValidationError):
        return []
    facts: list[str] = []
    for f in data.facts:
        f = f.strip()
        if f:
            facts.append(f[:_MAX_FACT_LEN])
        if len(facts) >= _MAX_FACTS:
            break
    return facts


async def extract_facts(user_message: str, assistant_message: str, cfg: llm.LLMConfig,
                        **llm_overrides) -> list[str]:
    """Return durable user facts from one turn. Empty list on anything unexpected."""
    convo = f"Nutzer: {user_message.strip()}\n\nAssistent: {assistant_message.strip()}"
    messages = [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": convo}]
    try:
        out = await llm.chat(messages, cfg, **llm_overrides)
    except Exception:
        return []
    return _parse(out)
