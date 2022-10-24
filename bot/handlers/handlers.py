import enum
from gettext import find
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from markup import *
from aiogram.dispatcher import FSMContext
from db.models import BookHub
from sqlalchemy import select, and_
import re
from enum import Enum


class FindHubForm(StatesGroup):
    location = State()
    country = State()
    city = State()
    distance = State()


class AddHubForm(StatesGroup):
    name = State()
    contacts = State()
    country = State()
    city = State()
    location = State()


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
    await message.answer("Вітаю!", reply_markup=create_markup(main_menu_markup_text))


async def start(message: types.Message):
    if message.text == "Знайсці шафу":
        await FindHubForm.location.set()
        reply = "Дадай інфармацыю аб сваім месцазнаходжанні"
        reply_markup = geolocation_markup()
    else:
        await AddHubForm.name.set()
        reply = "Увядзіце назву"
        reply_markup = types.ReplyKeyboardRemove()

    await message.answer(reply, reply_markup=reply_markup)


async def cancel(message: types.Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.finish()
    await message.answer('Адменены', reply_markup=create_markup(main_menu_markup_text))


async def location_find(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    async with state.proxy() as data:
        data['location'] = (lat, lon)

    await FindHubForm.distance.set()
    await message.answer("У якім радыусе шукаць?", reply_markup=create_markup(distance_markup_text))


async def location_manualy_find(message: types.Message, state: FSMContext):
    await FindHubForm.country.set()
    await message.answer("Увядзіце вашу краіну", reply_markup=types.ReplyKeyboardRemove())


async def country_find(message: types.Message, state: FSMContext):
    country = message.text.strip().lower().title()

    async with state.proxy() as data:
        data['country'] = country
    await FindHubForm.next()

    await message.answer("Увядзіце ваш горад", reply_markup=types.ReplyKeyboardRemove())


async def city_find(message: types.Message, state: FSMContext):
    city = message.text.strip().lower().title()

    async with state.proxy() as data:
        data['city'] = city

    await FindHubForm.distance.set()
    await message.answer("Дадзеныя паспяхова атрыманы", reply_markup=create_markup(find_markup_text))


async def distance_find(message: types.Message, state: FSMContext):
    distance = float(re.sub("[^0-9]", "", message.text))

    async with state.proxy() as data:
        data['distance'] = distance

    await message.answer("Дадзеныя паспяхова атрыманы", reply_markup=create_markup(find_markup_text))


async def find_hubs(message: types.Message, state: FSMContext):

    db_session = message.bot.get("db")

    async with state.proxy() as data:
        dict_data = data.as_dict()

    # else:
    #     print("Not enough location data")
    #     await state.finish()
    #     await message.answer("Не хапае дадзённых", reply_markup=geolocation_markup())

    query = find_hubs_query(dict_data)
    async with db_session() as session:
        book_hubs = await session.execute(query)

    book_hubs_info = [
        f"{index+1}. {hub.name}:\n{hub.contacts}\n{hub.country}, {hub.city}\n" for index, hub in enumerate(book_hubs)]
    reply = "Знойдзена па вашым запыце:\n\n" + "\n".join(book_hubs_info)

    await state.finish()
    await message.answer(reply, reply_markup=create_markup(main_menu_markup_text))


async def name_add(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['name'] = message.text

    await AddHubForm.next()
    await message.answer("Увядзіце кантактную інфармацыю", reply_markup=types.ReplyKeyboardRemove())


async def contacts_add(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['contacts'] = message.text

    await AddHubForm.next()
    await message.answer("Увядзіце краіну")


async def country_add(message: types.Message, state: FSMContext):
    country = message.text.strip().lower().title()

    async with state.proxy() as data:
        data['country'] = country
    await AddHubForm.next()

    await message.answer("Увядзіце горад")


async def city_add(message: types.Message, state: FSMContext):
    city = message.text.strip().lower().title()

    async with state.proxy() as data:
        data['city'] = city
    await AddHubForm.next()

    await message.answer("Дадайце інфармацыю аб месцазнаходжанні", reply_markup=create_markup(skip_markup_text))


async def location_add(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    async with state.proxy() as data:
        data['location'] = (lat, lon)

    await message.answer("Дадзеныя паспяхова атрыманы", reply_markup=create_markup(add_markup_text))


async def skip_location(message: types.Message, state: FSMContext):

    await message.answer("Дадзеныя паспяхова атрыманы", reply_markup=create_markup(add_markup_text))


async def add_hub(message: types.Message, state: FSMContext):
    db_session = message.bot.get("db")

    async with state.proxy() as data:
        dict_data = data.as_dict()

    if "location" in dict_data.keys():
        dict_data["latitude"] = dict_data["location"][0]
        dict_data["longitude"] = dict_data["location"][1]
        dict_data.pop('location', None)

    new_book_hub = BookHub(**dict_data)

    async with db_session() as session:
        session.add(new_book_hub)
        await session.commit()

    book_hubs_info = f"{new_book_hub.name}:\n{new_book_hub.contacts}\n{new_book_hub.country}, {new_book_hub.city}\n"
    reply = "Дададзеная шафа:\n\n" + book_hubs_info

    await state.finish()
    await message.answer(reply, reply_markup=create_markup(main_menu_markup_text))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'])
    dp.register_message_handler(
        start, Text(equals=["Знайсці шафу", "Дадаць шафу"]))
    
    dp.register_message_handler(cancel, Text(equals="Адмяніць"), state='*')
    dp.register_message_handler(location_find, content_types=[
                                'location'], state=FindHubForm.location)
    dp.register_message_handler(location_manualy_find, Text(
        equals="Задаць уручную"), state=FindHubForm.location)
    dp.register_message_handler(country_find, state=FindHubForm.country)
    dp.register_message_handler(find_hubs, Text(
        equals="Шукаць"), state=FindHubForm.distance)
    dp.register_message_handler(city_find, state=FindHubForm.city)
    dp.register_message_handler(distance_find, state=FindHubForm.distance)
    dp.register_message_handler(name_add, state=AddHubForm.name)
    dp.register_message_handler(contacts_add, state=AddHubForm.contacts)
    dp.register_message_handler(country_add, state=AddHubForm.country)
    dp.register_message_handler(city_add, state=AddHubForm.city)
    dp.register_message_handler(location_add, content_types=[
                                'location'], state=AddHubForm.location)
    dp.register_message_handler(add_hub, Text(
        equals="Дадаць"), state=AddHubForm.location)
    dp.register_message_handler(skip_location, Text(equals="Прапусціць"), state=AddHubForm.location)
    
