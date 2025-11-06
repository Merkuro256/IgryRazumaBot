from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Анонсы')],
                                     [KeyboardButton(text='Каталог игр')],
                                     [KeyboardButton(text='О нас'),
                                      KeyboardButton(text='Контакты')]],
                            resize_keyboard=True,
                            input_field_placeholder="Выберите пункт меню")




