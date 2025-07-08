from django.urls import path, include  # Make sure include is imported here
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
]