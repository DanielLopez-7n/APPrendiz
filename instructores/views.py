from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Instructor

@login_required
def listar_instructores(request):
    # Traemos todos los instructores
    instructores = Instructor.objects.all()
    context = {
        'instructores': instructores
    }
    return render(request, 'instructores/listar_instructores.html', context)