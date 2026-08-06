import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


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
            return response.content

        return (
            "GROQ_API_KEY is not set. "
            "Please add it to your .env file to use the model."
        )

    def route_message(state: State) -> str:
        messages = state["messages"]
        last_text = messages[-1].content.lower() if messages else ""
        if "summary" in last_text:
            return "summary"
        return "joke"

    def router(state: State):
        return {}

    def joke_node(state: State):
        user_text = state["messages"][-1].content if state["messages"] else "Hello"
        prompt = (
            f"Write one short, clean joke about: {user_text}. "
            "Keep it under 20 words."
        )
        reply = call_llm(prompt)
        return {"messages": [HumanMessage(content=reply)]}

    def summary_node(state: State):
        user_text = state["messages"][-1].content if state["messages"] else "Hello"
        prompt = (
            f"Summarize this in exactly one sentence: {user_text}. "
            "Do not use bullet points."
        )
        reply = call_llm(prompt)
        return {"messages": [HumanMessage(content=reply)]}

    builder.add_node("router", router)
    builder.add_node("joke", joke_node)
    builder.add_node("summary", summary_node)
    builder.set_entry_point("router")
    builder.add_conditional_edges("router", route_message, {"joke": "joke", "summary": "summary"})
    builder.add_edge("joke", END)
    builder.add_edge("summary", END)
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

    result = app.invoke({"messages": [HumanMessage(content="Summarize about the sun")]})
    print("\nModel response:")
    print(result["messages"][-1].content)
