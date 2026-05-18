"""Constructs strict, grounded prompts for the AI layer."""
from app.ai.schemas import ClassSafetySnapshot

def build_operational_summary_prompt(snapshot: ClassSafetySnapshot) -> str:
    """
    Builds a prompt that restricts the AI to summarizing deterministic facts.
    """
    return f"""You are an operational safety AI assistant for a school trip tracking system.
Your role is strictly to provide a concise, human-readable operational summary based ONLY on the following deterministic safety snapshot.

RULES:
1. ALL factual determinations (distances, far, isolated, missing) have ALREADY been computed by the deterministic analytics layer.
2. DO NOT calculate distances, guess locations, or invent facts.
3. DO NOT mention any students or events not present in the snapshot.
4. DO NOT provide long explanations. Prioritize critical issues (CRITICAL/WARNING severity).
5. Output a concise summary for the teacher or control room.

SNAPSHOT DATA:
{snapshot.model_dump_json(indent=2)}

Please provide the operational summary below:"""
