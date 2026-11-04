import logging

from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from .session import session_scope

logger = logging.getLogger(__name__)


@never_cache
def csrf_failure(request, reason=""):
    scope, _ = session_scope(request.path_info)
    name, login_view = {
        "student": ("學生端", "accounts:login"),
        "school": ("學校端", "school:login"),
        "admin": ("管理後台", "admin:login"),
    }[scope]
    # Keep diagnostics server-side. Never echo submitted data or replay the POST.
    logger.warning("CSRF rejected for %s: %s", request.path_info, reason)
    return render(request, "accounts/csrf_failure.html", {
        "portal_name": name,
        "login_url": reverse(login_view),
    }, status=403)
