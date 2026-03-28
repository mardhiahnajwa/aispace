from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .inc.agent import get_agent


@api_view(['POST'])
def chat(request):
    """Chat endpoint."""
    try:
        data = request.data
        query = data.get('query')

        if not query:
            return Response(
                {"error": "Query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        agent = get_agent(
            model=data.get('model', 'gpt-4-turbo'),
            temperature=float(data.get('temperature', 0.7))
        )

        result = agent.query(query)
        return Response(result)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def history(request):
    """Get conversation history from external database."""
    try:
        from .inc.db_analyzer import get_analyzer
        analyzer = get_analyzer()
        limit = int(request.GET.get('limit', 20))
        
        # Query conversation_log table (user-managed in MariaDB)
        results = analyzer.execute_query(
            f"SELECT * FROM conversation_log ORDER BY created_at DESC LIMIT {limit}"
        )
        
        return Response({
            "status": "success",
            "count": len(results),
            "conversations": results
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health(request):
    """Health check."""
    return Response({
        "status": "healthy",
        "message": "Agentic RAG is running"
    })
