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
    intent: str
    topic: str
    preferred_tone: str
    turn_count: int


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

    def context_node(state: State):
        last_user_message = state["messages"][-1].content if state["messages"] else ""
        text = str(last_user_message).strip().lower()

        topic = state.get("topic", "general")
        if "langgraph" in text:
            topic = "LangGraph"
        elif "python" in text:
            topic = "Python"
        elif "llm" in text or "model" in text:
            topic = "LLMs"

        preferred_tone = state.get("preferred_tone", "normal")
        if "short" in text or "brief" in text:
            preferred_tone = "short"
        elif "detailed" in text or "explain more" in text:
            preferred_tone = "detailed"

        intent = "question" if "?" in text else "statement"
        turn_count = state.get("turn_count", 0) + 1
        return {
            "intent": intent,
            "topic": topic,
            "preferred_tone": preferred_tone,
            "turn_count": turn_count,
        }

    def router_node(state: State):
        text = str(state["messages"][-1].content).strip().lower() if state["messages"] else ""

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
        is_question = state.get("intent") == "question" or text.startswith(question_starters)
        return {"route": "answer" if is_question else "clarify"}

    def answer_node(state: State):
        last_user_message = state["messages"][-1].content if state["messages"] else "Hello"
        preferred_tone = state.get("preferred_tone", "normal")
        topic = state.get("topic", "general")
        turn_count = state.get("turn_count", 1)

        style_instruction = "Respond in 1-2 short sentences." if preferred_tone == "short" else "Respond with a concise but clear explanation."
        if preferred_tone == "detailed":
            style_instruction = "Respond with a detailed but beginner-friendly explanation."

        prompt = (
            "You are a helpful assistant.\n"
            f"Known user topic preference: {topic}.\n"
            f"Current turn count: {turn_count}.\n"
            f"Tone preference: {preferred_tone}. {style_instruction}\n"
            f"User: {last_user_message}"
        )
        reply = call_llm(prompt)
        return {"messages": [AIMessage(content=reply)]}

    def clarify_node(state: State):
        last_user_message = state["messages"][-1].content if state["messages"] else ""
        topic = state.get("topic", "this")
        preferred_tone = state.get("preferred_tone", "normal")
        follow_up = (
            "I can help with that. Could you clarify what you want exactly? "
            f"For example: ask a specific question about '{topic}'. "
            f"I can keep the answer {preferred_tone}. "
            f"You wrote: '{last_user_message}'."
        )
        return {"messages": [AIMessage(content=follow_up)]}

    def pick_route(state: State):
        return state["route"]

    builder.add_node("context", context_node)
    builder.add_node("router", router_node)
    builder.add_node("answer", answer_node)
    builder.add_node("clarify", clarify_node)

    builder.set_entry_point("context")
    builder.add_edge("context", "router")
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
        "I prefer short answers about LangGraph.",
        "What is a node in LangGraph?",
        "And how is it different from an edge?",
    ]

    conversation_state: State = {
        "messages": [],
        "route": "clarify",
        "intent": "statement",
        "topic": "general",
        "preferred_tone": "normal",
        "turn_count": 0,
    }

    for user_input in test_inputs:
        conversation_state["messages"].append(HumanMessage(content=user_input))
        conversation_state = app.invoke(conversation_state)
        print("\nUser input:")
        print(user_input)
        print("\nState memory snapshot:")
        print(
            {
                "intent": conversation_state["intent"],
                "topic": conversation_state["topic"],
                "preferred_tone": conversation_state["preferred_tone"],
                "turn_count": conversation_state["turn_count"],
                "route": conversation_state["route"],
            }
        )
        print("\nModel response:")
        print(conversation_state["messages"][-1].content)
