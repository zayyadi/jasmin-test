import json

from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from main.core.models.setting import UserModel


@login_required
def user_settings(request):
    return render(request, "web/content/user_setting.html")


@login_required
def user_manage(request):
    try:
        args, res_status, res_message = {}, 400, _("Sorry, Command does not matched.")
        if request.POST and request.is_ajax():
            s = request.POST.get("s")
            if s in ["list", "add", "edit", "delete"]:
                if s == "list":
                    settings = UserModel.objects.all()
                    args = [
                        {
                            "id": setting.id,
                            "uid": setting.uid,
                            "url": setting.url,
                            "designated_bound": setting.designated_bound,
                            "email_list": [
                                email.strip("['']")
                                for email in setting.email_list.split(",")
                            ],
                        }
                        for setting in settings
                    ]
                    res_status, res_message = 200, _("OK")
                elif s == "add":
                    settings_instance = UserModel.objects.create(
                        uid=request.POST.get("uid"),
                        url=request.POST.get("url"),
                        designated_bound=request.POST.get("designated_bound"),
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
                        updates = UserModel.objects.get(id=setting_id)
                    except UserModel.DoesNotExist:
                        # If not found, return a JsonResponse with an error message
                        return JsonResponse(
                            {"status": "error", "message": _("Settings not found!")},
                            status=404,
                        )

                    updates.uid = request.POST.get("uid", "")
                    updates.url = request.POST.get("url", "")
                    updates.designated_bound = request.POST.get("designated_bound")
                    updates.email_list = request.POST.get("email_list", "")

                    updates.save()

                    dicts = model_to_dict(updates)
                    args = json.dumps(dicts)

                    res_status, res_message = 200, _("entry Updated successfully!")

                elif s == "delete":
                    args = get_object_or_404(UserModel, id=request.POST.get("id"))
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
