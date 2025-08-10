
from django.http import JsonResponse

def dashboard(request):
    return JsonResponse({'test': 'test'})
