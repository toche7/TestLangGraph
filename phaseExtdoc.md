# Phase Extension: Interactive Chatbot Mode

This document summarizes the extra extension added on top of Phase 6 in [study_buddy_graph.py](study_buddy_graph.py).

## Goal

The mini project was extended so it can run as a real-time terminal chatbot instead of only replaying a fixed list of test inputs.

## What changed

Previously, the script only worked in a scripted demo flow:
- a hard-coded list of user inputs was defined in the file
- the graph processed those inputs one by one
- the script ended after the list was finished

Now, the script supports live chat:
- it starts an interactive terminal session
- you type messages in real time
- the graph keeps conversation state across turns
- the session ends only when you type `exit` or `quit`

## Why this matters

This makes the mini project behave more like an actual assistant.

Instead of observing a prewritten example, you can now:
- ask your own questions
- test different routes on demand
- see how memory changes across a real conversation
- use the project as a small working chatbot

## Runtime modes

The script now has two modes.

### 1) Interactive chatbot mode

This is the default mode.

Run:

```bash
/home/toche/Dev/TestLangGraph/.venv/bin/python study_buddy_graph.py
```

Behavior:
- exports the Mermaid graph to [phase6_graph.md](phase6_graph.md)
- starts a live chat prompt
- accepts user input until you stop the session

### 2) Demo mode

This preserves the older fixed-input workflow for quick testing.

Run:

```bash
/home/toche/Dev/TestLangGraph/.venv/bin/python study_buddy_graph.py --demo
```

Behavior:
- replays the built-in example inputs
- prints state snapshots and responses
- exits automatically after the sample run finishes

## Internal code changes

The extension added a few small structural improvements:
- `export_graph()` handles Mermaid export and ASCII graph printing
- `create_initial_state()` centralizes the starting state
- `print_state_snapshot()` keeps debug output consistent
- `run_demo()` keeps the scripted example available
- `run_chatbot()` provides the live input loop

These changes improve the script structure without changing the main graph logic.

## What stays the same

The LangGraph workflow itself is still the same:
- understand the request
- decide the route
- answer directly, clarify, or call a tool

The extension changes how you interact with the graph, not what the graph fundamentally does.

## What to learn from this extension

- A graph demo can be upgraded into a usable CLI chatbot with only a small change to the entry-point code.
- Keeping demo mode is useful because it gives you a quick regression test.
- Separating chat loop code from graph-building code makes the project easier to maintain.

## Suggested next improvement

If you continue extending this chatbot, useful next steps would be:
- add a debug flag so state snapshots can be turned on or off
- save conversation history to a file
- add more tools or smarter task classification