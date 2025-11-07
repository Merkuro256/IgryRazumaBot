from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import app.keyboards as kb
import app.database.requests as rq

router = Router()

def printevent(event):
    eventpr = f'''*{event.name}*
_{event.description}_ \n
*{event.event_date}*
*{event.event_time}*
*{event.location}*'''
    return eventpr

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привет! Ты попал в бот клуба "Игры разума"',reply_markup=kb.main)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы нажали кнопку помощи')


@router.message(F.text == 'Анонсы')
async def eventlist(message: Message):
    events = await rq.get_events()
    for event in events:
        await message.answer(printevent(event), parse_mode="Markdown")
