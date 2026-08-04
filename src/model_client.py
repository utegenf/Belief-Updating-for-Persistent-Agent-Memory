"""Model client — the single place the experiments talk to an LLM.

Provider-neutral interface (``complete_text`` / ``complete_structured``) so the experiment
code never contains provider plumbing. The reference implementation targets a hosted LLM API
via boto3's Bedrock ``converse`` interface, using the standard default credential chain
(environment variables / instance role) — no profile or account identifiers are embedded.
To run against a different provider, reimplement these two functions.

Configuration (environment variables):
  AGENT_MODEL   model id / identifier for the agent (e.g. a Claude Sonnet model)
  JUDGE_MODEL   model id for the cross-family evaluation judge
  API_REGION    region for the hosted API (default: us-east-1)
"""
import ast
import json
import re
from typing import Optional

import boto3

# --- configuration (from environment; no credentials or identifiers in source) ------------
import os

AGENT_MODEL = os.environ.get("AGENT_MODEL")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL")
API_REGION = os.environ.get("API_REGION", "us-east-1")
TEMPERATURE = 0.0  # greedy decoding for reproducible measurement

# Default credential chain (env vars / role) — no profile pinned.
_client = boto3.client("bedrock-runtime", region_name=API_REGION)


def _inference_config(seed: Optional[int]) -> dict:
    # The hosted converse API takes temperature; there is no cross-model seed parameter, so
    # seed is used only for run labelling upstream. Determinism comes from temperature 0.
    return {"temperature": TEMPERATURE}


def complete_text(system_prompt: str, user_prompt: str, model_id: str = None,
                  seed: Optional[int] = None) -> str:
    """Single-turn text completion."""
    resp = _client.converse(
        modelId=model_id or AGENT_MODEL,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_prompt}]}],
        inferenceConfig=_inference_config(seed),
    )
    return resp["output"]["message"]["content"][0]["text"]


def complete_structured(system_prompt: str, user_prompt: str, pydantic_model,
                        model_id: str = None, seed: Optional[int] = None):
    """Structured completion: force the model to return an instance of ``pydantic_model``."""
    schema = pydantic_model.model_json_schema()
    tool_config = {
        "tools": [{
            "toolSpec": {
                "name": "return_structured_data",
                "description": "Return the strictly formatted result.",
                "inputSchema": {"json": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                    # propagate $defs so nested models resolve their $ref
                    **({"$defs": schema["$defs"]} if "$defs" in schema else {}),
                }},
            }
        }],
        "toolChoice": {"tool": {"name": "return_structured_data"}},
    }
    resp = _client.converse(
        modelId=model_id or AGENT_MODEL,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_prompt}]}],
        toolConfig=tool_config,
        inferenceConfig=_inference_config(seed),
    )
    for block in resp["output"]["message"]["content"]:
        if "toolUse" in block:
            data = _coerce_tool_input(block["toolUse"]["input"], pydantic_model)
            return pydantic_model(**data)
    raise ValueError(f"{model_id or AGENT_MODEL} returned no structured output")


def _coerce_tool_input(data: dict, pydantic_model) -> dict:
    """Robustness net for models that stringify list fields or echo the schema envelope."""
    coerced = dict(data)
    expected = set(pydantic_model.model_fields)
    if not (expected & coerced.keys()) and isinstance(coerced.get("properties"), dict):
        coerced = dict(coerced["properties"])
    for field_name, field_info in pydantic_model.model_fields.items():
        value = coerced.get(field_name)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith(("[", "{")):
                try:
                    coerced[field_name] = json.loads(stripped)
                except (ValueError, TypeError):
                    try:
                        coerced[field_name] = ast.literal_eval(stripped)
                    except (ValueError, SyntaxError):
                        if stripped.startswith("[") and str(field_info.annotation).startswith(("typing.List", "list")):
                            inner = stripped[1:-1].strip()
                            items = re.split(r"'\s*,\s*'", inner)
                            coerced[field_name] = [it.strip().strip("'\"") for it in items if it.strip()]
    return coerced
