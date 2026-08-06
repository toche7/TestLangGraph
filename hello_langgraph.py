import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    route: str


def build_app():
    builder = StateGraph(State)

    def call_llm(prompt: str) -> str:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            llm = ChatGroq(
                model="openai/gpt-oss-20b",
                temperature=0,
                groq_api_key=groq_api_key,
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            if isinstance(response.content, str):
                return response.content
            return str(response.content)

        return (
            "GROQ_API_KEY is not set. "
            "Please add it to your .env file to use the model."
        )

    def router_node(state: State):
        last_user_message = state["messages"][-1].content if state["messages"] else ""
        text = str(last_user_message).strip().lower()

        # Treat explicit questions as answerable, otherwise ask for clarification.
        question_starters = (
            "what",
            "why",
            "how",
            "when",
            "where",
            "who",
            "which",
            "can",
            "could",
            "do",
            "does",
            "is",
            "are",
        )
        is_question = "?" in text or text.startswith(question_starters)
        return {"route": "answer" if is_question else "clarify"}

    def answer_node(state: State):
        last_user_message = state["messages"][-1].content if state["messages"] else "Hello"
        prompt = (
            "You are a helpful assistant. Give a short direct answer to the user's question.\n"
            f"User: {last_user_message}"
        )
        reply = call_llm(prompt)
        return {"messages": [AIMessage(content=reply)]}

    def clarify_node(state: State):
        last_user_message = state["messages"][-1].content if state["messages"] else ""
        follow_up = (
            "I can help with that. Could you clarify what you want exactly? "
            f"For example: ask a specific question about '{last_user_message}'."
        )
        return {"messages": [AIMessage(content=follow_up)]}

    def pick_route(state: State):
        return state["route"]

    builder.add_node("router", router_node)
    builder.add_node("answer", answer_node)
    builder.add_node("clarify", clarify_node)

    builder.set_entry_point("router")
    builder.add_conditional_edges(
        "router",
        pick_route,
        {
            "answer": "answer",
            "clarify": "clarify",
        },
    )
    builder.add_edge("answer", END)
    builder.add_edge("clarify", END)
    return builder.compile()


app = build_app()


if __name__ == "__main__":
    graph = app.get_graph()
    mermaid_graph = graph.draw_mermaid()

    with open("graph.md", "w", encoding="utf-8") as f:
        f.write("# LangGraph Mermaid Diagram\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_graph)
        f.write("\n```\n")

    print("ASCII graph:")
    print(graph.draw_ascii())
    print("\nMermaid graph saved to graph.md")

    test_inputs = [
        "What is LangGraph in one sentence?",
        "LangGraph",
    ]

    for user_input in test_inputs:
        result = app.invoke({"messages": [HumanMessage(content=user_input)]})
        print("\nUser input:")
        print(user_input)
        print("\nModel response:")
        print(result["messages"][-1].content)
