from collections import OrderedDict

from django.conf import settings

from django.utils.datastructures import MultiValueDictKeyError
from main.core.tools import set_ikeys, split_cols
from main.core.exceptions import (
    JasminError,
    # JasminSyntaxError,
    MissingKeyError,
    UnknownError,
    ObjectNotFoundError,
)

import logging
import random

from main.core.utils.boolean import is_int  # noqa: E401

STANDARD_PROMPT = settings.STANDARD_PROMPT
INTERACTIVE_PROMPT = settings.INTERACTIVE_PROMPT

logger = logging.getLogger(__name__)


class MTInterceptor:
    lookup_field = "order"

    def __init__(self, telnet):
        self.telnet = telnet

    def _list(self):
        self.telnet.sendline("mtinterceptor -l")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        mtinterceptor_result = (
            str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        )

        if len(mtinterceptor_result) < 3:
            return {
                "mtinterceptor": [],
            }

        mtinterceptor_results = [
            l.replace(", ", ",").replace("(!)", "")
            for l in mtinterceptor_result[2:-2]  # noqa: E741
            if l
        ]

        intercept = split_cols(mtinterceptor_results)

        return {
            "mtinterceptor": [
                {
                    "order": r[0].strip().lstrip("#"),
                    "type": r[1],
                    "script": r[3:],
                    "filters": r[-2:],
                }
                for r in intercept
            ]
        }

    def list(self):
        "List MT interceptor. No parameters"
        return self._list()

    def get_router(self, order):
        "Return data for one mtinterceptor as Python dict"
        intercept = self._list()["mtinterceptor"]
        try:
            return {
                "mtinterceptor": next(
                    m for m in intercept if m["order"] == order
                )  # , None
            }
        except StopIteration:
            raise ObjectNotFoundError("No mtinterceptor with order: %s" % order)

    def flush(self):
        "Flush entire Interceptor table"
        self.telnet.sendline("mtinterceptor -f")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        self.telnet.sendline("persist")
        self.telnet.expect(r".*" + STANDARD_PROMPT)
        return {"mtinterceptor": []}

    def retrieve(self, order):
        "Details for one MORouter by order (integer)"
        return self.get_router(order)

    def create(self, data):
        try:
            rtype, order = data.get("type"), data.get("order")
            self.retrieve(order)
        except Exception:
            pass

        rtype = rtype.lower()
        self.telnet.sendline("mtinterceptor -a")
        self.telnet.expect(r"Adding a new MT Interceptor(.+)\n" + INTERACTIVE_PROMPT)
        ikeys = OrderedDict({"type": rtype})

        if rtype != "defaultinterceptor":
            try:
                filters = data["filters"] or ""
                script = data.get("script") or ""
                filters = filters
                if not filters:
                    raise ValueError(
                        "At least one filter is required for %s router" % rtype
                    )
                ikeys["filters"] = ";".join(filters)
                ikeys["script"] = script
            except MultiValueDictKeyError as e:
                logger.error(f"Missing key error while handling filters: {e}")
                raise MissingKeyError("%s router requires filters" % rtype)

                # raise MissingKeyError("%s Interceptor requires filters" % rtype)

        ikeys["order"] = order if is_int(order) else str(random.randrange(1, 99))
        script = data.get("script") or ""
        ikeys["script"] = script
        set_ikeys(self.telnet, ikeys)
        self.telnet.sendline("persist")
        self.telnet.expect(r".*" + STANDARD_PROMPT)
        return {"mtinterceptor": self.get_router(order)}

    def simple_mtinterceptor_action(self, action, order, return_mointercept=True):
        self.telnet.sendline("mtinterceptor -%s %s" % (action, order))
        matched_index = self.telnet.expect(
            [
                r".+Successfully(.+)" + STANDARD_PROMPT,
                r".+Unknown mointerceptor: (.+)" + STANDARD_PROMPT,
                r".+(.*)" + STANDARD_PROMPT,
            ]
        )
        if matched_index == 0:
            self.telnet.sendline("persist")
            if return_mointercept:
                self.telnet.expect(r".*" + STANDARD_PROMPT)
                return {"morouter": self.get_router(fid)}
            else:
                return {"order": self.get_router(order)}
        elif matched_index == 1:
            raise UnknownError(detail="No Interceptor:" + order)
        else:
            raise JasminError(self.telnet.match.group(1))

    def update(self, order, data):
        get_order = self.get_router(order)
        if not get_order:
            raise UnknownError(detail="No MTInterceptor:" + order)

        try:
            rtype, order = data.get("type"), order
            self.retrieve(order)
        except Exception:
            pass

        rtype = rtype.lower()
        self.telnet.sendline("mtinterceptor -a")
        self.telnet.expect(r"Adding a new MT Interceptor(.+)\n" + INTERACTIVE_PROMPT)
        ikeys = OrderedDict({"type": rtype})

        if rtype != "defaultinterceptor":
            try:
                filters = data["filters"] or ""
                script = data.get("script") or ""
                filters = filters
                if not filters:
                    raise ValueError(
                        "At least one filter is required for %s Interceptor" % rtype
                    )
                ikeys["filters"] = ";".join(filters)
                ikeys["script"] = script
            except MultiValueDictKeyError as e:
                logger.error(f"Missing key error while handling filters: {e}")
                raise MissingKeyError("%s router requires filters" % rtype)

                # raise MissingKeyError("%s Interceptor requires filters" % rtype)

        ikeys["order"] = order if is_int(order) else str(random.randrange(1, 99))
        script = data.get("script") or ""
        ikeys["script"] = script
        set_ikeys(self.telnet, ikeys)
        self.telnet.sendline("persist")
        self.telnet.expect(r".*" + STANDARD_PROMPT)
        return {"mtinterceptor": self.get_router(order)}

    def destroy(self, order):
        """Delete a mtinterceptor. One parameter required, the router identifier (a string)

        HTTP codes indicate result as follows

        - 200: successful deletion
        - 404: nonexistent router
        - 400: other error
        """
        return self.simple_mtinterceptor_action("r", order, return_mointercept=False)


# DefaultInterceptor, StaticMTInterceptor
