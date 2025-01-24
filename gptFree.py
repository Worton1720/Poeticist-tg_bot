from typing import Callable
import asyncio
import functools
from g4f.client import Client
import sys
from langdetect import detect

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def __retry_on_network_issue__(func: Callable = None, response_ignore: list = []):
    # response_ignore.append(["流量异常,请尝试更换网络环境", "根据不同种类的亚洲象和非洲象", "根据不同的种类和年龄", "根据不同的物种和性别"])

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            while True:
                response = await func(*args, **kwargs)
                if detect(response[0:20]) == 'zh-cn' or detect(response[0:20]) == 'zh-tw':
                    print(f'Ignoring message "{response}" due to Chinese language.')
                    continue
                elif response in response_ignore:
                    print(f'Processing the message "{response}", trying again.')
                    continue
                return response

        return wrapper

    if func:
        return decorator(func)
    return decorator


# Пример использования декоратора
@__retry_on_network_issue__()
async def generate_response(prompt: list):
    prompts = []
    if prompt[0]["role"] != "system":
        prompts = [
            {
                "role": "system",
                "content": "Вы - телеграм бот - помощник gpt-3.5-turbo. Это история нашего разговора, последний элемент - это обращение к вам."
            }
        ]
    prompts += prompt

    try:
        loop = asyncio.get_event_loop()
        func = functools.partial(
            Client().chat.completions.create, model="gpt-4", messages=prompts
        )
        response = await loop.run_in_executor(None, func)
        return response.choices[0].message.content
    except Exception as e:
        print(f"There was an error: {e}")
        return f"There was an error!"
