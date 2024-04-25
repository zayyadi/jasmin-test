from django.conf import settings
from main.core.exceptions import ObjectNotFoundError

# from django.conf import settings
from main.core.tools import split_cols

import logging


STANDARD_PROMPT = settings.STANDARD_PROMPT
INTERACTIVE_PROMPT = settings.INTERACTIVE_PROMPT

logger = logging.getLogger(__name__)


class Stats:
    lookup_field = "cid"

    def __init__(self, telnet):
        self.telnet = telnet

    def get_smppccm(self, cid, silent=False):
        # Some of this could be abstracted out - similar pattern in users.py
        self.telnet.sendline("smppccm -s " + cid)
        matched_index = self.telnet.expect(
            [
                r".+Unknown connector:.*" + STANDARD_PROMPT,
                r".+Usage:.*" + STANDARD_PROMPT,
                r"(.+)\n" + STANDARD_PROMPT,
            ]
        )
        if matched_index != 2:
            if silent:
                return
            else:
                raise ObjectNotFoundError("Unknown connector: %s" % cid)
        result = self.telnet.match.group(1)
        smppccm = {}
        for line in result.splitlines():
            d = [x for x in line.split() if x]
            if len(d) == 2:
                smppccm[str(d[0], "utf-8")] = str(d[1], "utf-8")
        return smppccm

    def list_smpp(self):
        self.telnet.sendline("stats --smppcs")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        res = str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        # print(res)
        lines = res
        if not lines:
            return []
        # if len(res) < 3:
        # return []
        return split_cols(res[2:-2])

    def list_s(self):
        connectors = []
        connector_list = self.list_smpp()
        # print(f"connector: {connector_list}")
        for row in connector_list:
            connector = {}
            n = len(row)
            # print(f"n: {n}")
            if n == 11:
                connector.update(
                    cid=row[0][1:],
                    connected_at=row[1] + " " + row[2],
                    bound_at=row[3] + " " + row[4],
                    disconnected_at=row[5] + " " + row[6],
                    submits=row[7],
                    delivers=row[8],
                    qos_err=row[9],
                    other_err=row[10],
                )
            elif n == 10:
                connector.update(
                    cid=row[0][1:],
                    connected_at=row[1] + " " + row[2],
                    bound_at=row[3] if row[3] == "ND" else row[3] + " " + row[4],
                    disconnected_at=row[4] + " " + row[5] if row[3] == "ND" else row[5],
                    submits=row[6],
                    delivers=row[7],
                    qos_err=row[8],
                    other_err=row[9],
                )

            elif n == 8:
                connector.update(
                    cid=row[0][1:],
                    connected_at=row[1],
                    bound_at=row[2],
                    disconnected_at=row[3],
                    submits=row[4],
                    delivers=row[5],
                    qos_err=row[6],
                    other_err=row[7],
                )
            connectors.append(connector)
            # if n == 11:
            #     connector.update(
            #         cid=row[0][1:],
            #         connected_at=row[1] + " " + row[2],
            #         bound_at=row[3] + " " + row[4],
            #         disconnected_at=row[5] + " " + row[6],
            #         submits=row[7],
            #         delivers=row[8],
            #         qos_err=row[9],
            #         other_err=row[10],
            #     )
            # elif n == 10:
            #     connector.update(
            #         cid=row[0][1:],
            #         connected_at=row[1] + " " + row[2],
            #         bound_at=row[3],
            #         disconnected_at=row[4] + " " + row[5],
            #         submits=row[6],
            #         delivers=row[7],
            #         qos_err=row[8],
            #         other_err=row[9],
            #     )
            # elif n == 8:
            #     connector.update(
            #         cid=row[0][1:],
            #         connected_at=row[1],
            #         bound_at=row[2],
            #         disconnected_at=row[3],
            #         submits=row[4],
            #         delivers=row[5],
            #         qos_err=row[6],
            #         other_err=row[7],
            #     )
            # connectors.append(connector)
            # # print(f"connectors: {connectors}")
        return dict(stats=connectors)
        # return {
        #     "stats": [
        #         {
        #             "cid": r[0].strip().lstrip("#"),
        #             "connected_at": [c.strip() for c in " ".join(r[1:2]).split(",")],
        #             "bound_at": r[3].strip(),
        #             "disconnected_at": [c.strip() for c in " ".join(r[4:5]).split(",")],
        #             "submits": r[6].strip(),
        #             "delivers": r[7].strip(),
        #             "qos_err": r[8].strip(),
        #             "other_err": r[9].strip(),
        #         }
        #         for r in connector_list
        #     ]
        # }

    def list_smppc(self, cid):
        self.telnet.sendline(f"stats --smppc {cid}")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        res = str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        # print(f"resuls: {res}")
        if len(res) < 3:
            return []
        connector_detail = split_cols(res[2:-2])

        return {
            "smppc": [
                {
                    "item": r[0].strip().lstrip("#"),
                    "value": "" if r[1:] is None or r[1:] == "" else r[1:],
                }
                for r in connector_detail
            ]
        }


