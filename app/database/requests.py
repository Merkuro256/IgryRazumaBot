import datetime as dt

from app.database.models import async_session
from app.database.models import User, Event
from sqlalchemy import select



async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
        session.close()


async def get_events():
    now = dt.datetime.now()
    async with async_session() as session:
        return await session.scalars(select(Event).where(Event.eventDateTime > now))


async def add_event(event: int) -> None:
    async with async_session() as session:
        eventTrue = Event (eventName = event["eventName"],
                           eventDesc = event["eventDesc"],
                           eventDateTime = event["eventDateTime"],
                           eventDuration = event["eventDuration"],
                           eventLocation = event["eventLocation"],
                           eventOrganizer = event["eventOrganizer"],
                           eventAuthor = event["eventAuthor"]
                           )
        session.add(eventTrue)
        await session.commit()