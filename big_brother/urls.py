from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:participant_id>/', views.participant_detail, name='participant_detail'),
    path('participants/<int:participant_id>/edit/', views.participant_edit, name='participant_edit'),
]
