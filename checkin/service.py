from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_module


def route_redirection() -> str:
    "Función que retorna la ruta flights/1/passengers"
    url_with_id = "/"
    for app_name in settings.INSTALLED_APPS:

        if app_name == "flight":
            app_urls = import_module(f"{app_name}.urls")
            if app_urls:
                for url in app_urls.urlpatterns:
                    if url.name == "flight-passengers":

                        url_with_id = reverse("flight-passengers", kwargs={"id": 1})

    return url_with_id
