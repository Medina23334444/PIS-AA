import uuid
from functools import wraps
from .models import Evento


def log_event(tipo):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.method in ("POST", "PUT", "DELETE"):
                Evento.objects.create(
                    sesion_id=request.session.session_key or str(uuid.uuid4()),
                    tipo_evento=tipo,
                    datos={"path": request.path, "method": request.method}
                )
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator

