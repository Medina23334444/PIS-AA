import uuid
from django.utils.deprecation import MiddlewareMixin
from .models import Evento


class CsrfEventMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # 1) page_load: cada vez que llegue un GET a una vista con formulario
        if request.method == "GET" and self._is_form_view(view_func):
            Evento.objects.create(
                sesion_id=request.session.session_key or str(uuid.uuid4()),
                tipo_evento="page_load",
                datos={"path": request.path}
            )
            Evento.objects.create(
                sesion_id=request.session.session_key,
                tipo_evento="form_render",
                datos={"path": request.path}
            )
        return None

    def process_response(self, request, response):
        # 2) request_end: al terminar cualquier petición
        Evento.objects.create(
            sesion_id=request.session.session_key,
            tipo_evento="request_end",
            datos={"status_code": response.status_code}
        )
        return response

    def _is_form_view(self, view_func):
        # aquí pones tu lógica: nombres de vistas, rutas, etc.
        name = view_func.__name__.lower()
        return "login" in name or "form" in name or "register" in name
