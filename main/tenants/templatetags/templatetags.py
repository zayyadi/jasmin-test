from django import template
from django_tenants.utils import get_tenant_model


register = template.Library()


@register.filter
def first_domain(domain_list, schema_name):
    tenant_model = get_tenant_model()
    try:
        tenant = tenant_model.objects.get(schema_name=schema_name)
        return domain_list.filter(tenant=tenant).first()
    except tenant_model.DoesNotExist:
        return None
