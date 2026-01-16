"""
Autonomous Coding Agent
=======================

Long-running autonomous coding harness using Claude Agent SDK.
Implements a two-agent pattern (initializer + coding agent) with
automatic rate limit handling and session continuation.

Example Usage:
    python autonomous_coding.py --project-dir my_project
    python autonomous_coding.py --project-dir my_project --max-iterations 5
"""

import argparse
import asyncio
import textwrap
from pathlib import Path

from core.agent import run_autonomous_agent


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent - Long-running coding harness with Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              # Start fresh project
              python autonomous_coding.py --project-dir ./generations/my_project --prompts-dir ./prompts

              # Limit iterations
              python autonomous_coding.py --project-dir ./generations/my_project --prompts-dir ./prompts --max-iterations 5
        """
        ),
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        required=True,
        help="Directory where the project will be generated",
    )
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        required=True,
        help="Directory containing prompt templates (app_spec.txt, initializer_prompt.md, coding_prompt.md)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )
    args = parser.parse_args()

    print("Note: using Claude Code subscription authentication")
    print("(Make sure you're logged in via 'claude' CLI)\n")

    project_dir = args.project_dir.resolve()
    prompts_dir = args.prompts_dir.resolve()

    try:
        asyncio.run(
            run_autonomous_agent(
                project_dir=project_dir,
                prompts_dir=prompts_dir,
                max_iterations=args.max_iterations,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("To resume, run the same command again")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
