# app/handlers.py
import datetime as dt
import locale
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

router = Router()


# ==========================
# --- СОСТОЯНИЯ ДЛЯ СОБЫТИЙ
# ==========================
class AddEvent(StatesGroup):
    eventName = State()
    eventDesc = State()
    eventDateTime = State()
    eventDuration = State()
    eventLocation = State()
    eventOrganizer = State()
    eventAuthor = State()


# ==========================
# --- СОСТОЯНИЯ ДЛЯ ИГР
# ==========================
class AddGame(StatesGroup):
    gameName = State()
    gameDesc = State()
    gameGenre = State()
    gamePhoto = State()
    gameAuthor = State()


class SearchGame(StatesGroup):
    query = State()


# ==========================
# --- ОБЩИЕ КОМАНДЫ
# ==========================
@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привет! Ты попал в бот клуба "Игры разума"', reply_markup=kb.main)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("📖 Помощь:\n\n"
                         "• /add — добавить мероприятие\n"
                         "• /addgame — добавить игру в каталог\n"
                         "• /search — поиск игры по названию\n"
                         "• 'Каталог игр' — список всех настолок\n"
                         "• 'Анонсы' — список ближайших мероприятий")


# ==========================
# --- АНОНСЫ (мероприятия)
# ==========================
@router.message(F.text == "Анонсы")
async def eventlist(message: Message):
    events = await rq.get_events()
    if not events:
        await message.answer("Пока нет предстоящих мероприятий 😔")
        return

    for event in events:
        end_time = event.eventDateTime + dt.timedelta(minutes=event.eventDuration)
        text = (f"*{event.eventName}*\n"
                f"_{event.eventDesc}_\n\n"
                f"{event.eventDateTime.day} {event.eventDateTime.strftime('%B')}\n"
                f"С *{event.eventDateTime.strftime('%H:%M')}* до *{end_time.strftime('%H:%M')}*\n"
                f"📍 {event.eventLocation}\n"
                f"👤 Организатор: {event.eventOrganizer}")
        await message.answer(text, parse_mode="Markdown")


# ==========================
# --- ДОБАВЛЕНИЕ МЕРОПРИЯТИЯ
# ==========================
@router.message(Command("add"))
async def add_eventName(message: Message, state: FSMContext):
    await state.set_state(AddEvent.eventName)
    await message.answer("Введи название мероприятия:")


@router.message(AddEvent.eventName)
async def add_eventDesc(message: Message, state: FSMContext):
    await state.update_data(eventName=message.text)
    await state.set_state(AddEvent.eventDesc)
    await message.answer("Введи описание мероприятия:")


@router.message(AddEvent.eventDesc)
async def add_eventDateTime(message: Message, state: FSMContext):
    await state.update_data(eventDesc=message.text)
    await state.set_state(AddEvent.eventDateTime)
    await message.answer('Введи дату и время начала в формате "%d/%m/%Y %H:%M:%S": ')


@router.message(AddEvent.eventDateTime)
async def add_eventDuration(message: Message, state: FSMContext):
    try:
        date = dt.datetime.strptime(message.text, "%d/%m/%Y %H:%M:%S")
        await state.update_data(eventDateTime=date)
        await state.set_state(AddEvent.eventDuration)
        await message.answer("Введи длительность мероприятия (в минутах):")
    except Exception:
        await message.answer("⛔ Неверный формат. Пример: 25/12/2025 18:00:00")


@router.message(AddEvent.eventDuration)
async def add_eventLocation(message: Message, state: FSMContext):
    try:
        duration = int(message.text)
        await state.update_data(eventDuration=duration)
        await state.set_state(AddEvent.eventLocation)
        await message.answer("Введи локацию:")
    except ValueError:
        await message.answer("⛔ Нужно ввести число минут!")


@router.message(AddEvent.eventLocation)
async def add_eventOrganizer(message: Message, state: FSMContext):
    await state.update_data(eventLocation=message.text)
    await state.set_state(AddEvent.eventOrganizer)
    await message.answer("Введи организатора:")


@router.message(AddEvent.eventOrganizer)
async def add_eventAuthor(message: Message, state: FSMContext):
    await state.update_data(eventOrganizer=message.text)
    await state.set_state(AddEvent.eventAuthor)
    await message.answer("Введи автора (кто добавляет):")


