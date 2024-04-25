from django.contrib import admin

from main.tenants.models import Domain, Client

# from timport Client, Domain


class DomainInline(admin.TabularInline):
    model = Domain


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [DomainInline]
    list_display = ("schema_name", "name")
