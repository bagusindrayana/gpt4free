from __future__ import annotations

import random
import json
from aiohttp import ClientSession

from ..typing import AsyncResult, Messages
from .base_provider import AsyncGeneratorProvider

API_URL = "https://labs-api.perplexity.ai/socket.io/"
WS_URL = "wss://labs-api.perplexity.ai/socket.io/"

class PerplexityLabs(AsyncGeneratorProvider):
    url = "https://labs.perplexity.ai"    
    working = True
    supports_gpt_35_turbo = True
    models = ['pplx-7b-online', 'pplx-70b-online', 'pplx-7b-chat', 'pplx-70b-chat', 'mistral-7b-instruct', 
        'codellama-34b-instruct', 'llama-2-70b-chat', 'llava-7b-chat', 'mixtral-8x7b-instruct', 
        'mistral-medium', 'related']
    default_model = 'pplx-70b-online'
    model_map = {
        "mistralai/Mistral-7B-Instruct-v0.1": "mistral-7b-instruct", 
        "meta-llama/Llama-2-70b-chat-hf": "llama-2-70b-chat",
        "mistralai/Mixtral-8x7B-Instruct-v0.1": "mixtral-8x7b-instruct",
        "codellama/CodeLlama-34b-Instruct-hf": "codellama-34b-instruct"
    }

    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        proxy: str = None,
        **kwargs
    ) -> AsyncResult:
        if not model:
            model = cls.default_model
        elif model in cls.model_map:
            model = cls.model_map[model]
        elif model not in cls.models:
            raise ValueError(f"Model is not supported: {model}")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Accept": "*/*",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": cls.url,
            "Connection": "keep-alive",
            "Referer": f"{cls.url}/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
        }
        async with ClientSession(headers=headers) as session:
            t = format(random.getrandbits(32), '08x')
            async with session.get(
                f"{API_URL}?EIO=4&transport=polling&t={t}",
                proxy=proxy
            ) as response:
                text = await response.text()

            sid = json.loads(text[1:])['sid']
            post_data = '40{"jwt":"anonymous-ask-user"}'
            async with session.post(
                f'{API_URL}?EIO=4&transport=polling&t={t}&sid={sid}',
                data=post_data,
                proxy=proxy
            ) as response:
                assert await response.text() == 'OK'
                
            async with session.ws_connect(f'{WS_URL}?EIO=4&transport=websocket&sid={sid}', autoping=False) as ws:
                await ws.send_str('2probe')
                assert(await ws.receive_str() == '3probe')
                await ws.send_str('5')
                assert(await ws.receive_str())
                assert(await ws.receive_str() == '6')
                message_data = {
                    'version': '2.2',
                    'source': 'default',
                    'model': model,
                    'messages': messages
                }
                await ws.send_str('42' + json.dumps(['perplexity_playground', message_data]))
                last_message = 0
                while True:
                    message = await ws.receive_str()
                    if message == '2':
                        await ws.send_str('3')
                        continue
                    try:
                        data = json.loads(message[2:])[1]
                        yield data["output"][last_message:]
                        last_message = len(data["output"])
                        if data["final"]:
                            break
                    except:
                        raise RuntimeError(f"Message: {message}")