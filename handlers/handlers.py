from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboard.markup import *
from aiogram.dispatcher import FSMContext


class FSMLocation(StatesGroup):
    lat_lon = State()
    country = State()
    city = State()
    distance = State()


async def welcome(message: types.Message):
    await message.answer("Вітаю!", reply_markup=find_hub_markup())


async def get_hubs(message: types.Message):
    await FSMLocation.lat_lon.set()
    await message.answer("Дадай інфармацыю аб сваім месцазнаходжанні", reply_markup=geolocation_markup())


async def locate_me(message: types.Message):
    reply = "Дадай інфармацыю аб сваім месцазнаходжанні"
    await message.answer(reply, reply_markup=manual_geolocation_markup())


async def get_lat_lon(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(location=[lat, lon])
    await FSMLocation.distance.set()
    await message.answer("У якім радыусе шукаць?", reply_markup=inline_distance_markup())


async def get_location_manualy(message: types.Message, state: FSMContext):
    await FSMLocation.country.set()
    await message.answer("Увядзіце вашу краіну", reply_markup=types.ReplyKeyboardRemove())


async def get_contry(message: types.Message, state: FSMContext):
    country = message.text.strip().lower()

    async with state.proxy() as data:
        data['contry'] = country
    await FSMLocation.next()

    await message.answer("Увядзіце ваш горад", reply_markup=types.ReplyKeyboardRemove())


async def get_city(message: types.Message, state: FSMContext):
    city = message.text.strip().lower()

    async with state.proxy() as data:
        data['city'] = city

    await FSMLocation.next()
    await message.answer("У якім радыусе шукаць?", reply_markup=inline_distance_markup())


async def get_distance(callback: types.CallbackQuery, state: FSMContext):
    db_session = callback.bot.get("db")

    async with state.proxy() as data:
        data['distance'] = int(callback.data)

    async with state.proxy() as data:
        dict_data = data.as_dict()
        print(dict_data)
        if "location" in dict_data.keys():
            pass
            
        elif "city" and "country" in dict_data.keys():
            pass
        else:
            print("state is not valid")

    await callback.message.answer()
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'])
    dp.register_message_handler(get_hubs, commands=['знайсці_шафу', 'вярнуцца'])
    dp.register_message_handler(locate_me, commands=['падзяліцца_месцазнаходжаннем'])
    dp.register_message_handler(get_lat_lon, content_types=['location'], state=FSMLocation.lat_lon)
    dp.register_message_handler(get_location_manualy, commands=['задаць_уручную'], state=FSMLocation.lat_lon)
    dp.register_message_handler(get_contry, state=FSMLocation.country)
    dp.register_message_handler(get_city, state=FSMLocation.city)
    dp.register_callback_query_handler(get_distance, state=FSMLocation.distance)
