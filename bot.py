#!env/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
import json
from random import randint

import remove_background
from pathlib import Path
from settings import stor_path
from io import BytesIO

with open('remove.bg api key.txt') as secret:
    secret = json.loads(secret.read())

# Объект бота
bot = Bot(token=secret['tg_token'])
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

dest_path = ''


# мутит путь
def setup():
    global dest_path
    dest_path = Path(stor_path)
    if not dest_path.is_absolute():
        dest_path = Path.cwd() / dest_path
    if not dest_path.exists():
        dest_path.mkdir()


def newfilename(dir: Path):
    last = max([int(f.stem) for f in dir.iterdir() if f.stem.isdigit()] + [0])
    return dir / f'{last + 1}.jpg'
    ### всегда ли jpg ???


# Хэндлер на команду /start
@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    await message.answer("Hi! This bot can prepare your images to become stickers: \n"
                         "1) Remove background with very clever computer vision AI algorithms (© rembg and api.remove.bg)\n"
                         "2) Add white stroke to the image using openCV lib\n"
                         "3) Resize image to fit to 512px\n"
                         "4) Profit!\n"
                         "ps. In future versions we could add autocreating stickerpacks for ya")


@dp.message_handler(content_types=['photo'])
async def type_test(message: types.Message):
    await message.answer(f"processing your image, please wait...")
    dest = Path(dest_path) / message.from_user.username
    if not dest.exists():
        dest.mkdir()
    new_name = newfilename(dest)
    raw = await message.photo[-1].download(destination_file=new_name)
    # b = BytesIO()
    # b.write(raw.raw)
    # with open('testfile.jpg', 'wb') as f:
    #     f.write(b.getvalue())
    ###
    ready = remove_background.complete_local(new_name)

    await message.answer_document(open(ready, 'rb'), 'here you are')


# тест оболочка для всего
@dp.message_handler(content_types=types.ContentTypes.all())
async def type_test(message: types.Message):
    await message.answer(f"this was {message.content_type} "
                         f"from userid {message.from_user.id}"
                         f" username {message.from_user.username}")


@dp.message_handler(commands="dice")
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


@dp.message_handler(commands="inline_url")
async def cmd_inline_url(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="GitHub", url="https://github.com"),
        types.InlineKeyboardButton(text="Оф. канал Telegram", url="tg://resolve?domain=telegram")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    await message.answer("Кнопки-ссылки", reply_markup=keyboard)


@dp.message_handler(commands="random")
async def cmd_random(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="random_value"))
    await message.answer("Нажмите на кнопку, чтобы бот отправил число от 1 до 10", reply_markup=keyboard)


@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer(str(randint(1, 10)))
    await call.answer(text="Спасибо, что воспользовались ботом!", show_alert=True)  # шоп небыло часиков
    # или просто await call.answer()


user_data = {}


def get_keyboard():
    # Генерация клавиатуры.
    buttons = [
        types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
        types.InlineKeyboardButton(text="+1", callback_data="num_incr"),
        types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")
    ]
    # Благодаря row_width=2, в первом ряду будет две кнопки, а оставшаяся одна
    # уйдёт на следующую строку
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


async def update_num_text(message: types.Message, new_value: int):
    # Общая функция для обновления текста с отправкой той же клавиатуры
    await message.edit_text(f"Укажите число: {new_value}", reply_markup=get_keyboard())


@dp.message_handler(commands="numbers")
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard())


@dp.callback_query_handler(Text(startswith="num_"))
async def callbacks_num(call: types.CallbackQuery):
    # Получаем текущее значение для пользователя, либо считаем его равным 0
    user_value = user_data.get(call.from_user.id, 0)
    # Парсим строку и извлекаем действие, например `num_incr` -> `incr`
    action = call.data.split("_")[1]
    if action == "incr":
        user_data[call.from_user.id] = user_value + 1
        await update_num_text(call.message, user_value + 1)
    elif action == "decr":
        user_data[call.from_user.id] = user_value - 1
        await update_num_text(call.message, user_value - 1)
    elif action == "finish":
        # Если бы мы не меняли сообщение, то можно было бы просто удалить клавиатуру
        # вызовом await call.message.delete_reply_markup().
        # Но т.к. мы редактируем сообщение и не отправляем новую клавиатуру, 
        # то она будет удалена и так.
        await call.message.edit_text(f"Итого: {user_value}")
    # Не забываем отчитаться о получении колбэка
    await call.answer()


if __name__ == "__main__":
    setup()
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
