# LangGraph Learning Plan

This document is a practical guide for learning LangGraph in this project.

## Goal
Build a solid understanding of LangGraph fundamentals and gradually move toward creating a small multi-step agent.

## Phase 1: Understand the basics

### Objectives
- Learn what a graph is in LangGraph.
- Understand nodes, edges, entry points, and the compiled app.
- Review the current example in hello_langgraph.py.

### Topics
- StateGraph
- TypedDict state
- add_messages for chat history
- END and graph compilation

### Example idea
- A single-node assistant that replies to a user message.
- This is your hello_langgraph example.

### Exercises
- Run the existing example.
- Read the generated Mermaid graph in graph.md.
- Change the prompt and observe how the graph behaves.

## Phase 2: Build a simple workflow

### Objectives
- Add a second node to the graph.
- Pass state from one node to another.

### Topics
- Adding nodes with add_node
- Connecting nodes with add_edge
- Returning updated state from nodes

### Example idea
- A two-step flow where the first node decides whether the user wants a joke or a summary, and the second node produces the result.
- This matches the joke or summarize style you already have in mind.

### Exercises
- Create a node that classifies a user request.
- Create a second node that responds based on that classification.

## Phase 3: Add branching logic

### Objectives
- Learn how to route between different paths.

### Topics
- Conditional edges
- Routing based on user input or state values

### Example idea
- A simple router that sends requests to either an answer path or a clarification path.
- Example: if the user asks a question, answer it; if the request is vague, ask a follow-up question.

### Exercises
- Build a small router node.
- Practice sending the flow to different branches.

## Phase 4: Add memory and richer state

### Objectives
- Move beyond simple message history.

### Topics
- Structured state fields
- Maintaining context across steps
- Using state as a conversation memory

### Example idea
- A small FAQ assistant that remembers the user’s topic, preferred tone, or previous question.
- Example: after the first turn, the assistant remembers that the user likes short answers.

### Exercises
- Add fields such as intent, context, or history.
- Make one later step respond differently based on earlier state.

## Phase 5: Use tools

### Objectives
- Connect LangGraph to external functions or APIs.

### Topics
- Tool calling patterns
- Node functions that call tools
- Passing outputs back into the graph state

### Example idea
- A simple assistant that uses a calculator, weather lookup, or a mock API tool.
- Example: if the user asks for a calculation, the graph calls a tool and returns the result.

### Exercises
- Add one small tool function.
- Let a node call that tool and then continue the flow.

## Phase 6: Build a mini project

### Objectives
- Combine everything into a small working agent.

### Suggested project
Create a simple assistant that:
1. Receives a user message.
2. Decides whether it should answer, ask a follow-up, or call a tool.
3. Uses state to keep context across steps.
4. Produces a final answer.

### Simple project idea
- A study buddy assistant that helps with homework:
  - first node: understands the request,
  - second node: asks for clarification if needed,
  - third node: gives a short explanation or uses a tool.

## Suggested study cadence

### Week 1
- Learn the basics and run the starter example.

### Week 2
- Add a second node and branching.

### Week 3
- Add tools and richer state.

### Week 4
- Build a small project end to end.

## Recommended resources
- LangGraph official documentation
- LangChain documentation
- Small example projects and tutorials
- The code in this repository as a hands-on reference

## Next step
Start by editing hello_langgraph.py to add a second node and connect it to the existing chat node.
