from django.urls import path
from . import views

app_name = 'inquiry'

urlpatterns = [
    path('', views.submit_inquiry, name='submit'),
    path('success/', views.success, name='success'),
]