from django.shortcuts import render
from .models import Ficha

def listar_fichas(request):
    # Traemos todas las fichas
    fichas = Ficha.objects.all()
    
    context = {
        'titulo': 'Fichas SENA',
        'fichas': fichas,
    }
    return render(request, 'fichas/listar_fichas.html', context)

