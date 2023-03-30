from .models import Flight, BoardingPass, Seat
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from django.db.utils import OperationalError
from typing import List


@retry(
    stop=stop_after_attempt(5),  # Intenta hasta 5 veces
    wait=wait_fixed(1),  # Espera 1 segundo antes de intentar de nuevo
    retry=retry_if_exception_type(
        OperationalError
    ),  # Solo reintenta si es un error de conexión
)
def flight_data(flight_id: int) -> List:
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


@retry(
    stop=stop_after_attempt(5),  # Intenta hasta 5 veces
    wait=wait_fixed(1),  # Espera 1 segundo antes de intentar de nuevo
    retry=retry_if_exception_type(
        OperationalError
    ),  # Solo reintenta si es un error de conexión
)
def seats_list() -> List:
    """Función que devuelve una lista de todas las sillas ordenadas por id"""
    seats_list = Seat.objects.all().order_by("seat_id")
    seats = []
    for seat in seats_list:
        seats.append(seat)
    return seats


def occupied_seats_id(passengers_list: List) -> List:
    """Función que recibe una lista de datos de pasajeros de un vuelo y retorna la lista de id de asientos ocupados."""
    occupied_seats_id = []

    for passenger in passengers_list:
        if passenger["seatId"] != None:
            occupied_seats_id.append(passenger["seatId"])

    return occupied_seats_id


@retry(
    stop=stop_after_attempt(5),  # Intenta hasta 5 veces
    wait=wait_fixed(1),  # Espera 1 segundo antes de intentar de nuevo
    retry=retry_if_exception_type(
        OperationalError
    ),  # Solo reintenta si es un error de conexión
)
def list_of_available_seat_type_ids(seat_type_id: int, flight_data: List) -> List:
    "Función que recibe el id de tipo de aiento y los datos del vuelo y retorna los id de los asientos disponibles por clase."
    seats = Seat.objects.filter(
        airplane_id=flight_data["airplaneId"], seat_type_id=seat_type_id
    )

    if not seats:
        return None

    seat_type_id_list = []

    for seat in seats:
        seat_type_id_list.append(seat.seat_id)

    occupied_seat_id_list = occupied_seats_id(flight_data["passengers"])
    seat_available_type_id_list = list(
        set(seat_type_id_list) - set(occupied_seat_id_list)
    )
    return seat_available_type_id_list


def left_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento de la izquierda."""
    seat_x = seats_list[seat_id - 1]

    left_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == chr(ord(seat_x.seat_column) - 1)
            and seat.seat_row == seat_x.seat_row
            and seat.airplane_id == seat_x.airplane_id
        ):
            left_seat_id = seat.seat_id
            break
    return left_seat_id


def right_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento de la derecha."""
    seat_x = seats_list[seat_id - 1]

    right_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == chr(ord(seat_x.seat_column) + 1)
            and seat.seat_row == seat_x.seat_row
            and seat.airplane_id == seat_x.airplane_id
        ):
            right_seat_id = seat.seat_id
            break
    return right_seat_id


def front_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento frontal."""
    seat_x = seats_list[seat_id - 1]

    front_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == seat_x.seat_column
            and seat.seat_row == seat_x.seat_row - 1
            and seat.airplane_id == seat_x.airplane_id
        ):
            front_seat_id = seat.seat_id
            break
    return front_seat_id


def back_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento trasero."""
    seat_x = seats_list[seat_id - 1]

    back_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == seat_x.seat_column
            and seat.seat_row == seat_x.seat_row + 1
            and seat.airplane_id == seat_x.airplane_id
        ):
            back_seat_id = seat.seat_id
            break
    return back_seat_id


def northeast_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento del noreste."""
    seat_x = seats_list[seat_id - 1]

    northeast_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == chr(ord(seat_x.seat_column) + 1)
            and seat.seat_row == seat_x.seat_row - 1
            and seat.airplane_id == seat_x.airplane_id
        ):
            northeast_seat_id = seat.seat_id
            break
    return northeast_seat_id


def southeast_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento del sureste."""
    seat_x = seats_list[seat_id - 1]

    southeast_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == chr(ord(seat_x.seat_column) + 1)
            and seat.seat_row == seat_x.seat_row + 1
            and seat.airplane_id == seat_x.airplane_id
        ):
            southeast_seat_id = seat.seat_id
            break
    return southeast_seat_id


