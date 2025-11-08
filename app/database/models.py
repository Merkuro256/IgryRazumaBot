import datetime

from sqlalchemy import String, BigInteger, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


class Event(Base):

    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True)
    eventName: Mapped[str] = mapped_column(String(25))
    eventDesc: Mapped[str] = mapped_column(Text)
    eventDateTime: Mapped[datetime.datetime] = mapped_column(DateTime)
    eventDuration: Mapped[int] = mapped_column(BigInteger)
    eventLocation: Mapped[str] = mapped_column(String(25))
    eventOrganizer: Mapped[str] = mapped_column(String(25))
    eventAuthor: Mapped[str] = mapped_column(String(25))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)