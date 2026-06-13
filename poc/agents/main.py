"""
OPA Policy Violation Fix Pipeline
──────────────────────────────────
Multi-agent LangGraph pipeline:
  START → [Scanner Agent] → [Fix Agent] → END

  Scanner Agent  — runs conftest against manifests and Helm charts, emits violations
  Fix Agent      — calls Claude Sonnet to fix each violating file, generates README.md
"""

import os
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from fix_agent import fix_node
from scanner_agent import scanner_node

BASE_DIR = os.getenv("BASE_DIR", "/app")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", str(Path(BASE_DIR) / "fixed"))


class PipelineState(TypedDict):
    base_dir: str
    output_dir: str
    violations: list[dict]
    fixed_files: list[str]
    readme_content: str
    fix_summary: list[dict]


def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("scan", scanner_node)
    graph.add_node("fix", fix_node)
    graph.add_edge(START, "scan")
    graph.add_edge("scan", "fix")
    graph.add_edge("fix", END)
    return graph.compile()


def main() -> None:
    print("=" * 55)
    print("  OPA POLICY VIOLATION FIX PIPELINE")
    print("=" * 55)
    print(f"  Base dir   : {BASE_DIR}")
    print(f"  Output dir : {OUTPUT_DIR}")

    pipeline = build_pipeline()
    base_dir = BASE_DIR
    output_dir = OUTPUT_DIR

    final_state = pipeline.invoke({
        "base_dir": base_dir,
        "output_dir": output_dir,
        "violations": [],
        "fixed_files": [],
        "readme_content": "",
        "fix_summary": [],
    })

    print("\n" + "=" * 55)
    print("  PIPELINE COMPLETE")
    print("=" * 55)
    print(f"  Violations found : {len(final_state['violations'])}")
    print(f"  Files fixed      : {len(final_state['fixed_files'])}")

    if final_state["fixed_files"]:
        print("\n  Fixed files:")
        for f in final_state["fixed_files"]:
            try:
                rel = Path(f).relative_to(BASE_DIR)
            except ValueError:
                rel = Path(f).name
            print(f"    - {rel}")

    if not final_state["violations"]:
        print("\n  No violations detected — all manifests are compliant.")
    elif not final_state["fixed_files"]:
        print("\n  WARNING: Violations found but no files were fixed.")


if __name__ == "__main__":
    main()
