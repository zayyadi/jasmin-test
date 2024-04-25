import os
import requests
import json
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from main.core.smpp import Stats
from main.core.models.setting import Settings
from django.core.mail import send_mail

from main.web.views.content.user_stats import json_list


def send_email_notification(request, cid):
    subject = "Connector Status Notification"
    message = f"Connector with ID {cid} is in a stopped state. Please take action."
    all_query = Settings.objects.all()
    query = all_query.filter(cid=cid)
    from_email = os.getenv("MAIL_FROM")  # Replace with your email
    url = [obj.url for obj in query]

    # Extract and clean email addresses
    admin_email_list = []
    for obj in query:
        try:
            json_list(admin_email_list, obj.email_list)
            # print("DONE!!")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {obj.email_list}: {e}")

    # print(f"cleaned email: {admin_email_list}")

    for urls in url:
        try:
            response = requests.get(urls)
            # Process the response as needed
            print(f"Response from {urls}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            # Handle exceptions (e.g., connection error)
            print(f"Error with {urls}: {e}")

    send_mail(subject, message, from_email, admin_email_list)

    return JsonResponse({"message": "Email notification sent successfully"})


@login_required
def stats_view(request):
    return render(request, "web/content/stats.html")


@login_required
def stat_view_manage(request):
    args, res_status, res_message = {}, 400, _("Sorry, Command does not matched.")
    stats = None
    if request.GET and request.is_ajax():
        s = request.GET.get("s")
        if s in ["list", "smppc"]:
            stats = Stats(telnet=request.telnet)

        if stats:
            if s == "list":
                args = stats.list_s()
                for conn in args.get("stats", []):
                    disconnected_at = conn.get("disconnected_at", "ND")
                    bound_at = conn.get("bound_at", "ND")

                    if disconnected_at != "ND" and bound_at != "ND":
                        if disconnected_at > bound_at:
                            conn["status"] = "DOWN"
                        else:
                            conn["status"] = "BOUND"
                    elif disconnected_at == "ND" and bound_at != "ND":
                        conn["status"] = "BOUND"
                    elif disconnected_at != "ND" and bound_at == "ND":
                        conn["status"] = "UNBOUND"
                    else:
                        conn["status"] = "UNBOUND"
                res_status, res_message = 200, _("ok")

            elif s == "smppc":
                args = stats.list_smppc(cid=request.GET.get("cid"))
                res_status, res_message = 200, _("ok")

    if isinstance(args, dict):
        args["status"] = res_status
        args["message"] = str(res_message)
        # print(f"args: {args}")
    else:
        res_status = 200
        # print(f"args: s{args}")
    return HttpResponse(
        json.dumps(args), status=res_status, content_type="application/json"
    )
