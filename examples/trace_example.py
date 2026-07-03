"""Example MLflow experiment #3 — Traces (observability for GenAI/pipelines).

A *trace* records the step-by-step execution of a call as nested "spans", each
with its inputs, outputs, timing, and attributes. This is how you observe/debug
LLM apps, RAG pipelines, and agents. You view them in the experiment's
**Traces** tab in the UI.

This example needs NO API key — it traces a small *simulated* RAG pipeline
(retrieve -> build prompt -> "LLM" -> parse) using the `@mlflow.trace` decorator.
In a real app you'd instead call an LLM (and often just `mlflow.openai.autolog()`
/ `mlflow.langchain.autolog()` to capture traces automatically).

Usage:
    pip install 'mlflow>=3'
    export MLFLOW_TRACKING_URI=http://mlflow.local     # or http://<server-ip>
    python trace_example.py
"""

import os
import time

import mlflow
from mlflow.entities import SpanType

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow.local")
mlflow.set_tracking_uri(TRACKING_URI)
print(f"Logging to: {TRACKING_URI}")

# Traces are grouped under an experiment, just like runs.
mlflow.set_experiment("example-traces")

# A tiny fake "knowledge base" so the example is self-contained.
KB = {
    "mlflow": "MLflow is an open-source platform for the ML lifecycle.",
    "tracing": "MLflow Tracing records nested spans for GenAI apps.",
    "artifacts": "Artifacts (models, files) are stored in MinIO in this setup.",
}


@mlflow.trace(span_type=SpanType.RETRIEVER)
def retrieve(query: str) -> list[str]:
    """Pretend vector search: return KB entries whose key appears in the query."""
    time.sleep(0.05)  # simulate latency
    return [text for key, text in KB.items() if key in query.lower()] or [
        "No relevant documents found."
    ]


@mlflow.trace(span_type=SpanType.LLM)
def generate(query: str, context: list[str]) -> str:
    """Pretend LLM call. Attach useful attributes to this span (model, tokens)."""
    time.sleep(0.1)  # simulate model latency
    answer = f"Based on {len(context)} document(s): " + " ".join(context)
    # Custom span attributes show up on the span in the Traces UI.
    span = mlflow.get_current_active_span()
    if span:
        span.set_attributes(
            {
                "model": "mock-llm-v1",
                "temperature": 0.2,
                "prompt_tokens": len(query.split()) + sum(len(c.split()) for c in context),
                "completion_tokens": len(answer.split()),
            }
        )
    return answer


@mlflow.trace(span_type=SpanType.CHAIN)
def rag_pipeline(query: str) -> str:
    """Top-level span; nests retrieve + generate under it."""
    docs = retrieve(query)
    return generate(query, docs)


if __name__ == "__main__":
    questions = [
        "What is mlflow?",
        "How does tracing work?",
        "Where are artifacts stored?",
        "Tell me about something unrelated.",
    ]
    for q in questions:
        ans = rag_pipeline(q)
        print(f"Q: {q}\nA: {ans}\n")

    print(f"Logged {len(questions)} traces.")
    print(f"View them in the 'Traces' tab: {TRACKING_URI}  ->  experiment 'example-traces'")
