from __future__ import unicode_literals
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


import json

from main.core.smpp import TelnetConnection, MTInterceptor


@login_required
def mtinterceptor_view(request):
    return render(request, "web/content/mtinterceptor.html")


@login_required
def mtinterceptor_view_manage(request):
    args, res_status, res_message = {}, 400, _("Sorry, Command does not matched.")
    tc, mtinterceptor = None, None
    if request.POST and request.is_ajax():
        s = request.POST.get("s")
        if s in ["list", "add", "edit", "delete"]:
            tc = TelnetConnection()
            mtinterceptor = MTInterceptor(telnet=tc.telnet)
        if tc and mtinterceptor:
            if s == "list":
                args = mtinterceptor.list()
                # print(f"args: {args}")
                res_status, res_message = 200, _("OK")
            elif s == "add":
                try:
                    mtinterceptor.create(
                        data=dict(
                            type=request.POST.get("type"),
                            order=request.POST.get("order"),
                            script=request.POST.get("script"),
                            filters=request.POST.getlist("filters"),
                        )
                    )
                    res_status, res_message = 200, _(
                        "MT Interceptor added successfully!"
                    )
                except Exception as e:
                    res_message = e
            elif s == "edit":
                try:
                    mtinterceptor.update(
                        order=request.POST.get("order"),
                        data=dict(
                            type=request.POST.get("type"),
                            order=request.POST.get("order"),
                            script=request.POST.get("script"),
                            filters=request.POST.getlist("filters"),
                        ),
                    )
                    res_status, res_message = 200, _(
                        "MT Interceptor updated successfully!"
                    )
                except Exception as e:
                    res_message = e
            elif s == "delete":
                args = mtinterceptor.destroy(order=request.POST.get("order"))
                res_status, res_message = 200, _("MT Interceptor deleted successfully!")
    if isinstance(args, dict):
        args["status"] = res_status
        args["message"] = str(res_message)
    else:
        res_status = 200
    return HttpResponse(
        json.dumps(args), status=res_status, content_type="application/json"
    )
