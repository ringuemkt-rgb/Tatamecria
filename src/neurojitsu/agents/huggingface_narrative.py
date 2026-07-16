"""Optional local Hugging Face narrative adapter.

It receives only validated report JSON. It never sees raw participant images and its
output is advisory text that must be reviewed by a professional.
"""

from __future__ import annotations

import json
from typing import Any


class HuggingFaceNarrativeModel:
    """Generate a constrained narrative with a locally cached Transformers model."""

    def __init__(self, model_id: str = "Qwen/Qwen3.5-4B") -> None:
        try:
            from transformers import pipeline
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install the agents extra to use a Hugging Face LLM") from exc
        self._generator: Any = pipeline(
            task="text-generation",
            model=model_id,
            device_map="auto",
            trust_remote_code=False,
        )

    def summarize(self, report_payload: dict[str, Any]) -> str:
        prompt = (
            "Você é um redator científico. Resuma somente os dados JSON abaixo. "
            "Não diagnostique, não infira emoções, não invente números e sempre descreva limitações.\n"
            + json.dumps(report_payload, ensure_ascii=False, sort_keys=True)
        )
        result = self._generator(prompt, max_new_tokens=320, do_sample=False)
        return str(result[0]["generated_text"])[len(prompt) :].strip()
