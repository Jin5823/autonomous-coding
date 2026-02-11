"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.
"""

import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import (
    AssistantMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from core.client import create_client
from core.progress import print_progress_summary, print_session_header
from core.prompts import copy_spec_to_project, get_coding_prompt, get_initializer_prompt

# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3
RATE_LIMIT_FALLBACK_SLEEP_SECONDS = 30 * 60
RATE_LIMIT_RESET_BUFFER_SECONDS = 60
RATE_LIMIT_RESET_RE = re.compile(
    r"hit your limit.*?resets\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(([^)]+)\)",
    re.IGNORECASE | re.DOTALL,
)


async def run_autonomous_agent(
    project_dir: Path,
    prompts_dir: Path,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Run the autonomous agent loop.

    Args:
        project_dir: Directory for the project
        prompts_dir: Directory containing prompt templates
        max_iterations: Maximum number of iterations (None for unlimited)
    """
    print("\n" + "=" * 70)
    print("  AUTONOMOUS CODING AGENT")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited (will run until completion)")
    print("\nTo stop safely, wait for the current session to complete before pressing Ctrl+C.")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a fresh start or continuation
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    if is_first_run:
        print("Fresh start - will use initializer agent")
        print()
        print("=" * 70)
        print("  NOTE: First session takes 10-20+ minutes!")
        print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
        print("=" * 70)
        print()
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(prompts_dir, project_dir)
    else:
        print("Continuing existing project")
        print_progress_summary(project_dir)

    # Main loop
    iteration = 0

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Print session header
        print_session_header(iteration, is_first_run)

        # Create client (fresh context)
        client = create_client(project_dir)

        # Choose prompt based on session type
        if is_first_run:
            prompt = get_initializer_prompt(prompts_dir)
            is_first_run = False  # Only use initializer once
        else:
            prompt = get_coding_prompt(prompts_dir)

        # Run session with async context manager
        status = "error"
        reset_at = None
        async with client:
            status, response, reset_at = await _run_agent_session(client, prompt, project_dir)

        # Handle status
        if status == "continue":
            print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...")
            print_progress_summary(project_dir)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "rate_limited":
            if reset_at:
                now = datetime.now(reset_at.tzinfo)
                sleep_seconds = max(0, (reset_at - now).total_seconds())
                sleep_seconds += RATE_LIMIT_RESET_BUFFER_SECONDS
                sleep_label = _format_sleep_duration(sleep_seconds)
                reset_label = reset_at.strftime("%Y-%m-%d %H:%M %Z")
                print(f"\nRate limit detected. Sleeping for {sleep_label} (until {reset_label}).")
                await asyncio.sleep(sleep_seconds)
            else:
                sleep_label = _format_sleep_duration(RATE_LIMIT_FALLBACK_SLEEP_SECONDS)
                print(f"\nRate limit detected. Sleeping for {sleep_label} before retrying.")
                await asyncio.sleep(RATE_LIMIT_FALLBACK_SLEEP_SECONDS)

        elif status == "error":
            print("\nSession encountered an error")
            print("Will retry with a fresh session...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Final summary
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print_progress_summary(project_dir)

    # Print instructions for running the generated application
    print("\n" + "-" * 70)
    print("  TO RUN THE GENERATED APPLICATION:")
    print("-" * 70)
    print(f"\n  cd {project_dir.resolve()}")
    print("  ./init.sh           # Run the setup script")
    print("  # Or manually:")
    print("  npm install && npm run dev")
    print("\n  Then open http://localhost:3000 (or check init.sh for the URL)")
    print("-" * 70)

    print("\nDone!")


async def _run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,
) -> tuple[str, str, Optional[datetime]]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path

    Returns:
        (status, response_text, reset_at) where status is:
        - "continue" if agent should continue working
        - "rate_limited" if usage limit was hit
        - "error" if an error occurred
    """
    print("Sending prompt to Claude Agent SDK...\n")

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            # Handle AssistantMessage (text and tool use)
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif isinstance(block, ToolUseBlock):
                        print(f"\n[Tool: {block.name}]", flush=True)
                        input_str = str(block.input)
                        if len(input_str) > 200:
                            print(f"   Input: {input_str[:200]}...", flush=True)
                        else:
                            print(f"   Input: {input_str}", flush=True)

            # Handle UserMessage (tool results)
            elif isinstance(msg, UserMessage):
                if isinstance(msg.content, list):
                    for block in msg.content:
                        if isinstance(block, ToolResultBlock):
                            result_content = block.content or ""
                            is_error = block.is_error or False

                            # Check if command was blocked by security hook
                            if "blocked" in str(result_content).lower():
                                print(f"   [BLOCKED] {result_content}", flush=True)
                            elif is_error:
                                # Show errors (truncated)
                                error_str = str(result_content)[:500]
                                print(f"   [Error] {error_str}", flush=True)
                            else:
                                # Tool succeeded - just show brief confirmation
                                print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        reset_at = _parse_rate_limit_reset(response_text)
        if reset_at:
            return "rate_limited", response_text, reset_at
        return "continue", response_text, None

    except Exception as e:
        print(f"Error during agent session: {e}")
        return "error", str(e), None


def _parse_rate_limit_reset(response_text: str) -> Optional[datetime]:
    match = RATE_LIMIT_RESET_RE.search(response_text)
    if not match:
        return None

    hour_str, minute_str, ampm, tz_name = match.groups()
    hour = int(hour_str)
    minute = int(minute_str or "0")

    if ampm:
        ampm = ampm.lower()
        if hour == 12:
            hour = 0
        if ampm == "pm":
            hour += 12

    try:
        tzinfo = ZoneInfo(tz_name)
    except Exception:
        tzinfo = datetime.now().astimezone().tzinfo

    now = datetime.now(tzinfo)
    reset_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if reset_at <= now:
        reset_at += timedelta(days=1)

    return reset_at


def _format_sleep_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, rem = divmod(seconds, 3600)
    minutes, _ = divmod(rem, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
