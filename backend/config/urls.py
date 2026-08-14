from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("casting.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]

# Les photos uploadées ne sont pas des statiques collectés. `static()` de Django
# ne fait rien quand DEBUG=False : on déclare donc la route explicitement, sinon
# les photos disparaissent en production (pas de serveur web devant l'app ici).
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]

if (settings.RACINE / "frontend" / "dist" / "index.html").exists():
    # Route attrape-tout du front : elle doit rester en dernier et surtout ne pas
    # avaler les fichiers construits par Vite, servis à la racine sous /assets/
    # (et non sous /static/) — sinon le navigateur reçoit index.html à la place
    # du bundle JavaScript, et la page reste blanche.
    urlpatterns += [
        re_path(
            r"^(?!api/|admin/|media/|static/|assets/|favicon|icons|manifest|robots|sw\.js)"
            r".*$",
            TemplateView.as_view(template_name="index.html"),
            name="front",
        ),
    ]
