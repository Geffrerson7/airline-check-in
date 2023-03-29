from .models import Flight, BoardingPass


def flight_data(flight_id):
    """Función que recibe el id del vuelo y retorna los datos del vuelo en formato CamelCase."""
    flights = Flight.objects.filter(flight_id=flight_id)
    if not flights:
        return None

    flight = flights[0]

    boarding_passes = (
        BoardingPass.objects.filter(
            flight_id=flight.flight_id,
        )
        .prefetch_related("passenger")
        .order_by("purchase_id", "passenger__age")
    )

    if not boarding_passes:
        return None

    # Crear la respuesta en formato JSON de los datos del vuelo
    data = {
        "flightId": flight.flight_id,
        "takeoffDateTime": flight.takeoff_date_time,
        "takeoffAirport": flight.takeoff_airport,
        "landingDateTime": flight.landing_date_time,
        "landingAirport": flight.landing_airport,
        "airplaneId": flight.airplane_id,
        "passengers": [],
    }
    # Crear los datos del pasajero del vuelo y de su respectiva tarjeta de embarque
    for boarding_pass in boarding_passes:
        passenger = boarding_pass.passenger
        data["passengers"].append(
            {
                "passengerId": passenger.passenger_id,
                "dni": int(passenger.dni),
                "name": passenger.name,
                "age": passenger.age,
                "country": passenger.country,
                "boardingPassId": boarding_pass.boarding_pass_id,
                "purchaseId": boarding_pass.purchase_id,
                "seatTypeId": boarding_pass.seat_type_id,
                "seatId": boarding_pass.seat_id,
            }
        )
    return data