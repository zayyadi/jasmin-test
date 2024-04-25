from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

# from django.utils.functional import SimpleLazyObject
from django.http import Http404

from django_tenants.middleware import TenantMainMiddleware
from django_tenants.utils import remove_www_and_dev, get_public_schema_urlconf

# from main..tenants import Tenant

from .exceptions import (
    TelnetUnexpectedResponse,
    TelnetConnectionTimeout,
    TelnetLoginFailed,
)
from .utils import get_user_agent, get_client_ip, LazyEncoder
from .models import ActivityLog

import logging
import pexpect, sys, time, json

# from main.tenants.models import Client
from django_tenants.utils import get_tenant

logger = logging.getLogger(__name__)


class AjaxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def is_ajax(self):  # noqa
            return request.headers.get("x-requested-with") == "XMLHttpRequest"

        request.is_ajax = is_ajax.__get__(request)
        response = self.get_response(request)
        return response


# class TelnetConnectionMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         """Add a telnet connection to all request paths that start with /api/
#         assuming we only need to connect for these means we avoid unecessary
#         overhead on any other functionality we add, and keeps URL path clear
#         for it.
#         """
#         # if not request.path.startswith('/api/'):
#         #     return None
#         if not request.path.endswith("/manage/"):
#             return None
#         try:
#             # telnet = pexpect.spawn(
#             #     "telnet %s %s" %
#             #     (settings.TELNET_HOST, settings.TELNET_PORT),
#             #     timeout=settings.TELNET_TIMEOUT,
#             # )
#             telnet = pexpect.spawn(
#                 "telnet",
#                 [settings.TELNET_HOST, str(settings.TELNET_PORT)],
#                 timeout=settings.TELNET_TIMEOUT,
#             )
#             # telnet.logfile_read = sys.stdout
#             telnet.expect(":")
#             telnet.sendline(settings.TELNET_USERNAME)
#             telnet.expect(":")
#             telnet.sendline(settings.TELNET_PW)
#             # telnet.send("\r\n")
#         except pexpect.EOF:
#             logger.error("TelnetUnexpectedResponse")
#             # raise TelnetUnexpectedResponse
#         except pexpect.TIMEOUT:
#             logger.error("TelnetConnectionTimeout")
#             # raise TelnetConnectionTimeout
#         except AttributeError as e:
#             logger.error(
#                 f"The Jasmin SMS Gateway not configured properly, the error: \n {e}"
#             )

#         try:
#             telnet.expect_exact(settings.STANDARD_PROMPT)
#         except pexpect.EOF:
#             logger.error("TelnetLoginFailed")
#             # raise TelnetLoginFailed
#         except UnboundLocalError as e:
#             logger.error(f"Cannot connect through Telnet, the error: \n {e}")
#         # else:
#         request.telnet = telnet
#         return None


class TelnetConnectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Add a telnet connection to all request paths that start with /api/
        assuming we only need to connect for these means we avoid unecessary
        overhead on any other functionality we add, and keeps URL path clear
        for it.
        """
        if not request.path.endswith("/manage/"):
            return None

        # Get the current tenant and its Telnet configuration
        current_tenant = get_tenant(request)
        if current_tenant:
            telnet_host = current_tenant.jasmin_host
            telnet_port = current_tenant.jasmin_port
            telnet_username = current_tenant.jasmin_username
            telnet_password = current_tenant.jasmin_password
        else:
            # Handle the case where the tenant does not exist
            return None

        try:
            telnet = pexpect.spawn(
                "telnet",
                [telnet_host, str(telnet_port)],
                timeout=settings.TELNET_TIMEOUT,
            )
            telnet.expect(":")
            telnet.sendline(telnet_username)
            telnet.expect(":")
            telnet.sendline(telnet_password)
        except pexpect.EOF:
            logger.error("TelnetUnexpectedResponse")
        except pexpect.TIMEOUT:
            logger.error("TelnetConnectionTimeout")
        except AttributeError as e:
            logger.error(
                f"The Jasmin SMS Gateway not configured properly, the error: \n {e}"
            )

        try:
            telnet.expect_exact(settings.STANDARD_PROMPT)
        except pexpect.EOF:
            logger.error("TelnetLoginFailed")
        except UnboundLocalError as e:
            logger.error(f"Cannot connect through Telnet, the error: \n {e}")

        request.telnet = telnet
        return None

    def process_response(self, request, response):
        "Make sure telnet connection is closed when unleashing response back to client"
        if hasattr(request, "telnet"):
            try:
                request.telnet.sendline("quit")
            except pexpect.ExceptionPexpect:
                request.telnet.kill(9)
        return response


class UserAgentMiddleware(object):

    def __init__(self, get_response=None):
        if get_response is not None:
            self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        user_agent = get_user_agent(request)
        if (
            request.user.is_authenticated
            and request.is_ajax()
            and request.path.endswith("/manage/")
        ):

            def clean_params(params):
                params = params.copy()
                if "csrfmiddlewaretoken" in params:
                    params.pop("csrfmiddlewaretoken", None)
                if "s" in params:
                    params.pop("s", None)
                return params

            if request.POST.get("s") != "list":
                ActivityLog.objects.create(
                    user=request.user,
                    service=request.POST.get("s", "unknown"),
                    method=request.method,
                    params=json.dumps(
                        clean_params(request.POST or request.GET or {}), cls=LazyEncoder
                    ),
                    path=request.path,
                    ip=get_client_ip(request),
                    user_agent=json.dumps(user_agent.__dict__ or {}, cls=LazyEncoder),
                )


class TenantTutorialMiddleware(TenantMainMiddleware):
    def no_tenant_found(self, request, hostname):
        hostname_without_port = remove_www_and_dev(request.get_host().split(":")[0])
        if hostname_without_port in ("127.0.0.1", "localhost"):
            request.urlconf = get_public_schema_urlconf()
            return
        else:
            raise Http404
