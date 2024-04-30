import json
from django.conf import settings
from django.db import utils

from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect, render

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django_tenants.utils import remove_www
from main.tenants.models import Client, Domain
from django.contrib.auth.decorators import login_required


class HomeView(TemplateView):
    template_name = "tenants/index_public.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hostname_without_port = remove_www(self.request.get_host().split(":")[0])

        try:
            Client.objects.get(schema_name="public")
        except utils.DatabaseError:
            context["need_sync"] = True
            context["shared_apps"] = settings.SHARED_APPS
            context["tenants_list"] = []
            return context
        except Client.DoesNotExist:
            context["no_public_tenant"] = True
            context["hostname"] = hostname_without_port

        # Filter out the public tenant from the list
        context["tenants_list"] = Client.objects.exclude(schema_name="public")
        context["domain_list"] = Domain.objects.all()
        context["server_port"] = self.request.get_port()

        return context


def list_tenants(request):
    return render(request, "tenants/list_tenants.html")


def tenants_manage(request):
    try:
        args, res_status, res_message = {}, 400, _("Sorry, Command does not matched.")
        if request.POST and request.is_ajax():
            s = request.POST.get("s")
            if s in ["list", "add"]:
                if s == "list":
                    tenants = Client.objects.exclude(schema_name="public")
                    # print(tenants)
                    # domain = Domain.objects.all()

                    args = [
                        {
                            "id": tenant.id,
                            "name": tenant.name,
                            "jasmin_host": tenant.jasmin_host,
                            "jasmin_port": tenant.jasmin_port,
                            # "domain_name": domain.domain,
                        }
                        for tenant in tenants
                    ]
                    res_status, res_message = 200, _("OK")
                elif s == "add":
                    tenant_instance = Client.objects.create(
                        schema_name=request.POST.get("schema_name"),
                        name=request.POST.get("name"),
                        jasmin_host=request.POST.get("jasmin_host"),
                        jasmin_port=request.POST.get("jasmin_port"),
                        jasmin_username=request.POST.get("jasmin_username"),
                        jasmin_password=request.POST.get("jasmin_password"),
                        description=request.POST.get("description"),
                    )

                    domain_instance = Domain.objects.create(
                        domain=request.POST.get("domain"), tenant=tenant_instance
                    )

                    tenant_dict = model_to_dict(tenant_instance)
                    domain_dict = model_to_dict(domain_instance)

                    args = json.dumps([tenant_dict, domain_dict])
                    res_status, res_message = 200, _("Settings added successfully!")

        if isinstance(args, dict):
            args["status"] = res_status
            args["message"] = str(res_message)
            # print(f"args: {args}")
        else:
            res_status = 200
            # print(f"args: {args}")

        return HttpResponse(
            json.dumps(args), status=res_status, content_type="application/json"
        )
    except Exception as e:
        raise e


# @login_required
# def tenant_add(request):
#     return render(request, "tenants/add_tenants.html")


# @login_required
# def add_tenant(request):
#     if request.method == "POST":
#         schema_name = request.POST["schema_name"]
#         name = request.POST["name"]
#         jasmin_host = request.POST["jasmin_host"]
#         jasmin_port = request.POST["jasmin_port"]
#         jasmin_username = request.POST["jasmin_username"]
#         jasmin_password = request.POST["jasmin_password"]
#         description = request.POST["description"]
#         domain = request.POST["domain"]

#         tenant = Client(
#             schema_name=schema_name,
#             name=name,
#             jasmin_host=jasmin_host,
#             jasmin_port=jasmin_port,
#             jasmin_username=jasmin_username,
#             jasmin_password=jasmin_password,
#             description=description,
#         )
#         tenant.save()

#         domain = Domain(domain=domain, tenant=tenant)
#         domain.save()

#         return redirect("home")

#     return render(request, "tenants/index_public.html")
