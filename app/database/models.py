import datetime

from sqlalchemy import String, BigInteger, Text, LargeBinary
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
    name: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(Text)
    event_date: Mapped[datetime.datetime] = mapped_column(String(25))
    event_time: Mapped[datetime.datetime] = mapped_column(String(25))
    location: Mapped[str] = mapped_column(String(25))
    organizer: Mapped[str] = mapped_column(String(25))
    author: Mapped[str] = mapped_column(String(25))
    image: Mapped[bytes] = mapped_column(LargeBinary)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)