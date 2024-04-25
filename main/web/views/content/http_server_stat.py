import json
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from main.core.smpp import HTTPStat


@login_required
def http_stats_view(request):
    return render(request, "web/content/http_stats.html")


@login_required
def http_stat_view_manage(request):
    args, res_status, res_message = {}, 400, _("Sorry, Command does not matched.")
    stats = None
    if request.GET and request.is_ajax():
        s = request.GET.get("s")
        if s in ["list"]:
            stats = HTTPStat(telnet=request.telnet)

        if stats:
            if s == "list":
                args = stats.list_http_server()
                res_status, res_message = 200, _("ok")

    if isinstance(args, dict):
        args["status"] = res_status
        args["message"] = str(res_message)
    else:
        res_status = 200
    return HttpResponse(
        json.dumps(args), status=res_status, content_type="application/json"
    )
