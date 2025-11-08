from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Анонсы')],
                                     [KeyboardButton(text='Каталог игр')],
                                     [KeyboardButton(text='О нас'),
                                      KeyboardButton(text='Контакты')]],
                            resize_keyboard=True,
                            input_field_placeholder="Выберите пункт меню")


events = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Игротеки', callback_data='Игротеки')]
])

event_edit = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Изменить')],
                                           [KeyboardButton(text='Подтвердить')],
                                           [KeyboardButton(text='Отмена')]],
                            resize_keyboard=True,
                            input_field_placeholder="Выбери действие")