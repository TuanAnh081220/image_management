from django.urls import path
from .views import UsersViewSet, example_view

urlpatterns = [
    path('', UsersViewSet.as_view({'get': 'list'}), name="users_view_and_retrieve"),
    path('<int:pk>', UsersViewSet.as_view({'get': 'retrieve'}), name="retrieve user"),
    path('example', example_view, name="example_view")
]
