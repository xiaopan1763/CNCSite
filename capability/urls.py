from django.urls import path
from . import views

app_name = 'capability'

urlpatterns = [
    path('', views.CapabilityListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),
    path('<slug:slug>/', views.CapabilityDetailView.as_view(), name='detail'),
]