def northwest_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento del noroeste."""
    seat_x = seats_list[seat_id - 1]

    northwest_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == chr(ord(seat_x.seat_column) - 1)
            and seat.seat_row == seat_x.seat_row - 1
            and seat.airplane_id == seat_x.airplane_id
        ):
            northwest_seat_id = seat.seat_id
            break
    return northwest_seat_id


def southwest_seat_id(seat_id: int, seats_list: List) -> int:
    """Función que recibe el id de un asiento y una lista de total de asientos y retorna el id del asiento del suroeste."""
    seat_x = seats_list[seat_id - 1]

    southwest_seat_id = None
    for seat in seats_list:
        if (
            seat.seat_column == chr(ord(seat_x.seat_column) - 1)
            and seat.seat_row == seat_x.seat_row + 1
            and seat.airplane_id == seat_x.airplane_id
        ):
            southwest_seat_id = seat.seat_id
            break
    return southwest_seat_id


def seats_distribution(id: int) -> List:
    """Función que recibe los datos de un veulo y retorna los mismos datos pero con asientos asignados a cada pasajero"""
    data = flight_data(id)
    if not data:
        return None

    seats_data = seats_list()  # Lista de de datos de todos los asientos

    first_class = list_of_available_seat_type_ids(
        1, data
    )  # Lista de ids asientos de primera clase
    premiun_economic_class = list_of_available_seat_type_ids(
        2, data
    )  # Lista de ids asientos de clase económica premiun
    economic_class = list_of_available_seat_type_ids(
        3, data
    )  # Lista de ids asientos de clase económica

    available_seats_ids = {
        1: first_class,
        2: premiun_economic_class,
        3: economic_class,
    }

    list_of_empty_seat_ids = []

    passengers = data["passengers"]

    # Distribución de asientos para los menores de edad
    for passenger in passengers:

        list_of_empty_seat_ids = available_seats_ids[
            passenger["seatTypeId"]
        ]  # Id de asientos disponibles segun el tipo de asiento del pasajero
        assigned = False

        if passenger["age"] < 18 and passenger["seatId"] == None:
            # Lista de datos de acompañantes sin asiento que tiene el menor de edad
            companions = [
                companion
                for companion in passengers
                if companion.get("purchaseId") == passenger["purchaseId"]
                and companion.get("seatId") == None
                and companion.get("passengerId") != passenger["passengerId"]
                and companion.get("passengerId") >= 18
            ]
            for companion in companions:
                if passengers[passengers.index(companion)]["seatId"] == None:
                    for seat_id in list_of_empty_seat_ids:
                        # Si es que existe el asiento vecino izquierdo
                        if (
                            left_seat_id(seat_id, seats_data)
                            and left_seat_id(seat_id, seats_data)
                            in list_of_empty_seat_ids
                        ):

                            if passenger["seatId"] == None:
                                # Actualizamos el valor del seatId del pasajero menor de edad
                                passenger["seatId"] = seat_id
                                # Eliminamos el id del asiento del menor de edad de la lista de ids de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(seat_id)
                                )
                            # Actualizamos el valor del seatId del acompañanate del pasajero menor de edad
                            passengers[passengers.index(companion)][
                                "seatId"
                            ] = left_seat_id(seat_id, seats_data)
                            # Eliminamos el id del asiento del acompañanate de la lista de id de asientos disponibles
                            list_of_empty_seat_ids.pop(
                                list_of_empty_seat_ids.index(
                                    left_seat_id(seat_id, seats_data)
                                )
                            )

                            assigned = True
                        # Si es que existe el asiento vecino derecho
                        elif (
                            right_seat_id(seat_id, seats_data)
                            and right_seat_id(seat_id, seats_data)
                            in list_of_empty_seat_ids
                        ):

                            if passenger["seatId"] == None:
                                # Actualizamos el valor del seatId del pasajero menor de edad
                                passenger["seatId"] = seat_id
                                # Eliminamos el id del asiento del menor de edad de la lista de id de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(seat_id)
                                )
                            # Actualizamos el valor del seatId del acompañanate del pasajero menor de edad
                            passengers[passengers.index(companion)][
                                "seatId"
                            ] = right_seat_id(seat_id, seats_data)
                            # Eliminamos el id del asiento del acompañanate de la lista de id de asientos disponibles
                            list_of_empty_seat_ids.pop(
                                list_of_empty_seat_ids.index(
                                    right_seat_id(seat_id, seats_data)
                                )
                            )

                            assigned = True

                        if assigned:
                            break
                # Actualizo la cantidad de asientos disponibles
                available_seats_ids[passenger["seatTypeId"]] = list_of_empty_seat_ids

    # Distribución de asientos para adultos que tienen el mismo purchase id
    for passenger in passengers:
        # Id de asientos disponibles segun el tipo de asiento del pasajero
        list_of_empty_seat_ids = available_seats_ids[passenger["seatTypeId"]]
        assigned = False
        # Si el pasajero es menor de edad y no tiene asiento
        if passenger["age"] >= 18 and passenger["seatId"] == None:
            companions = [
                companion
                for companion in passengers
                if companion.get("purchaseId") == passenger["purchaseId"]
                and companion.get("seatId") == None
                and companion.get("passengerId") != passenger["passengerId"]
            ]
            if companions != []:
                for companion in companions:
                    if passengers[passengers.index(companion)]["seatId"] == None:
                        for seat_id in list_of_empty_seat_ids:
                            # Si es que existe el asiento vecino izquierdo
                            if (
                                left_seat_id(seat_id, seats_data)
                                and left_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):

                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = left_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        left_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True
                            # Si es que existe el asiento vecino derecho
                            elif (
                                right_seat_id(seat_id, seats_data)
                                and right_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):
                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = right_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        right_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True
                            # Si es que existe el asiento vecino frontal
                            elif (
                                front_seat_id(seat_id, seats_data)
                                and front_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):
                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = front_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        front_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True
                            # Si es que existe el asiento vecino trasero
                            elif (
                                back_seat_id(seat_id, seats_data)
                                and back_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):
                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = back_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        back_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True
                            # Si es que existe el asiento vecino noreste
                            elif (
                                northeast_seat_id(seat_id, seats_data)
                                and northeast_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):
                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = northeast_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        northeast_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True
                            # Si es que existe el asiento vecino sureste
                            elif (
                                southeast_seat_id(seat_id, seats_data)
                                and southeast_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):
                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = southeast_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        southeast_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True
                            # Si es que existe el asiento vecino noroeste
                            elif (
                                northwest_seat_id(seat_id, seats_data)
                                and northwest_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):
                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = northwest_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        northwest_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True
                            elif (
                                southwest_seat_id(seat_id, seats_data)
                                and southwest_seat_id(seat_id, seats_data)
                                in list_of_empty_seat_ids
                            ):
                                if passenger["seatId"] == None:
                                    # Actualizamos el valor del seatId del pasajero
                                    passenger["seatId"] = seat_id
                                    # Eliminamos el id del asiento asignado al pasajero de la lista de asientos disponibles
                                    list_of_empty_seat_ids.pop(
                                        list_of_empty_seat_ids.index(seat_id)
                                    )
                                # Actualizamos el valor del seatId del acompañanate del pasajero
                                passengers[passengers.index(companion)][
                                    "seatId"
                                ] = southwest_seat_id(seat_id, seats_data)
                                # Eliminamos el id del asiento asignado al acompañante del pasajero de la lista de asientos disponibles
                                list_of_empty_seat_ids.pop(
                                    list_of_empty_seat_ids.index(
                                        southwest_seat_id(seat_id, seats_data)
                                    )
                                )
                                assigned = True

                            if assigned:
                                break
                # Se actualiza la lista de id de asientos disponibles
                available_seats_ids[passenger["seatTypeId"]] = list_of_empty_seat_ids

    # Distribución de asientos para los pasajeros restantes
    for passenger in passengers:
        # Id de asientos disponibles segun el tipo de asiento del pasajero
        list_of_empty_seat_ids = available_seats_ids[passenger["seatTypeId"]]

        if passenger["seatId"] == None:
            passenger["seatId"] = list_of_empty_seat_ids[0]
            list_of_empty_seat_ids.pop(0)
            available_seats_ids[passenger["seatTypeId"]] = list_of_empty_seat_ids

    data["passengers"] = passengers

    return data