@router.message(AddEvent.eventAuthor)
async def event_confirm(message: Message, state: FSMContext):
    await state.update_data(eventAuthor=message.text)
    data = await state.get_data()

    text = (f"*ПРОВЕРКА*\n\n"
            f"*{data['eventName']}*\n"
            f"_{data['eventDesc']}_\n\n"
            f"{data['eventDateTime'].strftime('%d %B %Y %H:%M')} "
            f"на {data['eventDuration']} мин.\n"
            f"📍 {data['eventLocation']}\n"
            f"Организатор: {data['eventOrganizer']}\n"
            f"Автор: {data['eventAuthor']}")
    await message.answer(text, parse_mode="Markdown", reply_markup=kb.event_edit)


@router.message(AddEvent.eventAuthor, F.text == "Подтвердить")
async def confirm_event(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.add_event(data)
    await state.clear()
    await message.answer("✅ Мероприятие добавлено!", reply_markup=kb.main)


@router.message(AddEvent.eventAuthor, F.text == "Отмена")
async def cancel_event(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Добавление мероприятия отменено.", reply_markup=kb.main)


@router.message(AddEvent.eventAuthor, F.text == "Изменить")
async def edit_event_restart(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddEvent.eventName)
    await message.answer("Введи новое название мероприятия:")


# ==========================
# --- КАТАЛОГ ИГР
# ==========================
@router.message(F.text == "Каталог игр")
async def show_games(message: Message):
    games = await rq.get_all_games()
    if not games:
        await message.answer("Каталог пока пуст 😔")
        return

    await message.answer("🎲 Каталог настольных игр:", reply_markup=kb.genre_keyboard())

    for game in games:
        caption = (f"*{game.gameName}*\n"
                   f"_{game.gameGenre}_\n\n"
                   f"{game.gameDesc}\n\n"
                   f"Добавил: {game.gameAuthor}")
        await message.answer_photo(photo=game.gamePhoto, caption=caption, parse_mode="Markdown")


# ==========================
# --- ДОБАВЛЕНИЕ ИГР
# ==========================
@router.message(Command("addgame"))
async def add_game_name(message: Message, state: FSMContext):
    await state.set_state(AddGame.gameName)
    await message.answer("Введи название настольной игры:")


@router.message(AddGame.gameName)
async def add_game_desc(message: Message, state: FSMContext):
    await state.update_data(gameName=message.text)
    await state.set_state(AddGame.gameDesc)
    await message.answer("Введи описание игры:")


@router.message(AddGame.gameDesc)
async def add_game_genre(message: Message, state: FSMContext):
    await state.update_data(gameDesc=message.text)
    await state.set_state(AddGame.gameGenre)
    await message.answer("Укажи жанр (например: стратегия, кооператив, пати):")


@router.message(AddGame.gameGenre)
async def add_game_photo(message: Message, state: FSMContext):
    await state.update_data(gameGenre=message.text)
    await state.set_state(AddGame.gamePhoto)
    await message.answer("Отправь фото игры:")


@router.message(AddGame.gamePhoto, F.photo)
async def receive_game_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(gamePhoto=file_id)
    await state.set_state(AddGame.gameAuthor)
    await message.answer("Кто добавил игру?")


@router.message(AddGame.gameAuthor)
async def finalize_game(message: Message, state: FSMContext):
    await state.update_data(gameAuthor=message.text)
    data = await state.get_data()
    await rq.add_game(data)
    await state.clear()
    await message.answer("✅ Игра успешно добавлена!", reply_markup=kb.main)


# ==========================
# --- ПОИСК ИГР
# ==========================
@router.message(Command("search"))
async def search_start(message: Message, state: FSMContext):
    await state.set_state(SearchGame.query)
    await message.answer("🔍 Введи название или часть названия игры:")


@router.message(SearchGame.query)
async def search_games(message: Message, state: FSMContext):
    query = message.text
    await state.clear()
    games = await rq.search_games_by_name(query)
    if not games:
        await message.answer("❌ Ничего не найдено.")
        return

    for game in games:
        caption = f"*{game.gameName}*\n_{game.gameGenre}_\n\n{game.gameDesc}"
        await message.answer_photo(photo=game.gamePhoto, caption=caption, parse_mode="Markdown")


# ==========================
# --- ФИЛЬТР ПО ЖАНРАМ
# ==========================
@router.callback_query(F.data.startswith("genre_"))
async def filter_by_genre(callback, state: FSMContext):
    genre = callback.data.split("_", 1)[1]
    games = await rq.get_games_by_genre(genre)

    if not games:
        await callback.message.answer(f"Нет игр жанра *{genre}* 😔", parse_mode="Markdown")
        return

    for game in games:
        caption = f"*{game.gameName}*\n_{game.gameGenre}_\n\n{game.gameDesc}"
        await callback.message.answer_photo(photo=game.gamePhoto, caption=caption, parse_mode="Markdown")

    await callback.answer()