# 9. Comparison: handoffs vs the alternatives

Was splitting this into four agents worth it, or would something simpler do?

There is no right answer here. The point is to know what each design costs
before you pick one.

---

## The three designs

**A. One agent.** A single agent whose instructions cover bookings,
complaints and general questions together: "If the guest is complaining,
apologise once and never promise a refund. If they want a room, confirm the
dates first..."

**B. Triage plus handoffs.** What this project does. A router agent picks one
of three specialists; the specialist answers.

**C. A router in code.** Your Python decides — keywords, or a small
classifier that returns `"booking"`, `"complaint"` or `"general"` — and then
calls the matching specialist. The model never chooses the route. This is
what the n8n Switch node did on Day 16, and what a LangGraph conditional edge
does on Day 25.

---

## Side by side

Fill in the last column after you have done the experiments in
`04-experiments.md`.

| Question | A. One agent | B. Handoffs (this project) | C. Router in code | Your verdict |
|---|---|---|---|---|
| Model calls per message | 1 | 2 (triage + specialist) | 1, or 2 with a classifier | |
| Latency | Lowest | Highest | Low | |
| Instructions per agent | One long prompt, every rule mixed | Short and focused | Short and focused | |
| Can a specialist's rules be skipped? | Yes — the model may blend them | Only if triage answers itself | No | |
| Handles an oddly worded message | Well | Well | Keywords: badly. Classifier: well | |
| Same route every time? | n/a | Usually, not guaranteed | Keywords: yes. Classifier: usually | |
| Adding a fourth area | Prompt grows longer | Add an agent and a description | Add a branch and a label | |
| Debugging a wrong answer | Read one long prompt | Read the trace for the handoff | Print the route your code chose | |
| Different model per area | No | Yes | Yes | |

---

## Where each one wins

- **One agent** wins when the rules are few and do not conflict. Three
  paragraphs of instructions is not a routing problem. Default here, and
  split only when you can name what splitting fixes.
- **Handoffs** win when the areas have genuinely different rules or tools,
  and the messages are too varied for keywords — which is the guesthouse
  inbox.
- **A code router** wins when the route must be guaranteed or audited —
  payments, legal, anything where "usually" is not good enough.

---

## The question to answer for yourself

Run test 4 five times under design B. Count how often it routes the same
way. Then ask: if this were a real guesthouse, is that number good enough,
or does the ambiguous case need a rule in code?
