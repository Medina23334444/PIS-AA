import uuid
from functools import wraps
from .models import Evento


def log_event(tipo):
    def deco(fn):
        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            if request.method in ("POST", "PUT", "DELETE") or tipo == "request_end":
                Evento.objects.create(
                    sesion_id=request.session.session_key,
                    tipo_evento=tipo,
                    datos={
                        "path": request.path,
                        "username": request.user.username if request.user.is_authenticated else None
                    }
                )
            return fn(request, *args, **kwargs)

        return wrapped

    return deco
