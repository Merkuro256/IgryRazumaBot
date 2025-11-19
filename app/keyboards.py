# app/keyboards.py
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Главное меню
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анонсы")],
        [KeyboardButton(text="Каталог игр")],
        [KeyboardButton(text="О нас"), KeyboardButton(text="Контакты")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню"
)

# --- Кнопки для редактирования события
event_edit = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить")],
        [KeyboardButton(text="Подтвердить")],
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие"
)

# --- Фильтр жанров
def genre_keyboard(selected: list[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    genres = [
        "Пати", "Стратегия", "Кооператив", "Детектив",
        "Для двоих", "Экономическая", "Фантастика", "Семейная"
    ]
    builder = InlineKeyboardBuilder()
    for g in genres:
        check = "✅ " if g in selected else ""
        builder.button(text=f"{check}{g}", callback_data=f"genre_{g}")
    builder.adjust(2)
    return builder.as_markup()


# --- Клавиатура для списка игр (админ)
def admin_games_list_keyboard(games: list) -> InlineKeyboardMarkup:
    """Создает клавиатуру со списком всех игр для админа"""
    builder = InlineKeyboardBuilder()
    for game in games:
        builder.button(text=f"✏️ {game.gameName}", callback_data=f"admin_edit_game_{game.id}")
    builder.adjust(1)
    return builder.as_markup()


# --- Клавиатура для редактирования игры (админ)
def admin_game_edit_keyboard(game_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с опциями редактирования игры"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Название", callback_data=f"admin_edit_name_{game_id}")
    builder.button(text="📄 Описание", callback_data=f"admin_edit_desc_{game_id}")
    builder.button(text="🎭 Жанр", callback_data=f"admin_edit_genre_{game_id}")
    builder.button(text="📷 Фото", callback_data=f"admin_edit_photo_{game_id}")
    builder.button(text="👤 Автор", callback_data=f"admin_edit_author_{game_id}")
    builder.button(text="🗑️ Удалить", callback_data=f"admin_delete_game_{game_id}")
    builder.button(text="❌ Отмена", callback_data="admin_cancel_edit")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()
