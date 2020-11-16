from django.http import JsonResponse
from rest_framework.decorators import api_view


# Create your views here.

@api_view(['GET'])
def api_over_view(request):
    print(request.data)
    return JsonResponse("api overview", safe=False)
