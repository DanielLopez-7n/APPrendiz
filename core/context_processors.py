from .models import Notificacion


def notificaciones_no_leidas(request):
    """
    Context processor que inyecta las notificaciones del usuario 
    logueado en TODOS los templates automáticamente.
    """
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.filter(
            usuario_destino=request.user,
            leida=False
        ).order_by('-fecha_creacion')[:10]

        total_no_leidas = Notificacion.objects.filter(
            usuario_destino=request.user,
            leida=False
        ).count()

        return {
            'notificaciones': notificaciones,
            'total_no_leidas': total_no_leidas,
        }
    return {
        'notificaciones': [],
        'total_no_leidas': 0,
    }
