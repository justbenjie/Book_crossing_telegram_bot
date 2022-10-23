from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from markup import *
from aiogram.dispatcher import FSMContext
from db.models import BookHub
from sqlalchemy import select, and_
import re


class FSMLocation(StatesGroup):
    lat_lon = State()
    country = State()
    city = State()
    distance = State()


def find_hubs_query(data: dict):

    if "location" in data.keys():
        query = select(BookHub.name, BookHub.contacts,
                       BookHub.country, BookHub.city).where(
            BookHub.calculate_distance(data["location"]) < data["distance"])

    # if "country" and "city" in data.keys():
    else:
        query = select(BookHub.name, BookHub.contacts,
                       BookHub.country, BookHub.city).where(
            and_(BookHub.country == data["country"], BookHub.city == data["city"]))

    return query


async def welcome(message: types.Message):
    reply_markup_text = ["Знайсці шафу"]

    await message.answer("Вітаю!", reply_markup=create_markup(reply_markup_text))


async def start(message: types.Message):
    await FSMLocation.lat_lon.set()
    await message.answer("Дадай інфармацыю аб сваім месцазнаходжанні", reply_markup=geolocation_markup())


async def enter_lat_lon(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    reply_markup_text = ["1 км.", "5 км.", "10 км."]

    await state.update_data(location=(lat, lon))
    await FSMLocation.distance.set()
    await message.answer("У якім радыусе шукаць?", reply_markup=create_markup(reply_markup_text))


async def enter_location_manualy(message: types.Message, state: FSMContext):
    await FSMLocation.country.set()
    await message.answer("Увядзіце вашу краіну", reply_markup=types.ReplyKeyboardRemove())


async def enter_country(message: types.Message, state: FSMContext):
    country = message.text.strip().lower().title()

    async with state.proxy() as data:
        data['country'] = country
    await FSMLocation.next()

    await message.answer("Увядзіце ваш горад", reply_markup=types.ReplyKeyboardRemove())


async def enter_city(message: types.Message, state: FSMContext):
    city = message.text.strip().lower().title()
    reply_markup_text = ["Шукаць"]

    async with state.proxy() as data:
        data['city'] = city

    await message.answer("Дадзеныя паспяхова атрыманы", reply_markup=create_markup(reply_markup_text))


async def enter_distance(message: types.Message, state: FSMContext):
    distance = float(re.sub("[^0-9]", "", message.text))
    reply_markup_text = ["Шукаць"]

    async with state.proxy() as data:
        data['distance'] = distance

    await message.answer("Дадзеныя паспяхова атрыманы", reply_markup=create_markup(reply_markup_text))


async def find_hubs(message: types.Message, state: FSMContext):
    db_session = message.bot.get("db")

    async with state.proxy() as data:
        dict_data = data.as_dict()
        print(dict_data)

    # else:
    #     print("Not enough location data")
    #     await state.finish()
    #     await message.answer("Не хапае дадзённых", reply_markup=geolocation_markup())

    query = find_hubs_query(dict_data)
    async with db_session() as session:
        print("connected")
        book_hubs = await session.execute(query)

    book_hubs_info = [
        f"{index+1}. {hub.name}:\n{hub.contacts}\n{hub.country}, {hub.city}\n" for index, hub in enumerate(book_hubs)]
    reply = "Знойдзена па вашым запыце:\n\n" + "\n".join(book_hubs_info)

    await state.finish()
    await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'])
    dp.register_message_handler(
        start, Text(equals="Знайсці шафу"))
    dp.register_message_handler(enter_lat_lon, content_types=[
                                'location'], state=FSMLocation.lat_lon)
    dp.register_message_handler(enter_location_manualy, Text(
        equals="Задаць уручную"), state=FSMLocation.lat_lon)
    dp.register_message_handler(enter_country, state=FSMLocation.country)
    dp.register_message_handler(find_hubs, Text(equals="Шукаць"), state='*')
    dp.register_message_handler(enter_city, state=FSMLocation.city)
    dp.register_message_handler(enter_distance, state=FSMLocation.distance)
