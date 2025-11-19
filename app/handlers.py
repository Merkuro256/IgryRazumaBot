# app/handlers.py
import datetime as dt
import locale
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq
from config import ADMIN_IDS

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
# --- СОСТОЯНИЯ ДЛЯ РЕДАКТИРОВАНИЯ ИГР (АДМИН)
# ==========================
class EditGame(StatesGroup):
    game_id = State()
    field = State()
    new_value = State()


# ==========================
# --- ОБЩИЕ КОМАНДЫ
# ==========================
@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привет! Ты попал в бот клуба "Игры разума"', reply_markup=kb.main)


@router.message(Command("help"))
async def cmd_help(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой команде.")
        return
    
    # Полная справка только для админов
    help_text = (
        "📖 *Справка по командам бота*\n\n"
        
        "🔹 *Основные команды:*\n"
        "• `/start` — начать работу с ботом, показать главное меню\n"
        "• `/help` — показать эту справку (только для админов)\n\n"
        
        "🔹 *Работа с мероприятиями:*\n"
        "• `/add` — добавить новое мероприятие в календарь\n"
        "  _Процесс добавления: название → описание → дата/время → длительность → локация → организатор → автор_\n"
        "• `Анонсы` (кнопка в меню) — просмотр всех предстоящих мероприятий\n\n"
        
        "🔹 *Работа с играми:*\n"
        "• `/addgame` — добавить новую игру в каталог\n"
        "  _Процесс добавления: название → описание → жанр → фото → автор_\n"
        "• `/search` — поиск игры по названию или части названия\n"
        "• `Каталог игр` (кнопка в меню) — просмотр всех игр с фильтрацией по жанрам\n\n"
        
        "🔐 *Админ-команды:*\n"
        "• `/admin_games` — управление играми в каталоге\n"
        "  _Позволяет просмотреть все игры, редактировать их поля (название, описание, жанр, фото, автор) или удалить игру_\n\n"
        
        "💡 *Советы:*\n"
        "• Используйте кнопки меню для быстрого доступа к основным функциям\n"
        "• При добавлении мероприятия дату вводите в формате: `дд/мм/гггг чч:мм:сс`\n"
        "• Для поиска игры можно вводить часть названия\n"
        "• Админ может редактировать любую игру через команду `/admin_games`"
    )
    
    await message.answer(help_text, parse_mode="Markdown")


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
async def filter_by_genre(callback: CallbackQuery, state: FSMContext):
    genre = callback.data.split("_", 1)[1]
    games = await rq.get_games_by_genre(genre)

    if not games:
        await callback.message.answer(f"Нет игр жанра *{genre}* 😔", parse_mode="Markdown")
        return

    for game in games:
        caption = f"*{game.gameName}*\n_{game.gameGenre}_\n\n{game.gameDesc}"
        await callback.message.answer_photo(photo=game.gamePhoto, caption=caption, parse_mode="Markdown")

    await callback.answer()


# ==========================
# --- АДМИН: УПРАВЛЕНИЕ ИГРАМИ
# ==========================
def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS


@router.message(Command("admin_games"))
async def admin_games_list(message: Message):
    """Команда для админов: список всех игр с возможностью редактирования"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой команде.")
        return

    games = await rq.get_all_games()
    if not games:
        await message.answer("📭 Каталог игр пуст.")
        return

    text = f"📋 *Список всех игр* ({len(games)} шт.):\n\nВыберите игру для редактирования:"
    await message.answer(text, parse_mode="Markdown", reply_markup=kb.admin_games_list_keyboard(games))


@router.callback_query(F.data.startswith("admin_edit_game_"))
async def admin_show_game_details(callback: CallbackQuery, state: FSMContext):
    """Показать детали игры и опции редактирования"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав доступа.", show_alert=True)
        return

    game_id = int(callback.data.split("_")[-1])
    game = await rq.get_game_by_id(game_id)

    if not game:
        await callback.answer("❌ Игра не найдена.", show_alert=True)
        return

    text = (f"🎮 *{game.gameName}*\n\n"
            f"📄 Описание: {game.gameDesc or 'не указано'}\n"
            f"🎭 Жанр: {game.gameGenre or 'не указан'}\n"
            f"👤 Автор: {game.gameAuthor or 'не указан'}\n\n"
            f"Выберите, что хотите изменить:")

    if game.gamePhoto:
        await callback.message.answer_photo(
            photo=game.gamePhoto,
            caption=text,
            parse_mode="Markdown",
            reply_markup=kb.admin_game_edit_keyboard(game_id)
        )
    else:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=kb.admin_game_edit_keyboard(game_id)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_name_"))
