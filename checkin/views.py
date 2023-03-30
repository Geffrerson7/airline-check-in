from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from django.shortcuts import redirect
from .service import route_redirection


class ApiRootView(APIView):
    @swagger_auto_schema(
        operation_description="View that redirects to checkin simulation when flight id is 1",
        responses={
            200: "Redirect to route flights/1/passengers",
        },
    )
    def get(self, request, format=None):
        try:
            url_with_id = route_redirection()

        except ModuleNotFoundError:
            pass
        return redirect(url_with_id)
