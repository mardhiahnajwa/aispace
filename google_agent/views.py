"""Google Agent Views using ADK."""
import json
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from google.adk.agents.llm_agent import Agent


# Tool functions
def get_current_time(city: str) -> dict:
    """Returns current time in a specified city."""
    cities_tz = {
        "new york": "EST",
        "london": "GMT",
        "tokyo": "JST",
        "sydney": "AEDT",
    }
    tz = cities_tz.get(city.lower(), "Unknown")
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return {
        "status": "success",
        "city": city,
        "time": current_time,
        "timezone": tz
    }


def get_weather(location: str) -> dict:
    """Returns weather for a location."""
    return {
        "status": "success",
        "location": location,
        "temperature": "72°F",
        "condition": "Sunny",
        "humidity": "45%"
    }


# Create the root agent with tools
root_agent = Agent(
    model='gemini-2.0-flash',
    name='chat_agent',
    description="A helpful AI assistant that can answer questions and use tools.",
    instruction="""You are a helpful and friendly AI assistant. You can:
1. Answer general knowledge questions
2. Use the 'get_current_time' tool to tell users the current time in different cities
3. Use the 'get_weather' tool to provide weather information
4. Have natural conversations and provide detailed explanations

Always be helpful, accurate, and polite in your responses.""",
    tools=[get_current_time, get_weather],
)


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Chat endpoint using Google ADK."""
    try:
        data = json.loads(request.body)
        query = data.get('query')

        if not query:
            return JsonResponse(
                {"error": "Query is required"},
                status=400
            )

        # Send query to ADK agent
        response = root_agent.run(query)
        
        return JsonResponse({
            "status": "success",
            "response": response,
            "model": "gemini-2.0-flash",
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON in request body"},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e), "status": "error"},
            status=500
        )
