from django.urls import path
from . import views


app_name = "accounts"
urlpatterns = [
    # public profile anyone can see
    path("profile/<slug:username>/", views.ProfileView.as_view(), name="profile"),
    # private profile only logged in
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
]
