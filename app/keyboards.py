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
def genre_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    genres = ["Пати", "Стратегия", "Кооператив", "Детектив", "Для двоих"]
    for g in genres:
        builder.button(text=g, callback_data=f"genre_{g}")
    builder.adjust(2)
    return builder.as_markup()

def genre_keyboard(selected: list[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    genres = [
        "Пати", "Стратегия", "Кооператив", "Детектив",
        "Для двоих", "Экономическая", "Фантастика", "Семейная"
    ]
    builder =  InlineKeyboardBuilder()
    for g in genres:
        check