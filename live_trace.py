"""
live_trace.py — see what happens INSIDE the real run, step by step.
===================================================================

These are "hooks": functions the Runner calls automatically at each moment
of the run. Because they print DURING the run (not afterwards), you see
everything up to the exact moment something goes wrong.

What you see:
    • which AGENT is working, and every HANDOFF from one agent to another
    • every call to the model — and exactly what was SENT to it
    • what the model ASKED FOR (a tool, or the final answer)
    • every tool that ran — its INPUT and its OUTPUT
    • the tokens used by each model call

Use it in research_assistant.py:
    from live_trace import LiveTrace
    result = Runner.run_sync(agent, question, max_turns=10, hooks=LiveTrace())

Options:
    LiveTrace()                          shows each tool's FULL output (the default)
    LiveTrace(show_full_output=False)    shows only the first 300 characters
    LiveTrace(show_system_prompt=True)   also shows the agent's instructions

Note: the short view only shortens what YOU see on screen. The model always
receives the full tool output.
"""

from agents import RunHooks

LINE = "─" * 70


def _short(text, limit=300):
    """Shorten long text so the terminal stays readable."""
    text = str(text).replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + " …"


def _describe(item):
    """Turn one item of the conversation into a short, readable line."""
    if not isinstance(item, dict):
        item = getattr(item, "model_dump", lambda: {"value": item})()
    kind = item.get("type") or item.get("role", "?")

    if kind == "function_call":
        return f"[earlier tool request]  {item.get('name')}  {item.get('arguments')}"
    if kind == "function_call_output":
        return f"[earlier tool result]   {_short(item.get('output'), 150)}"

    content = item.get("content", "")
    if isinstance(content, list):  # messages can hold a list of parts
        content = " ".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return f"[{item.get('role', kind)}]  {_short(content, 150)}"


class LiveTrace(RunHooks):
    def __init__(self, show_system_prompt=False, show_full_output=True):
        self.call = 0
        self.show_system_prompt = show_system_prompt
        self.show_full_output = show_full_output

    # ---- which agent is working, and handoffs between agents ----------------
    async def on_agent_start(self, context, agent):
        print(f"\n🤖  AGENT WORKING: {agent.name}")

    async def on_handoff(self, context, from_agent, to_agent):
        print(f"\n  ↪  HANDOFF:  {from_agent.name}  →  {to_agent.name}")

    # ---- just BEFORE each model call: what are we sending? -------------------
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        self.call += 1
        print(f"\n{LINE}\nMODEL CALL {self.call}  —  sending to the model:")
        if self.show_system_prompt and system_prompt:
            print(f"  [instructions]  {_short(system_prompt, 400)}")
        else:
            print(f"  [instructions]  ({len(system_prompt or '')} characters — "
                  f"use LiveTrace(show_system_prompt=True) to see them)")
        for item in input_items:
            print("  " + _describe(item))

    # ---- just AFTER each model call: what did it decide? ---------------------
    async def on_llm_end(self, context, agent, response):
        for item in response.output:
            kind = getattr(item, "type", "")
            if kind == "function_call":
                print(f"  → the model asks for:  {item.name}  {item.arguments}")
            elif kind == "message":
                text = " ".join(getattr(part, "text", "") for part in item.content)
                print(f"  → the model answers:   {_short(text)}")
        usage = response.usage
        print(f"  (tokens: {usage.input_tokens} in, {usage.output_tokens} out)")

    # ---- each tool: input and output ----------------------------------------
    async def on_tool_start(self, context, agent, tool):
        args = getattr(context, "tool_arguments", "")
        print(f"\n  ⚙ RUNNING TOOL  {tool.name}\n    input : {args}")

    async def on_tool_end(self, context, agent, tool, result):
        if self.show_full_output:
            # the full output, keeping its line breaks, indented under the tool
            print("    output:")
            print("      " + str(result).replace("\n", "\n      "))
        else:
            # only the first 300 characters, to keep the screen readable
            print(f"    output: {_short(result)}")
