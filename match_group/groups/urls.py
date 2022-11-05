from django.urls import path
from . import views

urlpatterns = [
    path('groups/', views.GroupsViewSet.as_view())
]