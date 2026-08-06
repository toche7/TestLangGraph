# Phase 6 Guide: Mini Project Study Buddy Agent

This document explains the Phase 6 mini project implemented in [study_buddy_graph.py](study_buddy_graph.py).

## Goal of Phase 6

In this phase, the earlier LangGraph concepts are combined into one small agent with a clear purpose.

The graph now acts as a simple study buddy that can:
- understand a learner request
- decide whether to answer directly, ask for clarification, or use a tool
- keep lightweight state across turns
- produce a final response in the user's preferred style

This is the first phase where the graph feels like a small end-to-end assistant rather than an isolated feature demo.

## What changed from Phase 5

Phase 5 focused on adding a tool path to a general-purpose graph:
- one calculator tool was available
- the router detected math requests
- the answer node used the tool result when present

Phase 6 turns that into a mini project with a specific identity:
- the graph is now framed as a study buddy assistant
- the entry node classifies the request in task-oriented terms
- the decision node routes between direct answer, clarification, calculator, and glossary lookup
- the graph uses two simple tools instead of one
- the overall flow is easier to read as an agent workflow

## State schema

The state includes these fields:
- messages: conversation history
- route: selected branch for the current turn
- task_type: detected task such as explain, calculate, or lookup
- topic: detected study topic
- preferred_tone: short, normal, or detailed
- turn_count: number of turns processed so far
- tool_result: transient output from the most recent tool call
- needs_clarification: whether the request is too vague to answer directly

The important addition in Phase 6 is `task_type` and `needs_clarification`.

These fields make the graph easier to reason about:
- `task_type` describes what kind of help the user wants
- `needs_clarification` describes whether the graph should pause and ask a follow-up

## Graph flow

Current flow is:

1. start -> understand
2. understand -> decide
3. decide -> answer, clarify, calculator, or glossary
4. calculator -> answer
5. glossary -> answer
6. answer/clarify -> end

You can see the generated Mermaid graph in [phase6_graph.md](phase6_graph.md).

## Node-by-node explanation

### 1) understand node

Purpose:
- inspect the latest user message
- update structured state for the current turn

What it does:
- detects topic keywords such as LangGraph, node, edge, or Python
- updates tone preference when the user asks for short or detailed answers
- classifies the task as explain, calculate, or lookup
- marks the request for clarification when it is too vague
- increments the turn count

Why it matters:
- it centralizes request interpretation
- downstream nodes can make decisions from normalized state instead of re-parsing raw text

### 2) decide node

Purpose:
- choose the next action for the current turn

What it does:
- routes to `clarify` when the request is vague
- routes to `calculator` when the task is a calculation
- routes to `glossary` when the task is a definition or lookup
- otherwise routes to `answer`

Why it matters:
- it separates understanding from action selection
- it makes the graph read more like an agent policy

### 3) calculator node

Purpose:
- handle arithmetic requests with deterministic logic

What it does:
- extracts the first arithmetic expression from the user message
- calls `calculator_tool`
- stores the result in `tool_result`

Why it matters:
- exact computation stays outside the LLM
- the answer node can explain the result naturally after the tool returns it

### 4) glossary node

Purpose:
- handle lightweight concept definitions

What it does:
- reads the detected topic from state
- calls `glossary_tool`
- stores the returned definition in `tool_result`

Why it matters:
- it demonstrates that Phase 6 can support multiple tools
- it keeps the example practical without making the graph too large

### 5) answer node

Purpose:
- produce the final learner-facing response

What it does:
- reads topic, turn count, tone, and any tool output
- builds a study-buddy prompt around those fields
- asks the model to explain clearly at the requested level of detail
- clears `tool_result` after using it

Why it matters:
- all successful paths converge on one output node
- response formatting stays in one place even when the graph branches earlier

### 6) clarify node

Purpose:
- ask the learner for a more specific question

What it does:
- uses the remembered topic and tone preference
- asks the user to name the exact concept, problem, or example they need help with

Why it matters:
- the graph does not guess when the request is too vague
- clarification stays contextual instead of generic

## The tools in this mini project

### calculator_tool

`calculator_tool` safely evaluates arithmetic expressions using Python's `ast` module.

It supports basic operators while avoiding `eval()`, which keeps the example safer and deterministic.

### glossary_tool

`glossary_tool` is a small dictionary-backed lookup tool.

It returns short definitions for a few supported topics such as:
- LangGraph
- node
- edge
- Python

This tool is intentionally simple. Its purpose is to show how multiple tool paths fit into the same graph.

## Example multi-turn behavior

When the script runs, it simulates several inputs in sequence.

Typical pattern:
1. User says they want short answers for homework.
2. State saves `preferred_tone=short`.
3. User asks what a node in LangGraph is.
4. The graph classifies the request as a lookup and routes to the glossary tool.
5. The glossary output is passed into the answer node.
6. User asks for a calculation.
7. The graph routes to the calculator tool and then back to answer.
8. User sends a vague request such as "help me".
9. The graph routes to clarification instead of guessing.

This is the main Phase 6 idea: one graph can choose among multiple actions while still preserving state across turns.

## How to run

From project root:

```bash
/home/toche/Dev/TestLangGraph/.venv/bin/python study_buddy_graph.py
```

What to inspect:
- terminal output for route, task_type, tone, topic, and clarification flags
- responses after calculator and glossary tool usage
- the generated graph in [phase6_graph.md](phase6_graph.md)

## What to learn from this phase

- A mini project works best when the graph has a clear role, not just generic branching logic.
- Separate request understanding from route selection so the workflow stays readable.
- Multiple tools can fit naturally into the same graph when state carries their output forward.
- Clarification is part of agent behavior, not just a fallback error case.
- One shared answer node can unify direct responses and tool-assisted responses.

## Suggested next step after Phase 6

If you want to keep growing this mini project, the next useful step would be to improve the decision logic so it is less heuristic and more model-guided.

Examples:
- add a lightweight classifier prompt for task selection
- expand the glossary tool into a small knowledge base
- keep a short memory of the learner's current subject or difficulty level