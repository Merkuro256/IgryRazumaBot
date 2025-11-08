import datetime as dt
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


import app.keyboards as kb
import app.database.requests as rq

router = Router()


class Addevent(StatesGroup):
    eventName = State()
    eventDesc = State()
    eventDateTime = State()
    eventDuration = State()
    eventLocation = State()
    eventOrganizer = State()
    eventAuthor = State()




@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привет! Ты попал в бот клуба "Игры разума"',reply_markup=kb.main)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы нажали кнопку помощи')


@router.message(F.text == 'Анонсы')
async def eventlist(message: Message):
    events = await rq.get_events()
    for event in events:
        await message.answer("*" + event.eventName + "*\n_" + 
                             event.eventDesc + "_\n\n" +
                             str(event.eventDateTime.day) +
                             event.eventDateTime.strftime(" %B \nC *%H:%M*") + " - " +
                             (event.eventDateTime+dt.timedelta(minutes=event.eventDuration)).strftime("до *%H:%M*") + "\n" +
                             event.eventLocation,
                                    
                                    parse_mode="Markdown")


# Добавление мероприятия (пока без фото)
# --------
@router.message(Command('add'))
async def add_eventName(message: Message, state: FSMContext):
    await state.set_state(Addevent.eventName)
    await message.answer('Введи название меропрития:')

@router.message(Addevent.eventName)
async def add_eventDesc(message: Message, state: FSMContext):
    await state.update_data(eventName=message.text)
    await state.set_state(Addevent.eventDesc)
    await message.answer('Введи описание мероприятия:')

@router.message(Addevent.eventDesc)
async def add_eventDataTime(message: Message, state: FSMContext):
    await state.update_data(eventDesc=message.text)
    await state.set_state(Addevent.eventDateTime)
    await message.answer('Введи дату и время начала в формате "%d/%m/%Y %H:%M:%S": ')

@router.message(Addevent.eventDateTime)
async def add_eventLocation(message: Message, state: FSMContext):
    try:
        await state.update_data(eventDateTime=dt.datetime.strptime(message.text, "%d/%m/%Y %H:%M:%S"))
        await state.set_state(Addevent.eventDuration)
        await message.answer('Введи длительность мер-я в минутах:')
    except:
        await message.answer('Неправильный формат даты и времени :(')

@router.message(Addevent.eventDuration)
async def add_eventDuration(message: Message, state: FSMContext):
    try:
        await state.update_data(eventDuration=int(message.text))
        await state.set_state(Addevent.eventLocation)
        await message.answer('Введи локацию:')
    except:
        await message.answer('Нужно именно число :(')

@router.message(Addevent.eventLocation)
async def add_eventOrganizer(message: Message, state: FSMContext):
    await state.update_data(eventLocation=message.text)
    await state.set_state(Addevent.eventOrganizer)
    await message.answer('Введи Организатора:')

@router.message(Addevent.eventOrganizer)
async def add_eventAuthor(message: Message, state: FSMContext):
    await state.update_data(eventOrganizer=message.text)
    await state.set_state(Addevent.eventAuthor)
    await message.answer('Введи Автора:')

@router.message(Addevent.eventAuthor, F.text == 'Изменить')
async def edit_event_restart(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Addevent.eventName)
    await message.answer('Введи название меропрития:')

@router.message(Addevent.eventAuthor, F.text == 'Отмена')
async def cancel_event(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Добавление мероприятия отменено.', reply_markup=kb.main)

@router.message(Addevent.eventAuthor, F.text == 'Подтвердить')
async def confirm_event(message: Message, state: FSMContext):
    event_data = await state.get_data()
    await rq.add_event(event_data)
    await state.clear()
    await message.answer('Мероприятие успешно добавлено!', reply_markup=kb.main)

@router.message(Addevent.eventAuthor)
async def add_eventEnd(message: Message, state: FSMContext):
    await state.update_data(eventAuthor=message.text)
    event_data = await state.get_data()
    await message.answer("ПРОВЕРКА" + "\n\n*" +
                             event_data["eventName"] + "*\n_" + 
                             event_data["eventDesc"] + "_\n\n" +
                             str(event_data["eventDateTime"].day) +
                             event_data["eventDateTime"].strftime(" %B \nC *%H:%M*") + " - " +
                             (event_data["eventDateTime"]+dt.timedelta(minutes=event_data["eventDuration"])).strftime("до *%H:%M*") + "\n" +
                             event_data["eventLocation"] + "\n\n" +
                             "Организатор: " + event_data["eventOrganizer"] + "\n\n" +
                             "Автор: " + event_data["eventAuthor"],
                                    
                parse_mode="Markdown",
                reply_markup=kb.event_edit)



# --------