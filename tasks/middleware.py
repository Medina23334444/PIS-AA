from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin
import uuid
from .models import Evento


class CsrfEventMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self._csrf_mw = CsrfViewMiddleware(get_response)

    def _get_sid(self, request):
        sid = request.session.session_key
        if not sid:
            request.session.create()
            sid = request.session.session_key
        return sid

    def process_request(self, request):
        sid = self._get_sid(request)
        # external_referrer
        referer = request.META.get("HTTP_REFERER")
        host = request.get_host()
        if referer and host not in referer:
            Evento.objects.create(sesion_id=sid, tipo_evento="external_referrer",
                                  datos={"referer": referer})
        # replay_attempt...
        return self._csrf_mw.process_request(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        sid = self._get_sid(request)
        if request.method == "GET" and self._is_form_view(view_func):
            Evento.objects.create(sesion_id=sid, tipo_evento="page_load",
                                  datos={"path": request.path})
            Evento.objects.create(sesion_id=sid, tipo_evento="form_render",
                                  datos={"path": request.path})
        # valid_token...
        return self._csrf_mw.process_view(request, view_func, view_args, view_kwargs)

    def process_response(self, request, response):
        sid = request.session.session_key or ""
        Evento.objects.create(sesion_id=sid, tipo_evento="request_end",
                              datos={"status_code": response.status_code})
        return self._csrf_mw.process_response(request, response)

    def _is_form_view(self, view_func):
        name = view_func.__name__.lower()
        return any(k in name for k in ("form", "login", "register"))
