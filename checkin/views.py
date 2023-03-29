from django.urls import reverse
from django.utils.module_loading import import_module
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect


class ApiRootView(APIView):
    """Endpoint que redirecciona la ruta raiz a la ruta /flights/1/passengers."""
    def get(self, request, format=None):

        for app_name in settings.INSTALLED_APPS:
            try:
                if app_name == "flight":
                    app_urls = import_module(f"{app_name}.urls")
                    if app_urls:
                        for url in app_urls.urlpatterns:
                            if url.name == "flight-passengers":

                                url_with_id = reverse(
                                    "flight-passengers", kwargs={"id": 1}
                                )

            except ModuleNotFoundError:
                pass
        return redirect(url_with_id)
