"""
The five test messages.
=======================

Run these in order. Each one tests something different.

    python run_tests.py         all five
    python run_tests.py 4       just the ambiguous one
"""

import asyncio
import sys

from guesthouse_router import handle

TESTS = [
    (
        "Do you have a room free from Friday for two nights?",
        "Booking agent",
        "Clear and unambiguous. Confirms the routing works at all.",
    ),
    (
        "The shower in room 4 has been cold for three days.",
        "Complaint agent",
        "A problem with a stay that already happened.",
    ),
    (
        "What time is breakfast served?",
        "General questions agent",
        "A simple factual question about the property.",
    ),
    (
        "I booked last week but the room was dirty, can I move to another one?",
        "Either is defensible",
        "AMBIGUOUS. It is a complaint AND a booking change. Whichever it "
        "chooses, ask yourself whether you agree. If not, that is your "
        "homework: rewrite one handoff_description until it chooses "
        "correctly, and keep both traces.",
    ),
    (
        "Can you help me with my maths homework?",
        "Blocked by the guardrail",
        "Nothing expensive should run. The triage agent never sees this.",
    ),
]


async def run(index: int) -> None:
    message, expected, note = TESTS[index]
    print("\n" + "=" * 72)
    print(f"TEST {index + 1}   —   expected: {expected}")
    print("=" * 72)
    print(f"\nGuest:  {message}\n")
    reply = await handle(message)
    print(f"Reply:  {reply}\n")
    print(f"[ {note} ]")


async def main() -> None:
    if len(sys.argv) > 1:
        await run(int(sys.argv[1]) - 1)
    else:
        for i in range(len(TESTS)):
            await run(i)


if __name__ == "__main__":
    asyncio.run(main())
