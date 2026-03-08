import os
import operator
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated, Sequence

# import path

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

# Initialize the LLM
llm = ChatOpenAI(model="gpt-5.2-mini", temperature=0)

# Django view
def home(request):
    # Create the agent
    agent = create_agent(llm, tools=[get_programming_fact])
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=[get_programming_fact])

    if request.method == 'GET':
        question = request.GET.get('question', 'Tell me about Python')
        # Run the agent
        result = agent_executor.run(question)
        return JsonResponse({"question": question, "answer": result})
    return HttpResponse("Use GET with ?question=your question")