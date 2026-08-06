# Phase 4 Guide: Memory and Richer State in LangGraph

This document explains the Phase 4 example implemented in [hello_langgraph.py](hello_langgraph.py).

## Goal of Phase 4

In this phase, the graph moves beyond simple message passing and starts using structured memory.

The graph now remembers key conversation facts across turns, such as:
- user intent
- topic preference
- response tone preference
- turn count

## What changed from Phase 3

Phase 3 focused on routing only:
- route to answer if input looks like a question
- route to clarify if input is vague

Phase 4 adds memory-aware behavior:
- a context node extracts and stores structured fields
- downstream nodes read those fields
- responses change based on earlier turns

## State schema

The state now includes these fields:
- messages: conversation history
- route: selected branch (answer or clarify)
- intent: question or statement
- topic: detected topic (for example LangGraph, Python, LLMs)
- preferred_tone: short, normal, or detailed
- turn_count: number of turns processed so far

This is the core of richer state: the graph stores explicit values, not just raw chat messages.

## Graph flow

Current flow is:

1. start -> context
2. context -> router
3. router -> answer or clarify
4. answer/clarify -> end

You can see the generated Mermaid graph in [graph.md](graph.md).

## Node-by-node explanation

### 1) context node

Purpose:
- inspect the latest user message
- update memory fields in state

What it does:
- detects topic keywords and updates topic
- detects tone preferences like short or detailed
- sets intent to question if message contains ?
- increments turn_count each turn

Why it matters:
- this node centralizes memory extraction
- later nodes can stay simple and consume normalized state

### 2) router node

Purpose:
- decide which branch to follow

What it does:
- uses stored intent and question starters
- sets route to answer or clarify

Why it matters:
- routing is now based on structured memory, not only raw text

### 3) answer node

Purpose:
- produce final answer when input is clear

What it does:
- reads topic, preferred_tone, and turn_count
- injects those into the prompt
- changes response style based on remembered tone

Why it matters:
- later output behavior depends on earlier state

### 4) clarify node

Purpose:
- ask follow-up when request is vague

What it does:
- references remembered topic and tone
- asks for a more specific question

Why it matters:
- clarification is contextual, not generic

## Example multi-turn behavior

When the script runs, it simulates multiple inputs in sequence.

Typical pattern:
1. User says they prefer short answers about LangGraph.
2. State saves preferred_tone=short and topic=LangGraph.
3. Next question gets routed to answer.
4. Answer follows the remembered short style.
5. turn_count increases each turn.

This demonstrates memory across turns using explicit fields.

## How to run

From project root:

```bash
/home/toche/Dev/TestLangGraph/.venv/bin/python hello_langgraph.py
```

What to inspect:
- terminal output for state memory snapshots
- graph structure in [graph.md](graph.md)

## What to learn from this phase

- Use TypedDict fields to model memory clearly.
- Separate concerns: extract context first, route second, respond third.
- Keep branch logic simple by reading normalized state.
- Verify behavior by printing state snapshots during development.

## Suggested next step toward Phase 5

Add a tool-enabled path, for example:
- if user asks for a calculation, route to a calculator tool node
- store tool output in state
- format final answer in a follow-up response node
