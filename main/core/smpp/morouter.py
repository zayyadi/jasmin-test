from collections import OrderedDict

from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError

from main.core.utils import is_int
from main.core.tools import set_ikeys, split_cols
from main.core.exceptions import (
    JasminError,
    UnknownError,
    MissingKeyError,
    MutipleValuesRequiredKeyError,
    ObjectNotFoundError,
)

import logging, random  # noqa: E401

STANDARD_PROMPT = settings.STANDARD_PROMPT
INTERACTIVE_PROMPT = settings.INTERACTIVE_PROMPT

logger = logging.getLogger(__name__)


class MORouter(object):
    "MORouter for managing MO Routes"
    lookup_field = "order"

    def __init__(self, telnet):
        self.telnet = telnet

    def _list(self):
        "List MO router as python dict"
        self.telnet.sendline("morouter -l")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        morouter_result = (
            str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        )

        self.telnet.sendline("user -l")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        user_result = (
            str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        )

        if len(morouter_result) < 3:
            result = {"morouters": [], "users": []}  # noqa: F841
        else:
            morouter_results = [
                l.replace(", ", ",").replace("(!)", "")
                for l in morouter_result[2:-2]  # noqa: E741
                if l
            ]
            # print(morouter_results)
            user_results = [
                l.replace(", ", ",").replace("(!)", "")
                for l in user_result[2:-2]  # noqa: E741
                if l  # noqa: E741
            ]

            morouters = split_cols(morouter_results)
            users = split_cols(user_results)

        # Create a list of users inside the 'morouters' dictionary
        return {
            "morouters": [
                {
                    "order": r[0].strip().lstrip("#"),
                    "type": r[1],
                    "connectors": [c.strip() for c in r[2].split(",")],
                    "filters": [c.strip() for c in " ".join(r[3:]).split(",")],
                    "user": [users[0][2].lstrip().strip("#")],
                    # if len(r) > 3
                    # else [],
                    # "users": users,  # Include the user data here
                }
                for r in morouters
            ]
        }

    # def format_filter(self):
    #     self.telnet.sendline("filter -l")
    #     self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
    #     filter_result = (
    #         str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
    #     )
    #     filter_results = [
    #             l.replace(", ", ",").replace("(!)", "")
    #             for l in filter_result[2:-2]  # noqa: E741
    #             if l  # noqa: E741
    #         ]
    #     filters = split_cols(filter_results)

    #     return {
    #         "fid": [filters[0][0].lstrip().strip("#")],
    #     }
    def list(self):
        "List MO routers. No parameters"
        # print(f"morouters: {self._list()}")
        return self._list()

    def get_router(self, order):
        "Return data for one morouter as Python dict"
        morouters = self._list()["morouters"]
        try:
            return {
                "morouter": next(m for m in morouters if m["order"] == order)  # , None
            }
        except StopIteration:
            raise ObjectNotFoundError("No MoROuter with order: %s" % order)

    def retrieve(self, order):
        "Details for one MORouter by order (integer)"
        return self.get_router(order)

    # methods=['delete']
    def flush(self):
        "Flush entire routing table"
        self.telnet.sendline("morouter -f")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        self.telnet.sendline("persist")
        self.telnet.expect(r".*" + STANDARD_PROMPT)
        return {"morouters": []}

    def create(self, data: dict):

        try:
            rtype, order = data.get("type"), data.get("order")
            self.retrieve(order)
        except Exception:  # noqa
            pass
        rtype = rtype.lower()
        self.telnet.sendline("morouter -a")
        self.telnet.expect(r"Adding a new MO Route(.+)\n" + INTERACTIVE_PROMPT)
        ikeys = OrderedDict({"type": rtype})

        if rtype != "defaultroute":
            try:
                filters = data["filters"] or ""
                filter_list = []
                if filters:
                    filter_list.append(filters)
                # filters2 = [filters2]
                # print(f"second filters: {filter_list}")
                if not filters:
                    raise ValueError(
                        "At least one filter is required for %s router" % rtype
                    )
                ikeys["filters"] = ";".join(filters)
                # ikeys["filters2"] = ";".join(filters2)
            except MultiValueDictKeyError:
                raise MissingKeyError("%s router requires filters" % rtype)

        ikeys["order"] = order if is_int(order) else str(random.randrange(1, 99))
        smppconnectors = data.get("smppconnectors") or ""
        httpconnectors = data.get("httpconnectors") or ""
        userconnectors = data.get("userconnectors") or ""
        connectors = (
            ["smpps(%s)" % c.strip() for c in smppconnectors.split(",") if c.strip()]
            + ["smpps(%s)" % c.strip() for c in userconnectors.split(",") if c.strip()]
            + ["http(%s)" % c for c in httpconnectors.split(",") if c.strip()]
        )
        if rtype == "randomroundrobinmoroute":
            if len(connectors) < 2:
                raise MutipleValuesRequiredKeyError(
                    "Round Robin route requires at least two connectors"
                )
            ikeys["connectors"] = ";".join(connectors)
        elif rtype == "failovermoroute":
            if len(connectors) < 2:
                raise MutipleValuesRequiredKeyError(
                    "FailOver route requires at least two connectors"
                )
            ikeys["connectors"] = ";".join(connectors)
        else:
            if len(connectors) != 1:
                raise MissingKeyError("One and only one connector required")
            ikeys["connector"] = connectors[0]
        set_ikeys(self.telnet, ikeys)
        self.telnet.sendline("persist")
        self.telnet.expect(r".*" + STANDARD_PROMPT)
        return {"morouter": self.get_router(order)}

    def simple_morouter_action(self, action, order, return_moroute=True):
        self.telnet.sendline("morouter -%s %s" % (action, order))
        matched_index = self.telnet.expect(
            [
                r".+Successfully(.+)" + STANDARD_PROMPT,
                r".+Unknown MO Route: (.+)" + STANDARD_PROMPT,
                r".+(.*)" + STANDARD_PROMPT,
            ]
        )

        if matched_index == 0:
            self.telnet.sendline("persist")
            if return_moroute:
                self.telnet.expect(r".*" + STANDARD_PROMPT)
                return {"morouter": self.get_router(fid)}
            else:
                return {"order": order}
        elif matched_index == 1:
            raise UnknownError(detail="No router:" + order)
        else:
            raise JasminError(self.telnet.match.group(1))

    def update(self, order, data):
        get_order = self.get_router(order)
        if not get_order:
            raise UnknownError(detail="No Router:" + order)

        try:
            rtype, order = data.get("type"), order
            self.retrieve(order)
        except Exception:  # noqa
            pass
        # else:
        #     raise MissingKeyError("MO route already exists")
        # raise MissingKeyError('Missing parameter: type or order required')
        rtype = rtype.lower()
        self.telnet.sendline("morouter -a")
        self.telnet.expect(r"Adding a new MO Route(.+)\n" + INTERACTIVE_PROMPT)
        ikeys = OrderedDict({"type": rtype})

        if rtype != "defaultroute":
            try:
                filters = data["filters"] or ""
                filter_list = []
                if filters:
                    filter_list.append(filters)
                if not filters:
                    raise ValueError(
                        "At least one filter is required for %s router" % rtype
                    )
                ikeys["filters"] = ";".join(filters)
            except MultiValueDictKeyError:
                raise MissingKeyError("%s router requires filters" % rtype)
            # ikeys["filters"] = ";".join(filters)
        ikeys["order"] = order if is_int(order) else str(random.randrange(1, 99))
        smppconnectors = data.get("smppconnectors") or ""
        httpconnectors = data.get("httpconnectors") or ""
        userconnectors = data.get("userconnectors") or ""
        connectors = (
            ["smpps(%s)" % c.strip() for c in smppconnectors.split(",") if c.strip()]
            + ["smpps(%s)" % c.strip() for c in userconnectors.split(",") if c.strip()]
            + ["http(%s)" % c for c in httpconnectors.split(",") if c.strip()]
        )
        if rtype == "randomroundrobinmoroute":
            if len(connectors) < 2:
                raise MutipleValuesRequiredKeyError(
                    "Round Robin route requires at least two connectors"
                )
            ikeys["connectors"] = ";".join(connectors)
        elif rtype == "failovermoroute":
            if len(connectors) < 2:
                raise MutipleValuesRequiredKeyError(
                    "FailOver route requires at least two connectors"
                )
            ikeys["connectors"] = ";".join(connectors)
        else:
            if len(connectors) != 1:
                raise MissingKeyError("One and only one connector required")
            ikeys["connector"] = connectors[0]
        set_ikeys(self.telnet, ikeys)
        self.telnet.sendline("persist")
        self.telnet.expect(r".*" + STANDARD_PROMPT)
        return {"morouter": self.get_router(order)}

    def destroy(self, order):
        """Delete a morouter. One parameter required, the router identifier (a string)

        HTTP codes indicate result as follows

        - 200: successful deletion
        - 404: nonexistent router
        - 400: other error
        """
        return self.simple_morouter_action("r", order, return_moroute=False)
