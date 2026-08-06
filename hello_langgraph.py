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

    def chatbot(state: State):
        messages = state["messages"]
        user_text = messages[-1].content if messages else "Hello"

        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            llm = ChatGroq(
                model="openai/gpt-oss-20b",
                temperature=0,
                groq_api_key=groq_api_key,
            )
            response = llm.invoke([HumanMessage(content=user_text)])
            reply = response.content
        else:
            reply = (
                "GROQ_API_KEY is not set. "
                f"Export it and re-run. You said: {user_text}"
            )

        return {"messages": [HumanMessage(content=reply)]}

    builder.add_node("chatbot", chatbot)
    builder.set_entry_point("chatbot")
    builder.add_edge("chatbot", END)
    return builder.compile()


app = build_app()


if __name__ == "__main__":
    print("ASCII graph:")
    print(app.get_graph().draw_ascii())
    print("\nMermaid graph:")
    print(app.get_graph().draw_mermaid())

    result = app.invoke({"messages": [HumanMessage(content="Hello LangGraph + Groq")]})
    print("\nModel response:")
    print(result["messages"][-1].content)
