import ast
import operator as op
import os
import re
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


class StudyBuddyState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    task_type: str
    topic: str
    preferred_tone: str
    turn_count: int
    tool_result: str
    needs_clarification: bool


_SAFE_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def calculator_tool(expression: str) -> str:
    def _eval(node: ast.expr) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported operation: {ast.dump(node)}")

    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _eval(tree.body)
        return str(int(result) if result == int(result) else result)
    except Exception as exc:
        return f"Error: {exc}"


def glossary_tool(topic: str) -> str:
    glossary = {
        "langgraph": "LangGraph is a framework for building stateful, multi-step LLM workflows as graphs.",
        "node": "A node is a step in the workflow that reads state and returns state updates.",
        "edge": "An edge connects nodes and controls what step runs next.",
        "python": "Python is a general-purpose programming language often used to build AI workflows and tools.",
    }
    normalized = topic.strip().lower()
    return glossary.get(
        normalized,
        f"I do not have a glossary entry for '{topic}', but I can still explain it from context.",
    )


def build_app():
    builder = StateGraph(StudyBuddyState)

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

    def understand_node(state: StudyBuddyState):
        last_user_message = state["messages"][-1].content if state["messages"] else ""
        text = str(last_user_message).strip().lower()

        topic = state.get("topic", "general")
        if "langgraph" in text:
            topic = "langgraph"
        elif "node" in text:
            topic = "node"
        elif "edge" in text:
            topic = "edge"
        elif "python" in text:
            topic = "python"

        preferred_tone = state.get("preferred_tone", "normal")
        if "short" in text or "brief" in text:
            preferred_tone = "short"
        elif "detailed" in text or "step by step" in text:
            preferred_tone = "detailed"

        task_type = "explain"
        if re.search(r"[\d\.]+\s*[\+\-\*\/]\s*[\d\.]", text) or "calculate" in text:
            task_type = "calculate"
        elif any(keyword in text for keyword in ("define", "meaning of", "what is a", "what is an")):
            task_type = "lookup"

        vague_requests = {
            "help me",
            "i do not understand",
            "can you help",
            "homework",
            "study",
        }
        has_specific_action = task_type in {"calculate", "lookup"} or "?" in text
        needs_clarification = text in vague_requests or (
            len(text.split()) < 4 and not has_specific_action
        )

        return {
            "task_type": task_type,
            "topic": topic,
            "preferred_tone": preferred_tone,
            "turn_count": state.get("turn_count", 0) + 1,
            "needs_clarification": needs_clarification,
        }

    def decide_node(state: StudyBuddyState):
        if state.get("needs_clarification", False):
            return {"route": "clarify"}

        task_type = state.get("task_type", "explain")
        if task_type == "calculate":
            return {"route": "tool_calculator"}
        if task_type == "lookup":
            return {"route": "tool_glossary"}
        return {"route": "answer"}

    def calculator_node(state: StudyBuddyState):
        last_msg = str(state["messages"][-1].content) if state["messages"] else ""
        match = re.search(r"[\d\.]+(?:\s*[\+\-\*\/]\s*[\d\.]+)+", last_msg)
        expression = match.group(0) if match else ""
        result = calculator_tool(expression) if expression else "No valid arithmetic expression found."
        return {"tool_result": f"Calculator result: {result}"}

    def glossary_node(state: StudyBuddyState):
        topic = state.get("topic", "general")
        result = glossary_tool(topic)
        return {"tool_result": f"Glossary lookup: {result}"}

    def answer_node(state: StudyBuddyState):
        last_user_message = state["messages"][-1].content if state["messages"] else "Hello"
        preferred_tone = state.get("preferred_tone", "normal")
        topic = state.get("topic", "general")
        turn_count = state.get("turn_count", 1)
        tool_result = state.get("tool_result", "")

        style_instruction = "Reply in 1-2 short sentences."
        if preferred_tone == "normal":
            style_instruction = "Reply with a concise but clear explanation."
        elif preferred_tone == "detailed":
            style_instruction = "Reply with a beginner-friendly explanation in clear steps."

        tool_section = f"{tool_result}\n" if tool_result else ""
        prompt = (
            "You are a study buddy assistant helping a learner with homework and core concepts.\n"
            f"Current topic: {topic}.\n"
            f"Turn count: {turn_count}.\n"
            f"Tone preference: {preferred_tone}. {style_instruction}\n"
            "If a tool result is provided, use it directly and explain it simply.\n"
            f"{tool_section}"
            f"User request: {last_user_message}"
        )
        reply = call_llm(prompt)
        return {"messages": [AIMessage(content=reply)], "tool_result": ""}

    def clarify_node(state: StudyBuddyState):
        topic = state.get("topic", "your homework topic")
        preferred_tone = state.get("preferred_tone", "normal")
        reply = (
            "I can help, but I need a more specific question. "
            f"Tell me the concept, problem, or example you want help with about {topic}. "
            f"I can answer in a {preferred_tone} style."
        )
        return {"messages": [AIMessage(content=reply)], "tool_result": ""}

    def pick_route(state: StudyBuddyState):
        return state["route"]

    builder.add_node("understand", understand_node)
    builder.add_node("decide", decide_node)
    builder.add_node("calculator", calculator_node)
    builder.add_node("glossary", glossary_node)
    builder.add_node("answer", answer_node)
    builder.add_node("clarify", clarify_node)

    builder.set_entry_point("understand")
    builder.add_edge("understand", "decide")
    builder.add_conditional_edges(
        "decide",
        pick_route,
        {
            "answer": "answer",
            "clarify": "clarify",
            "tool_calculator": "calculator",
            "tool_glossary": "glossary",
        },
    )
    builder.add_edge("calculator", "answer")
    builder.add_edge("glossary", "answer")
    builder.add_edge("answer", END)
    builder.add_edge("clarify", END)

    return builder.compile()


app = build_app()


if __name__ == "__main__":
    graph = app.get_graph()
    mermaid_graph = graph.draw_mermaid()

    with open("phase6_graph.md", "w", encoding="utf-8") as file_handle:
        file_handle.write("# Phase 6 Mermaid Diagram\n\n")
        file_handle.write("```mermaid\n")
        file_handle.write(mermaid_graph)
        file_handle.write("\n```\n")

    print("ASCII graph:")
    print(graph.draw_ascii())
    print("\nMermaid graph saved to phase6_graph.md")

    test_inputs = [
        "I want short answers for my homework.",
        "What is a node in LangGraph?",
        "Calculate 14 * 12",
        "help me",
        "Define edge",
    ]

    conversation_state: StudyBuddyState = {
        "messages": [],
        "route": "answer",
        "task_type": "explain",
        "topic": "general",
        "preferred_tone": "normal",
        "turn_count": 0,
        "tool_result": "",
        "needs_clarification": False,
    }

    for user_input in test_inputs:
        conversation_state["messages"].append(HumanMessage(content=user_input))
        conversation_state = app.invoke(conversation_state)
        print("\nUser input:")
        print(user_input)
        print("\nState snapshot:")
        print(
            {
                "route": conversation_state["route"],
                "task_type": conversation_state["task_type"],
                "topic": conversation_state["topic"],
                "preferred_tone": conversation_state["preferred_tone"],
                "turn_count": conversation_state["turn_count"],
                "needs_clarification": conversation_state["needs_clarification"],
                "tool_result": conversation_state["tool_result"],
            }
        )
        print("\nAssistant response:")
        print(conversation_state["messages"][-1].content)