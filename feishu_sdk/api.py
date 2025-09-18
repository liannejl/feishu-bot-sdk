import os
import logging
import requests
from typing import Optional

# const
TENANT_ACCESS_TOKEN_URI = "/open-apis/auth/v3/tenant_access_token/internal"
MESSAGE_URI = "/open-apis/im/v1/messages"


class MessageApiClient(object):
    def __init__(self, app_id: str, app_secret: str, lark_host: str):
        self._app_id = app_id
        self._app_secret = app_secret
        self._lark_host = lark_host
        self._tenant_access_token = ""

    @classmethod
    def from_env(cls, lark_host: str, app_id_env: str = "APP_ID", app_secret_env: str = "APP_SECRET"):
        """Create client from environment variables"""
        app_id = os.getenv(app_id_env)
        app_secret = os.getenv(app_secret_env)
        if not app_id or not app_secret:
            raise ValueError(f"Environment variables {app_id_env} and {app_secret_env} must be set")
        return cls(app_id, app_secret, lark_host)

    @property
    def tenant_access_token(self):
        return self._tenant_access_token

    def send_text_with_open_id(self, open_id: str, content: str):
        self.send("open_id", open_id, "text", content)

    def send_card_with_open_id(self, open_id: str, content: str):
        return self.send("open_id", open_id, "interactive", content)

    def send_update_message_card(self, message_id: str, updated_card: str):
        # Updates message card that was sent previously
        # doc link: https://open.feishu.cn/document/server-docs/im-v1/message-card/patch?appId=cli_a6ac1c1b7df9900e
        self._authorize_tenant_access_token()
        url = "{}{}/{}".format(
            self._lark_host, MESSAGE_URI, message_id
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        req_body = {"content": updated_card}
        print("update message card url: ", url)
        print("update message card headers: ", headers)
        print("update message card body: ", req_body)
        resp = requests.patch(url, headers=headers, json=req_body)
        MessageApiClient._check_error_response(resp)


    def send(self, receive_id_type: str, receive_id: str, msg_type: str, content: str):
        # send message to user, implemented based on Feishu open api capability.
        # doc link: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        self._authorize_tenant_access_token()
        url = "{}{}?receive_id_type={}".format(
            self._lark_host, MESSAGE_URI, receive_id_type
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }

        req_body = {
            "receive_id": receive_id,
            "content": content,
            "msg_type": msg_type,
        }
        # print(f"Sending message request body w header {headers["Authorization"]}:\n", req_body)
        resp = requests.post(url=url, headers=headers, json=req_body)
        print(resp)
        MessageApiClient._check_error_response(resp)
        return resp.json()["data"]["message_id"]

    def _authorize_tenant_access_token(self):
        # get tenant_access_token and set, implemented based on Feishu open api capability.
        # doc link: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal
        url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
        req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
        print("Authorize tenant_access_token:\n", req_body)
        response = requests.post(url, req_body)
        MessageApiClient._check_error_response(response)
        self._tenant_access_token = response.json().get("tenant_access_token")

    @staticmethod
    def _check_error_response(resp):
        # check if the response contains error information
        if resp.status_code != 200:
            resp.raise_for_status()
        response_dict = resp.json()
        code = response_dict.get("code", -1)
        if code != 0:
            logging.error(response_dict)
            raise LarkException(code=code, msg=response_dict.get("msg"))


class LarkException(Exception):
    def __init__(self, code=0, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return "{}:{}".format(self.code, self.msg)

    __repr__ = __str__