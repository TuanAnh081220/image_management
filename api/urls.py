from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_over_view, name="api-overview"),
]
