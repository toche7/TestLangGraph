# Phase 2 Explanation

This project builds a small LangGraph application that routes a user message to one of two paths:

- `joke` if the message is not asking for a summary
- `summary` if the message contains the word "summary"

## 1. State Definition

The file defines a state called `State` using `TypedDict`.

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

This means the app keeps a list of messages as its shared state. The `add_messages` helper makes sure new messages are appended properly.

## 2. Loading Environment Variables

The app loads environment variables using `load_dotenv()`.

```python
load_dotenv()
```

This allows the code to read values such as the Groq API key from a `.env` file.

## 3. Calling the LLM

The `call_llm` function is responsible for sending a prompt to the model.

It:

1. Reads the `GROQ_API_KEY` from the environment.
2. Creates a `ChatGroq` model instance.
3. Sends a `HumanMessage` containing the prompt.
4. Returns the model response.

If the API key is missing, the function returns a helpful message instead of crashing.

## 4. Routing Logic

The `route_message` function inspects the latest message.

- If the message contains the word `summary`, it returns `"summary"`.
- Otherwise, it returns `"joke"`.

This routing decision controls which node runs next.

## 5. Graph Nodes

The graph contains three main nodes:

- `router`: decides the next step
- `joke`: generates a short joke
- `summary`: generates a short summary

### Joke Node

The `joke_node` function builds a prompt like:

> Write one short, clean joke about the user's text.

It then calls the model and stores the reply in the message state.

### Summary Node

The `summary_node` function builds a prompt like:

> Summarize this in exactly one sentence.

It also sends the reply back into the message state.

## 6. Building the Graph

The graph is built with `StateGraph(State)`.

The workflow is wired as follows:

- start at `router`
- go to either `joke` or `summary`
- end after the chosen node

This is the basic structure of a LangGraph workflow.

## 7. Running the App

When the script runs, it:

1. generates a graph diagram,
2. saves it to `graph.md`,
3. prints the graph in ASCII form,
4. runs the workflow on example input.

## Summary

This example shows the basic pattern of a LangGraph application:

- define state,
- route input,
- run a node,
- update the state,
- finish the workflow.
