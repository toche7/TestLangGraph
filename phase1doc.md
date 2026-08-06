# Phase 1 Documentation

## Overview
This script builds a very small LangGraph application with one node named `chatbot`. The app accepts a message from the user, sends that message to a Groq-powered LLM, and returns the model's response as a new message.

## What the code does

### 1. Imports and setup
The script imports:
- `os` for reading environment variables
- `Annotated` and `TypedDict` for defining the graph state
- `load_dotenv` to load values from a `.env` file
- `HumanMessage` for representing chat messages
- `ChatGroq` for connecting to the Groq model
- `StateGraph` and `END` from LangGraph to build the workflow
- `add_messages` to help manage message history in the state

It also calls `load_dotenv()` so environment variables from `.env` are available during execution.

### 2. State definition
A `State` typed dictionary is created with one field:
- `messages`: a list of chat messages

The `Annotated` wrapper uses `add_messages`, which tells LangGraph how to merge new messages into the existing state automatically.

### 3. Building the app
The `build_app()` function creates a state graph using `StateGraph(State)`.

Inside it, a function named `chatbot(state)` is defined. This function:
- reads the latest message from the state
- checks whether a `GROQ_API_KEY` environment variable exists
- if present, creates a `ChatGroq` model and sends the user message to it
- if absent, returns a fallback message explaining that the API key is missing

The function returns a dictionary containing the model reply as a new message.

### 4. Graph structure
The graph is configured as follows:
- a node called `chatbot` is added
- it is set as the entry point
- the chatbot node connects to `END`, meaning the workflow finishes after the chatbot responds

This creates a simple one-step graph: input message → chatbot → finish.

### 5. Running the app
When the script is executed directly:
- it prints the graph in ASCII form
- it prints the graph in Mermaid form
- it invokes the app with a sample message: `Hello LangGraph + Groq`
- it prints the final response from the model

## Important notes
- The app depends on a valid `GROQ_API_KEY` being available in the environment.
- If the key is missing, the app will not call the model and instead return a fallback response.
- The example is intentionally simple and shows the basic structure of a LangGraph workflow.

## In simple terms
This code is a beginner-friendly example of a LangGraph app that uses a language model to reply to a user message. It demonstrates how to define state, create a graph, add a node, and run the graph from Python.
