# Cheatsheet: LangGraph

## Minimal supervisor graph
```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict):
    input: str
    route: str
    output: str
    trace: list

def supervisor(state: State) -> dict:
    decision = router_llm.invoke(state["input"])   # structured output!
    return {"route": decision.route}

def research(state: State) -> dict:
    return {"output": rag_answer(state["input"])}

def writer(state: State) -> dict:
    return {"output": compose(state["input"])}

g = StateGraph(State)
g.add_node("supervisor", supervisor)
g.add_node("research", research)
g.add_node("writer", writer)
g.set_entry_point("supervisor")
g.add_conditional_edges("supervisor",
    lambda s: s["route"],                 # reads state, returns node name
    {"research": "research", "writer": "writer"})
g.add_edge("research", END)
g.add_edge("writer", END)
app = g.compile()
final = app.invoke({"input": "...", "trace": []})
```

## Key concepts
| Concept | One-liner |
| --- | --- |
| State | TypedDict passed to every node; nodes return partial updates |
| Node | function or agent: `state -> dict` (merged into state) |
| Conditional edge | function of state → next node name |
| END | terminal sentinel |
| Checkpointer | persist state per step → resume, replay, human-in-the-loop |
| Reducer | how updates merge (e.g. `Annotated[list, add]` appends) |

## Append-only trace pattern (used in AgentForge)
```python
from typing import Annotated
from operator import add

class State(TypedDict):
    trace: Annotated[list, add]     # every node's trace entries append

def node(state):
    return {"trace": [{"agent": "research", "latency_ms": 412}]}
```

## Loop with a cap
```python
def should_continue(state):
    if state["iterations"] >= 3 or state["done"]:
        return "finish"
    return "revise"
g.add_conditional_edges("critique", should_continue,
                        {"revise": "draft", "finish": END})
```

## Chains vs graphs decision
- Fixed steps → LCEL chain.
- Runtime routing / cycles / multi-agent / resumability → LangGraph.
- Supervisor routing should be a **structured output** (enum of routes), never free text parsing.

## Gotchas
- Nodes must return dicts of *updates*, not mutate state in place.
- Un-capped cycles = infinite loops = infinite bills.
- Keep state minimal: it's serialized on every checkpoint.
