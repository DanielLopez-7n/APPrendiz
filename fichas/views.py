from django.shortcuts import render
from .models import Ficha
from django.db.models import Q


def listar_fichas(request):
    fichas = Ficha.objects.all()
    query = request.GET.get('q', '')

    if query:
        fichas = fichas.filter(
            Q(numero__icontains=query) |
            Q(programa__nombre__icontains=query)
        )

    context = {
        'fichas': fichas,
    }
    return render(request, 'fichas/listar_fichas.html', context)
