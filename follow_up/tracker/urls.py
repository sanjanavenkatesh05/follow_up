from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="tracker/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create/", views.create_followup, name="create_followup"),
    path("edit/<int:pk>/", views.edit_followup, name="edit_followup"),
    path("mark_done/<int:pk>/", views.mark_done, name="mark_done"),
    path("p/<str:token>/", views.public_followup, name="public_followup"),#Public Followup url that doesnt require login
]
