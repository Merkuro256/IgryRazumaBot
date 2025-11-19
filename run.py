import asyncio
from aiogram import Bot, Dispatcher, F

from config import TOKEN
from app.handlers import router
from app.database.models import async_main


async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    db = Dispatcher()
    db.include_router(router)
    await db.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')