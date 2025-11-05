import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import TOKEN

bot = Bot(token=TOKEN)
db = Dispatcher()


@db.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!')


async def main():
    await db.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')