async def admin_edit_game_name(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование названия игры"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав доступа.", show_alert=True)
        return

    game_id = int(callback.data.split("_")[-1])
    await state.update_data(game_id=game_id, field="gameName")
    await state.set_state(EditGame.new_value)
    await callback.message.answer("✏️ Введите новое название игры:")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_desc_"))
async def admin_edit_game_desc(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование описания игры"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав доступа.", show_alert=True)
        return

    game_id = int(callback.data.split("_")[-1])
    await state.update_data(game_id=game_id, field="gameDesc")
    await state.set_state(EditGame.new_value)
    await callback.message.answer("✏️ Введите новое описание игры:")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_genre_"))
async def admin_edit_game_genre(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование жанра игры"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав доступа.", show_alert=True)
        return

    game_id = int(callback.data.split("_")[-1])
    await state.update_data(game_id=game_id, field="gameGenre")
    await state.set_state(EditGame.new_value)
    await callback.message.answer("✏️ Введите новый жанр игры:")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_photo_"))
async def admin_edit_game_photo(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование фото игры"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав доступа.", show_alert=True)
        return

    game_id = int(callback.data.split("_")[-1])
    await state.update_data(game_id=game_id, field="gamePhoto")
    await state.set_state(EditGame.new_value)
    await callback.message.answer("✏️ Отправьте новое фото игры:")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_author_"))
async def admin_edit_game_author(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование автора игры"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав доступа.", show_alert=True)
        return

    game_id = int(callback.data.split("_")[-1])
    await state.update_data(game_id=game_id, field="gameAuthor")
    await state.set_state(EditGame.new_value)
    await callback.message.answer("✏️ Введите нового автора игры:")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_delete_game_"))
async def admin_delete_game(callback: CallbackQuery, state: FSMContext):
    """Удалить игру"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав доступа.", show_alert=True)
        return

    game_id = int(callback.data.split("_")[-1])
    game = await rq.get_game_by_id(game_id)

    if not game:
        await callback.answer("❌ Игра не найдена.", show_alert=True)
        return

    await rq.delete_game(game_id)
    await callback.message.answer(f"✅ Игра *{game.gameName}* удалена.", parse_mode="Markdown")
    await callback.answer("✅ Игра удалена")


@router.callback_query(F.data == "admin_cancel_edit")
async def admin_cancel_edit(callback: CallbackQuery, state: FSMContext):
    """Отменить редактирование"""
    await state.clear()
    await callback.message.answer("❌ Редактирование отменено.")
    await callback.answer()


@router.message(EditGame.new_value, F.photo)
async def admin_receive_photo(message: Message, state: FSMContext):
    """Получить новое фото игры"""
    data = await state.get_data()
    file_id = message.photo[-1].file_id
    await rq.update_game(data["game_id"], {data["field"]: file_id})
    game = await rq.get_game_by_id(data["game_id"])
    await message.answer(f"✅ Фото игры *{game.gameName}* обновлено!", parse_mode="Markdown")
    await state.clear()


@router.message(EditGame.new_value)
async def admin_save_edit(message: Message, state: FSMContext):
    """Сохранить изменения в игре"""
    data = await state.get_data()
    field = data["field"]
    new_value = message.text

    await rq.update_game(data["game_id"], {field: new_value})
    game = await rq.get_game_by_id(data["game_id"])

    field_names = {
        "gameName": "название",
        "gameDesc": "описание",
        "gameGenre": "жанр",
        "gameAuthor": "автор"
    }

    field_name = field_names.get(field, field)
    await message.answer(f"✅ {field_name.capitalize()} игры *{game.gameName}* обновлено!", parse_mode="Markdown")
    await state.clear()