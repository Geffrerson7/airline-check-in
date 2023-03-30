from django.db import models


class Airplane(models.Model):

    airplane_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "airplane"


class Flight(models.Model):

    flight_id = models.AutoField(primary_key=True)
    takeoff_date_time = models.IntegerField()
    takeoff_airport = models.CharField(max_length=255)
    landing_date_time = models.IntegerField()
    landing_airport = models.CharField(max_length=255)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "flight"


class Passenger(models.Model):

    passenger_id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    country = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "passenger"


class Purchase(models.Model):

    purchase_id = models.AutoField(primary_key=True)
    purchase_date = models.IntegerField()

    class Meta:
        managed = False
        db_table = "purchase"


class SeatType(models.Model):

    seat_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "seat_type"


class Seat(models.Model):

    seat_id = models.AutoField(primary_key=True)
    seat_column = models.CharField(max_length=2)
    seat_row = models.IntegerField()
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "seat"


class BoardingPass(models.Model):

    boarding_pass_id = models.AutoField(primary_key=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, blank=True, null=True, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "boarding_pass"
