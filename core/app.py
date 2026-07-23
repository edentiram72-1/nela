"""NELA OS command-line entry point."""

from __future__ import annotations

import argparse

from agents.base import AgentResult
from brain.conversation import ConversationTurn
from core.startup import bootstrap


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NELA OS.")
    parser.add_argument(
        "--once",
        help="Process one request and exit.",
    )
    parser.add_argument(
        "--no-dispatch",
        action="store_true",
        help="Create a plan without sending tasks to Agents.",
    )
    args = parser.parse_args()

    runtime = bootstrap()
    runtime.conversation.auto_dispatch = not args.no_dispatch

    if args.once:
        turn = runtime.conversation.handle_text(args.once)
        print(_format_turn(turn))
        return

    _interactive_loop(runtime.conversation)


def _interactive_loop(conversation) -> None:
    print("NELA OS is running. Type a request, or type 'exit' to stop.")
    while True:
        try:
            user_text = input("nela> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            conversation.end_conversation()
            print("NELA stopped.")
            return

        if user_text.lower() in {"exit", "quit", "stop"}:
            conversation.end_conversation()
            print("NELA stopped.")
            return
        if not user_text:
            continue

        try:
            turn = conversation.handle_text(user_text)
        except ValueError as error:
            print(f"NELA needs clarification: {error}")
            continue
        print(_format_turn(turn))


def _format_turn(turn: ConversationTurn) -> str:
    lines = [
        "NELA Brain",
        f"- Intent: {turn.intent.action}",
        f"- Decision: {turn.decision.type.value}",
        f"- Message: {turn.message}",
    ]

    if turn.intent.application:
        lines.append(f"- Application: {turn.intent.application}")
    if turn.intent.resource:
        lines.append(f"- Resource: {turn.intent.resource}")

    if turn.plan:
        lines.append(f"- Plan: {len(turn.plan.tasks)} task(s)")
        for index, task in enumerate(turn.plan.tasks, start=1):
            target = task.target_agent or "unassigned"
            lines.append(f"  {index}. {task.description} -> {target}.{task.action}")

    if turn.dispatched_results:
        lines.append("- Agent Results:")
        for result in turn.dispatched_results:
            lines.append(f"  - {_format_result(result)}")

    return "\n".join(lines)


def _format_result(result: AgentResult) -> str:
    status = "ok" if result.success else "failed"
    return f"{status}: {result.message}"


if __name__ == "__main__":
    main()

