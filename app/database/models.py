# app/database/models.py
import datetime
from sqlalchemy import String, BigInteger, Text, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"

engine = create_async_engine(url=DATABASE_URL, echo=False, future=True)

# expire_on_commit=False чтобы объекты оставались пригодными для чтения после commit
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    eventName: Mapped[str] = mapped_column(String(100), nullable=False)
    eventDesc: Mapped[str] = mapped_column(Text, nullable=True)
    eventDateTime: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    eventDuration: Mapped[int] = mapped_column(Integer, nullable=False)  # минуты
    eventLocation: Mapped[str] = mapped_column(String(100), nullable=True)
    eventOrganizer: Mapped[str] = mapped_column(String(100), nullable=True)
    eventAuthor: Mapped[str] = mapped_column(String(100), nullable=True)

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    gameName: Mapped[str] = mapped_column(String(100), nullable=False)
    gameDesc: Mapped[str] = mapped_column(Text, nullable=True)
    gameGenre: Mapped[str] = mapped_column(String(100), nullable=True)  # можно хранить CSV тегов
    gamePhoto: Mapped[str] = mapped_column(String(255), nullable=True)  # file_id или URL
    gameAuthor: Mapped[str] = mapped_column(String(100), nullable=True)


# утилита для создания таблиц
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)