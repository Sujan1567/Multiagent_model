"""
Day 22 — Guesthouse Message Router
===================================

A triage agent that reads a customer message and hands it to one of three
specialists. An input guardrail blocks anything that is not about the
guesthouse at all.

Run it:      python guesthouse_router.py
Ask it:      python guesthouse_router.py "Do you have a room on Friday?"
Test suite:  python run_tests.py

Before running, copy .env.example to .env and put your key in it.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from agents import Runner, InputGuardrailTripwireTriggered
from agents.exceptions import MaxTurnsExceeded

from agents_setup import triage_agent
from guardrail import guesthouse_topic_guardrail
from live_trace import LiveTrace

load_dotenv()


# Attach the guardrail to the agent that receives the message first.
triage_agent.input_guardrails = [guesthouse_topic_guardrail]


async def handle(message: str) -> str:
    """Run one message through the router.

    Returns either the specialist's reply, or a polite refusal if the
    guardrail stopped it.
    """
    try:
        # max_turns=10  → course rule 3: every agent has a limit.
        # hooks=LiveTrace() → prints every step of THIS run as it happens,
        #                     including the moment of each HANDOFF.
        result = await Runner.run(triage_agent, message, max_turns=10,
                                  hooks=LiveTrace())
        print(f"\n✔  Answered by: {result.last_agent.name}")
        return result.final_output

    except InputGuardrailTripwireTriggered:
        # The guardrail fired. Because it runs first, no agent ran at all.
        return (
            "Sorry — I can only help with questions about the guesthouse. "
            "Is there anything about your stay I can help with?"
        )

    except MaxTurnsExceeded:
        return ("The agents stopped after 10 steps without finishing. "
                "Read the trace above to see what they were doing.")

    except Exception as error:
        # Any other error: the live trace above shows every step up to here.
        return f"The run failed: {type(error).__name__}: {error}"


async def main() -> None:
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = "Do you have a room free from Friday for two nights?"

    print("\nGUEST SAYS")
    print(" ", message)
    print("\nRouting...\n")

    reply = await handle(message)

    print("REPLY")
    print(" ", reply)
    print()
    print("-" * 70)
    print("Read the trace above. Which specialist did it choose, and why?")
    print("See developer-tools/03-reading-the-handoff.md")
    print("-" * 70)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("\nNo OPENAI_API_KEY found.")
        print("Copy .env.example to .env and put your key in it.\n")
        sys.exit(1)
    asyncio.run(main())