class SMPPSERVERStat(object):
    lookup_field = "cid"

    def __init__(self, telnet):
        self.telnet = telnet

    def list_smpp_server(self):
        self.telnet.sendline("stats --smppsapi")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        res = str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        # print(f"resuls: {res}")
        if len(res) < 3:
            return []
        connector_detail = split_cols(res[2:-2])

        return {
            "smppsapi": [
                {
                    "item": r[0].strip().lstrip("#"),
                    "value": r[1],
                }
                for r in connector_detail
            ]
        }


class HTTPStat(object):
    def __init__(self, telnet):
        self.telnet = telnet

    def list_http_server(self):
        self.telnet.sendline("stats --httpapi")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        res = str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        # print(f"resuls: {res}")
        if len(res) < 3:
            return []
        connector_detail = split_cols(res[2:-2])
        # print(f"connector details: {connector_detail}")

        return {
            "httpapi": [
                {
                    "item": r[0].strip().lstrip("#"),
                    "value": "" if r[1] is None or r[1] == "" else r[1],
                }
                for r in connector_detail
            ]
        }


class UserStat(object):
    lookup_field = "uid"

    def __init__(self, telnet):
        self.telnet = telnet

    def list_users(self):
        self.telnet.sendline("stats --users")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        res = str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        # print(res)
        if not res:
            return []
        return split_cols(res[2:-2])

    def list_u(self):
        users = []
        user_list = self.list_users()
        # print(f"connector: {user_list}")
        for row in user_list:
            n = len(row)
            # print(f"n == {n}")
            user = {}
            if n == 6:
                if row[1] == "0":  # must be http binds
                    user.update(
                        uid=row[0][1:],
                        smpp_bound_conn=row[1],
                        smpp_la=row[2] if row[2] == "ND" else row[2] + " " + row[3],
                        http_req_counter=row[3] if row[2] == "ND" else row[4],
                        http_la=row[4] + " " + row[5] if row[3] == "ND" else row[5],
                    )
                else:
                    user.update(
                        uid=row[0][1:],
                        smpp_bound_conn=row[1],
                        smpp_la=row[2] + " " + row[3],
                        http_req_counter=row[4],
                        http_la=row[5],
                    )
            elif n == 7:  # both http and smpp activity
                user.update(
                    uid=row[0][1:],
                    smpp_bound_conn=row[1],
                    smpp_la=row[2] + " " + row[3],
                    http_req_counter=row[4],
                    http_la=row[5] + " " + row[6],
                )
            else:
                user.update(
                    uid=row[0][1:],
                    smpp_bound_conn=row[1],
                    smpp_la=row[2],
                    http_req_counter=row[3],
                    http_la=row[4],
                )
            users.append(user)
        return dict(users=users)
        # return {
        #     "users": [
        #         {
        #             "uid": r[0].strip().lstrip("#"),
        #             "smpp_bound_conn": r[1].strip(),
        #             "smpp_la": [c.strip() for c in " ".join(r[2:3]).split(",")],
        #             "http_req_counter": r[4].strip(),
        #             "http_la": [c.strip() for c in " ".join(r[5]).split(",")],
        #         }
        #         for r in user_list
        #     ]
        # }

    def list_user(self, uid):
        self.telnet.sendline(f"stats --user {uid}")
        self.telnet.expect([r"(.+)\n" + STANDARD_PROMPT])
        res = str(self.telnet.match.group(0)).strip().replace("\\r", "").split("\\n")
        # print(f"resuls: {res}")
        if len(res) < 3:
            return []
        connector_detail = split_cols(res[2:-2])

        return {
            "user": [
                {
                    "item": r[0].strip().lstrip("#"),
                    "types": [c.strip() for c in " ".join(r[1:2]).split(",")],
                    "value": [c.strip() for c in " ".join(r[3:]).split(",")],
                }
                for r in connector_detail
            ]
        }
