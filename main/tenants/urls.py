from django.urls import path
from main.tenants import views
from django.contrib import admin

urlpatterns = [
    path("", views.HomeView.as_view()),
    path("admin/", admin.site.urls),
]
