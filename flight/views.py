from rest_framework.views import APIView
from rest_framework.response import Response
from .service import seats_distribution
import traceback
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AirlineCheckInView(APIView):
    @swagger_auto_schema(
        operation_description="Get information about passengers on a flight by ID.",
        responses={
            200: "Successful response",
            404: "Flight not found",
            400: "Error connecting to the database",
        },
        tags=["Flights"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID of the flight to get passengers from",
                required=True,
            ),
        ],
    )
    def get(self, request, id):

        try:

            simulation_data = seats_distribution(id)

            if simulation_data == None:
                return Response({"code": 404, "data": {}})

            return Response({"code": 200, "data": simulation_data})

        except Exception as e:
            print("Ocurrió un error:", e)
            print("Traceback completo:")
            traceback.print_exc()
            return Response({"code": 400, "errors": "could not connect to db"})
