# app/database/requests.py
import datetime as dt
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app.database.models import async_session, User, Event, Game


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        # ищем существующего пользователя
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_events() -> List[Event]:
    now = dt.datetime.now()
    async with async_session() as session:
        result = await session.scalars(select(Event).where(Event.eventDateTime > now).order_by(Event.eventDateTime))
        return result.all()


async def add_event(event: dict) -> None:
    """
    event - словарь с ключами:
      eventName, eventDesc, eventDateTime (datetime), eventDuration (int), eventLocation, eventOrganizer, eventAuthor
    """
    async with async_session() as session:
        event_obj = Event(
            eventName=event["eventName"],
            eventDesc=event.get("eventDesc"),
            eventDateTime=event["eventDateTime"],
            eventDuration=event["eventDuration"],
            eventLocation=event.get("eventLocation"),
            eventOrganizer=event.get("eventOrganizer"),
            eventAuthor=event.get("eventAuthor"),
        )
        session.add(event_obj)
        await session.commit()


# --- Методы для каталога игр ---
async def add_game(data: dict) -> None:
    async with async_session() as session:
        game = Game(
            gameName=data["gameName"],
            gameDesc=data.get("gameDesc"),
            gameGenre=data.get("gameGenre"),
            gamePhoto=data.get("gamePhoto"),  # file_id или URL
            gameAuthor=data.get("gameAuthor"),
        )
        session.add(game)
        await session.commit()


async def get_all_games() -> List[Game]:
    async with async_session() as session:
        result = await session.scalars(select(Game).order_by(Game.gameName))
        return result.all()


async def search_games_by_name(query: str) -> List[Game]:
    async with async_session() as session:
        # ilike для регистронезависимого поиска (sqlite поддерживает)
        result = await session.scalars(select(Game).where(Game.gameName.ilike(f"%{query}%")))
        return result.all()


async def get_games_by_genre(genre: str) -> List[Game]:
    async with async_session() as session:
        # простая проверка подстроки в поле gameGenre (если у тебя хранятся через запятую)
        result = await session.scalars(select(Game).where(Game.gameGenre.ilike(f"%{genre}%")))
        return result.all()