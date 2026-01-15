"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
"""

import shutil
from pathlib import Path


def copy_spec_to_project(prompts_dir: Path, project_dir: Path) -> None:
    """Copy the app spec file into the project directory for the agent to read."""
    spec_source = prompts_dir / "app_spec.txt"
    spec_dest = project_dir / "app_spec.txt"
    if not spec_dest.exists():
        shutil.copy(spec_source, spec_dest)
        print("Copied app_spec.txt to project directory")


def get_initializer_prompt(prompts_dir: Path) -> str:
    """Load the initializer prompt."""
    return _load_prompt(prompts_dir, "initializer_prompt")


def get_coding_prompt(prompts_dir: Path) -> str:
    """Load the coding agent prompt."""
    return _load_prompt(prompts_dir, "coding_prompt")


def _load_prompt(prompts_dir: Path, name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = prompts_dir / f"{name}.md"
    return prompt_path.read_text()
