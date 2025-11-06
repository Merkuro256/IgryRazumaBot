from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import ADMIN_IDS
import app.keyboards as kb
from app.storage import users

router = Router()


# /start — добавляем пользователя в список
@router.message(CommandStart())
async def cmd_start(message: Message):
    users.add(message.from_user.id)
    await message.answer(
        'Привет! Ты попал в бот клуба "Игры разума"',
        reply_markup=kb.main
    )


# /help
@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы нажали кнопку помощи')


# /addevent — только для админов
@router.message(Command('addevent'))
async def cmd_addevent(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав для добавления мероприятий.")
        return

    await message.answer("Отправьте текст нового мероприятия:")
    router.message.register(process_new_event, F.chat.id == message.chat.id)


async def process_new_event(message: Message):
    from app.storage import users

    event_text = f"🧩 Новое мероприятие!\n\n{message.text}"

    sent = 0
    for user_id in users:
        try:
            await message.bot.send_message(user_id, event_text)
            sent += 1
        except Exception:
            pass

    await message.answer(f"✅ Мероприятие отправлено {sent} пользователям.")
    # после отправки убираем хендлер
    router.message.unregister(process_new_event)