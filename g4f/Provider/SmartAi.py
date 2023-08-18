import uuid

import requests

from ..typing import Any, CreateResult
from .base_provider import BaseProvider


class SmartAi(BaseProvider):
    url = "https://play.google.com/store/apps/details?id=com.chatgpt.ai.bot.open.assistant"
    supports_stream = False
    needs_auth = False
    supports_gpt_35_turbo = True
    working = True

    @staticmethod
    def create_completion(
        model: str,
        messages: list[dict[str, str]],
        stream: bool,
        **kwargs: Any,
    ) -> CreateResult:
        conversation = ""
        for message in messages:
            conversation += "%s: %s\n" % (message["role"], message["content"])
        conversation += "assistant: "
        headers = {
            'accept-encoding': 'gzip',
            'authorization': '6036b7974764a01f2e437d13f2d255275808929e91847ea77d8d8585da9e284c3dbe280685523e991bd9b3ebfce2884ba1fe329e534691dc8c9da29c55b620c9758d70c3635c2e97977b4c2c5e74dc3aec482a68ad5c994902782c08182c01c3890699ead860c391fc058b3d6320381dbc603ab02996482d17561f0bc9f984a6',
            'connection': 'Keep-Alive',
            'content-type': 'application/json; charset=UTF-8',
            'deviceid': 'C349DFBBA079AEBDDAF09A5E52A0506C5EFD90F6',
            'host': 'api.smartai.land',
            'user-agent': 'okhttp/3.12.0'
        }
        
        json_data = {
            "prompt": {
                "message": conversation
            },
            "reqId": "1692359983804",
            "templateId": "10000"
        }

        response = requests.post(
            "https://api.smartai.land/conversation",
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            response_json = response.json()
            if "code" in response_json and response_json["code"] == 200:
                yield response_json["data"]["response"]
            else:
                raise Exception(response_json["msg"])
        else:
            raise Exception(response.text)

    @classmethod
    @property
    def params(cls):
        params = [
            ("model", "str"),
            ("messages", "list[dict[str, str]]"),
            ("stream", "bool"),
            ("auth", "str"),
        ]
        param = ", ".join([": ".join(p) for p in params])
        return f"g4f.provider.{cls.__name__} supports: ({param})"
