# Phase 3 Guide: Branching Logic in LangGraph

This document explains the Phase 3 example implemented in [hello_langgraph.py](hello_langgraph.py).

## Goal of Phase 3

Phase 3 focuses on routing. Instead of a single linear path, the graph decides which path to take based on user input.

In this example, the assistant chooses between:
- an answer path when the input looks like a question
- a clarification path when the input is vague

## What is new in this phase

Compared to earlier phases, this example introduces:
- a router node
- conditional edges
- multiple terminal branches

These are key LangGraph concepts for building non-linear workflows.

## State used in this phase

The graph state has two fields:
- messages: chat history
- route: selected branch label

`messages` is maintained with `add_messages`, and `route` is written by the router node.

## Graph structure

The flow is:

1. start -> router
2. router -> answer or clarify (conditional)
3. answer/clarify -> end

You can inspect the generated diagram in [graph.md](graph.md).

## Node-by-node explanation

### 1) router node

Purpose:
- classify the latest user message
- choose a route label

How it works:
- reads the latest input text
- checks if it contains `?` or starts with common question words
- returns `route = "answer"` or `route = "clarify"`

This is where branching decisions are made.

### 2) answer node

Purpose:
- generate a direct response for clear questions

How it works:
- builds a prompt from the latest user message
- calls the model via `call_llm`
- returns an assistant message

### 3) clarify node

Purpose:
- request more detail when the input is too vague

How it works:
- creates a follow-up question
- nudges the user to ask something specific

## Conditional edges in practice

The graph uses `add_conditional_edges` with:
- source node: `router`
- route function: `pick_route`
- mapping:
  - `answer` -> `answer`
  - `clarify` -> `clarify`

This pattern scales well when you add more branches later.

## Example behavior

The script includes two sample inputs:

1. `What is LangGraph in one sentence?`
Result: routed to `answer`.

2. `LangGraph`
Result: routed to `clarify`.

Running both examples helps verify that branching is working.

## How to run

From project root:

```bash
/home/toche/Dev/TestLangGraph/.venv/bin/python hello_langgraph.py
```

What to check:
- ASCII graph in terminal
- Mermaid graph in [graph.md](graph.md)
- different outputs for question vs vague input

## What to learn from this phase

- Use a router node to separate decision logic from response logic.
- Store the branch decision in state for transparent routing.
- Use conditional edges to make graph execution non-linear.
- Keep each branch node focused on one responsibility.

## Suggested next step toward Phase 4

Add richer memory fields to the state, such as:
- intent
- topic
- preferred tone
- turn count

Then make later responses depend on those remembered values across turns.
