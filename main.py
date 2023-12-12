import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import openai


logging.basicConfig(level=logging.INFO)

openai.api_key = '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'
dp = Dispatcher(Bot("6111409589:AAFP5sGZl-sJ_0yOGYBgvGWEhXGYmLGWBvc"))

if not openai.api_key:
    logging.error("OpenAI API key not found in environment variable")


async def generate_poem(name: str) -> str:
    prompt = (
        f'Создайте стихотворение на русском языке для человеческого имени "{name}" в 4 строчки. Стихотворение должно быть написано в стиле классической поэзии и следовать рифме "АБАБ". \n',
        "Стихотворение должно быть длиной [не больше 4 строчек], следуя рифме. \n",
        "Красиво оформленный, без ненужных абзацев.",
    )

    try:
        response = await asyncio.to_thread(
            openai.Completion.create,
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=250,
            n=1,
            stop=None,
            temperature=0.5,
        )
        poem = response["choices"][0]["text"]
    except Exception as e:
        logging.error(f"Failed to generate poem for {name}: {e}")
        poem = "Произошла ошибка при генерации стихотворения."

    return poem


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Введите ваше имя.")


@dp.message_handler()
async def send(message: types.Message):
    name = message.text.strip()

    if not name:
        await message.answer("Пожалуйста, введите ваше имя.")
        return

    poem = await generate_poem(name)
    await message.answer(poem)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
