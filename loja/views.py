from django.http import JsonResponse

def clientes(request):
    data = {
        'id': 1,
        'nome': 'João Silva',
    }
    return JsonResponse(data)