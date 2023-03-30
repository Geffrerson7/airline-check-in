from django.urls import path
from . import views

urlpatterns = [
    path(
        "<int:id>/passengers",
        views.AirlineCheckInView.as_view(),
        name="flight-passengers",
    ),
]
