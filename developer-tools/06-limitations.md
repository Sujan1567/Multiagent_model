# 6. Limitations of this pattern

## Handoffs are one-way

Once control moves to a specialist, it stays there. The specialist cannot
hand back partway, and two specialists cannot discuss something together.

**If you need that:** the conversational pattern, Day 27.

---

## No shared memory between specialists

Each specialist sees the conversation, but there is no structured state they
all read and write. If the booking agent learns something the complaint agent
needs, there is no clean place to put it.

**If you need that:** LangGraph state, Day 25.

---

## No checkpointing

If the program stops mid-run, the work is gone. There is nothing to resume
from.

**If you need that:** LangGraph checkpointers, Day 26.

---

## The router is a model, and models vary

Your routing is a model decision, so the same message can occasionally route
differently. For most support systems that is acceptable. For anything where
the route must be guaranteed, use a real classifier or a rule.

**If you need that:** a conditional edge in LangGraph, where **your Python**
decides the path rather than the model.

---

## Specialists multiply the ways it can go wrong

Three specialists means three descriptions that must stay distinct. Add a
fourth and the risk of overlap rises. Past a certain number you are better
off with two layers of routing, or fewer, broader specialists.

---

## When this pattern is the right choice

| Good fit | Poor fit |
|---|---|
| Distinct request types with different rules | Steps that are the same every time |
| Each specialist needs different tools | Agents that must collaborate on one answer |
| A cheap model can route, an expensive one can answer | Runs that must survive a crash |
| You want each specialist testable on its own | Guaranteed, non-varying routing |
