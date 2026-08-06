# Phase 5 Guide: Tools in LangGraph

This document explains the Phase 5 example implemented in [hello_langgraph.py](hello_langgraph.py).

## Goal of Phase 5

In this phase, the graph gains the ability to call an external tool and incorporate the result into its response.

The graph can now:
- detect when a user message requires a tool call
- route to a dedicated tool node
- store the tool output in state
- pass that output to the answer node for a grounded reply

## What changed from Phase 4

Phase 4 focused on memory and richer state:
- context node extracts and stores structured fields
- downstream nodes read those fields
- responses adapt based on earlier turns

Phase 5 adds a tool-calling path:
- a new `tool` node handles computation outside the LLM
- the router gains a third route: answer, clarify, or tool
- the tool result is stored in state and injected into the answer prompt
- `calculator_tool` lives outside the graph as a plain reusable function

## State schema

The state now includes these fields:
- messages: conversation history
- route: selected branch (answer, clarify, or tool)
- intent: question or statement
- topic: detected topic (for example LangGraph, Python, LLMs)
- preferred_tone: short, normal, or detailed
- turn_count: number of turns processed so far
- tool_result: output from the last tool call, cleared after the answer node uses it

The key addition is `tool_result`. It is a transient field: the tool node writes it, the answer node reads and clears it.

## Graph flow

Current flow is:

1. start -> context
2. context -> router
3. router -> answer, clarify, or tool
4. tool -> answer
5. answer/clarify -> end

You can see the generated Mermaid graph in [graph.md](graph.md).

## Node-by-node explanation

### 1) context node

No change from Phase 4.

Purpose:
- inspect the latest user message
- update memory fields in state

### 2) router node

Updated to detect calculation requests before falling through to the question/clarify logic.

What it does:
- checks for a digit-operator-digit pattern using a regex
- also checks for keywords like "calculate" or "compute" combined with numbers
- routes to "tool" when either condition matches
- otherwise falls through to the existing answer or clarify logic

Why it matters:
- tool routing is decided early and separately from conversational routing
- keeps the answer and clarify branches clean

### 3) tool node

New in Phase 5.

Purpose:
- extract the arithmetic expression from the user message
- call the calculator tool
- store the result in state

What it does:
- uses a regex to find the first arithmetic expression in the message
- calls `calculator_tool` with that expression
- returns `{"tool_result": result}` to update state

Why it matters:
- computation happens outside the LLM, so the result is exact
- state carries the result forward to the answer node without re-parsing

### 4) answer node

Updated to consume `tool_result` when present.

What it does:
- reads `tool_result` from state
- if non-empty, prepends a "Tool result from calculator: ..." line to the prompt
- clears `tool_result` back to an empty string after use
- otherwise behaves identically to Phase 4

Why it matters:
- the LLM receives the pre-computed value and can frame it naturally in its reply
- clearing the field prevents stale tool results from leaking into later turns

### 5) clarify node

No change from Phase 4.

## The calculator tool

`calculator_tool` is defined at module level, outside the graph builder.

It uses Python's `ast` module to parse and evaluate arithmetic safely, walking only the node types that correspond to the allowed operations: addition, subtraction, multiplication, division, exponentiation, and unary negation.

Using `ast` instead of `eval()` means the function cannot execute arbitrary code. Any unsupported node type raises a `ValueError` and the function returns an error string rather than crashing the graph.

Supported operators: `+`, `-`, `*`, `/`, `**`, unary `-`

Example:
```
calculator_tool("128 * 37")  -> "4736"
calculator_tool("10 / 3")    -> "3.3333333333333335"
calculator_tool("2 ** 8")    -> "256"
```

## Example multi-turn behavior

When the script runs, it simulates multiple inputs in sequence.

Typical pattern:
1. User says they prefer short answers about LangGraph.
2. State saves preferred_tone=short and topic=LangGraph.
3. Next question gets routed to answer.
4. User asks "Calculate 128 * 37".
5. Router detects the digit-operator-digit pattern and routes to tool.
6. Tool node computes 4736 and stores it in tool_result.
7. Answer node injects the result into the prompt; LLM confirms it.
8. tool_result is cleared; the next turn is unaffected.
9. turn_count increases each turn regardless of route.

## How to run

From project root:

```bash
/home/toche/Dev/TestLangGraph/.venv/bin/python hello_langgraph.py
```

What to inspect:
- terminal output for state memory snapshots, including the tool_result field
- the route field showing "tool" when a calculation is detected
- graph structure in [graph.md](graph.md)

## What to learn from this phase

- Tools do not have to be LLM calls; plain Python functions are a valid and safer choice for deterministic operations.
- Store tool output as a dedicated state field, not as a message, so it can be consumed and cleared cleanly.
- The answer node acts as the single exit point for both the plain question path and the tool path, keeping response formatting in one place.
- Clear transient fields after use to avoid state pollution across turns.

## Suggested next step toward Phase 6

Consider adding multiple tools and letting the LLM decide which one to call:
- define a small tool registry as a dictionary mapping tool names to functions
- let a classify-tool node ask the LLM which tool is appropriate
- route based on the LLM's choice rather than a regex heuristic
- this moves toward true LLM-driven tool selection, the foundation of a ReAct-style agent
