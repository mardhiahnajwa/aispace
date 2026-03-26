from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated, Sequence
import operator
import os

# import path

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm_with_tools = None  # Will be set in home view

# Define the tool
@tool
def get_programming_fact(language: str) -> str:
    """Get a fact about a programming language."""
    facts = {
        "python": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used for web development, data science, and automation.",
        "javascript": "JavaScript is a versatile scripting language primarily used for web development, enabling interactive web pages and server-side applications via Node.js.",
        "java": "Java is an object-oriented programming language designed to be platform-independent, commonly used for enterprise applications and Android development.",
        "c++": "C++ is a powerful, high-performance programming language that extends C with object-oriented features, used for system software, games, and real-time simulations.",
        "ruby": "Ruby is a dynamic, open-source programming language with a focus on simplicity and productivity, popular for web development with the Ruby on Rails framework.",
    }
    return facts.get(language.lower(), f"I'm sorry, I don't have information about {language}. Try Python, JavaScript, Java, C++, or Ruby.")

# Define the state
class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]

# Define the agent function
def agent_node(state: AgentState):
    global llm_with_tools
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Define the tool execution function
def tool_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    tool_calls = last_message.tool_calls
    results = []
    for tool_call in tool_calls:
        if tool_call["name"] == "get_programming_fact":
            result = get_programming_fact.invoke(tool_call["args"])
            results.append(result)
    return {"messages": [AIMessage(content=str(results))]}

# Conditional routing
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

# Django view
def home(request):
    global llm_with_tools
    # Bind the tool to the LLM
    llm_with_tools = llm.bind_tools([get_programming_fact])

    # Build the graph
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    # Compile the graph
    agent_executor = graph.compile()

    if request.method == 'GET':
        question = request.GET.get('question', 'Tell me about Python')
        # Run the agent
        result = agent_executor.invoke({"messages": [HumanMessage(content=question)]})
        answer = result["messages"][-1].content
        return JsonResponse({"question": question, "answer": answer})
    return HttpResponse("Use GET with ?question=your question")