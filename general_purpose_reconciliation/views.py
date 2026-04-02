from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def table_matching(request):
    try:
        user_filename = request.GET.get('user_filename')
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)