from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    jasmin_host = models.CharField(max_length=255)
    jasmin_port = models.IntegerField()
    jasmin_username = models.CharField(max_length=255)
    jasmin_password = models.CharField(max_length=255)
    description = models.TextField(max_length=200)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.schema_name

    def get_jasmin_config(self):
        return {
            "TELNET_HOST": self.jasmin_host,
            "TELNET_PORT": self.jasmin_port,
            "TELNET_USERNAME": self.jasmin_username,
            "TELNET_PW": self.jasmin_password,
        }


class Domain(DomainMixin):
    pass
