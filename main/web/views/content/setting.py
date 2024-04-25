import json

from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from main.core.models.setting import Settings


@login_required
def settings(request):
    return render(request, "web/content/settings.html")


@login_required
def monitor_settings(request):
    return render(request, "web/content/monitor_settings.html")


@login_required
def settings_manage(request):
    try:
        args, res_status, res_message = {}, 400, _("Sorry, Command does not matched.")
        if request.POST and request.is_ajax():
            s = request.POST.get("s")
            if s in ["list", "add", "edit", "delete"]:
                if s == "list":
                    settings = Settings.objects.all()
                    args = [
                        {
                            "id": setting.id,
                            "cid": setting.cid,
                            "url": setting.url,
                            "email_list": [
                                email.strip("['']")
                                for email in setting.email_list.split(",")
                            ],
                        }
                        for setting in settings
                    ]
                    res_status, res_message = 200, _("OK")
                elif s == "add":
                    settings_instance = Settings.objects.create(
                        cid=request.POST.get("cid"),
                        url=request.POST.get("url"),
                        email_list=request.POST.get("email_list"),
                    )

                    # Convert the Settings instance to a dictionary
                    settings_dict = model_to_dict(settings_instance)

                    # Serialize the dictionary to JSON
                    args = json.dumps(settings_dict)

                    res_status, res_message = 200, _("Settings added successfully!")

                elif s == "edit":

                    setting_id = request.POST.get("id")
                    try:
                        # Try to get the existing Settings object
                        settings_instance = Settings.objects.get(id=setting_id)
                    except Settings.DoesNotExist:
                        # If not found, return a JsonResponse with an error message
                        return JsonResponse(
                            {"status": "error", "message": _("Settings not found!")},
                            status=404,
                        )

                    # Update the fields based on the provided data
                    settings_instance.cid = request.POST.get("cid", "")
                    settings_instance.url = request.POST.get("url", "")
                    settings_instance.email_list = request.POST.get("email_list", "")
                    settings_instance.save()

                    dicts = model_to_dict(settings_instance)
                    args = json.dumps(dicts)

                    res_status, res_message = 200, _("entry Updated successfully!")

                elif s == "delete":
                    args = get_object_or_404(Settings, id=request.POST.get("id"))
                    args.delete()
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": _("Entry Deleted successfully!"),
                        }
                    )

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
