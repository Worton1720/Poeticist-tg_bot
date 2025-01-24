import os
import logging
import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from gptFree import generate_response  # Импортируем функцию из gptFree.py
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)

# Функция для сохранения имени и стиха в JSON файл
async def save_name_to_file(name: str, poem: str):
    try:
        # Читаем существующие данные из файла
        if os.path.exists("names.json"):
            with open("names.json", "r", encoding="utf-8") as file:
                names = json.load(file)
        else:
            names = {}

        # Добавляем новое имя и стих в начало словаря
        names[name] = poem

        # Сохраняем обновленный словарь обратно в файл
        with open("names.json", "w", encoding="utf-8") as file:
            json.dump(names, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Failed to save name and poem to file: {e}")

async def generate_poem(name: str) -> str:
    prompt = [
        {"role": "system", "content": f'Ты - классический русский поэт. Напиши четверостишье о человеке по имени [{name}]. Включи в стихотворение его характерные черты, увлечения и мечты. Стихотворение должно быть написано в рифмованном стиле и состоять из одного четверостишья. Используй яркие образы и метафоры, чтобы передать атмосферу и чувства, связанные с этим именем.'},
    ]

    try:
        # Используем функцию generate_response для получения ответа
        poem = await generate_response(prompt)
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

    # Генерируем стих для имени
    poem = await generate_poem(name)

    # Сохраняем имя и стих в файл
    await save_name_to_file(name, poem)

    await message.answer(poem)

if __name__ == "__main__":
    asyncio.run(executor.start_polling(dp, skip_updates=True))
