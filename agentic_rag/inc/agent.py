"""LangChain agent for chat."""
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from .tools import tools


class AgenticRAG:
    """Chat agent with tool support."""

    def __init__(self, model: str = "gpt-4-turbo", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.agent = create_agent(self.llm, tools) 

    def query(self, question: str) -> dict:
        """Process query."""
        try:
            result = self.agent.invoke({"messages": [("user", question)]})
            response = result["messages"][-1].content
            return {
                "status": "success",
                "response": response,
                "tools_used": []
            }
        except Exception as e:
            return {
                "status": "error",
                "response": f"Error: {str(e)}",
                "tools_used": []
            }


_agent_instance = None

def get_agent(model: str = "gpt-4-turbo", temperature: float = 0.7) -> AgenticRAG:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgenticRAG(model, temperature)
    return _agent_instance
