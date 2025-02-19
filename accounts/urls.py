from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", user_login, name="login"),
    path("doctor_dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("patient_dashboard/", patient_dashboard, name="patient_dashboard"),
]