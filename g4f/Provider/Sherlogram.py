import json

from curl_cffi import requests

from ..typing import Any, CreateResult
from .base_provider import BaseProvider


class Sherlogram(BaseProvider):
    #https://play.google.com/store/apps/details?id=com.smplea.chatgpt
    url = "https://sherlogram.herokuapp.com"
    working = True
    supports_stream = False
    supports_gpt_35_turbo = True

    @staticmethod
    def create_completion(
        model: str,
        messages: list[dict[str, str]],
        stream: bool,
        **kwargs: Any,
    ) -> CreateResult:
        payload = json.dumps({"messages": messages})
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip",
            "api_key": kwargs.get("auth","d2e621a6646a4211768cd68e26f21228a81"),
            "connection": "Keep-Alive",
            "content-type": "application/json",
            "host": "sherlogram.herokuapp.com",
            "user-agent": "okhttp/4.9.2",
        }

        response = requests.request("POST", "https://sherlogram.herokuapp.com/gpt/chat/search", headers=headers, data=payload)
        json_data = json.loads(response.text)
        if "content" in json_data:
            yield json_data["content"]
        else:
            raise Exception(f"Error: {response.status_code} : {response.text}")
    
    @classmethod
    @property
    def params(cls):
        params = [
            ("model", "str"),
            ("messages", "list[dict[str, str]]")
        ]
        param = ", ".join([": ".join(p) for p in params])
        return f"g4f.provider.{cls.__name__} supports: ({param})"
