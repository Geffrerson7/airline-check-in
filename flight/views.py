from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import flight_data

# Create your views here.
class AirlineCheckInView(APIView):
    def get(self, request, id):
        try:

            flight_id = id
            data = flight_data(flight_id)

            

            if data == None:
                return Response({"code": 404, "data": {}})

            return Response({"code": 200, "data": data})

        except Exception as e:
            print("Ocurrió un error:", e)
            print("Traceback completo:")
            import traceback

            traceback.print_exc()
            return Response({"code": 400, "errors": "could not connect to db"})