from django.urls import include, path
from main.tenants import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = (
    [
        path("", views.HomeView.as_view(), name="home"),
        # path("add/", views.tenant_add, name="add_tenants"),
        path("list/", views.list_tenants, name="list_tenants"),
        path("list/manage/", views.tenants_manage, name="manage_tenants"),
        path("tenants", include("config.urls")),
        path("admin/", admin.site.urls),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
