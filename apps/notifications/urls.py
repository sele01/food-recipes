from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list, name='list'),
    path('mark/<int:notification_id>/', views.mark_notification_read, name='mark_read'),
]