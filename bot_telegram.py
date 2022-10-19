from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboard.markup import *
from db.database import get_db, engine, SessionLocal
from db import models
from config import settings

TOKEN = settings.token_bot

models.Base.metadata.create_all(bind=engine)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class FSMLocation(StatesGroup):
    lat_lon = State()
    country = State()
    city = State()
    distance = State()

async def on_startup(_):
    print("bot is running")


@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.answer("Вітаю!", reply_markup=find_hub_markup())


@dp.message_handler(commands=['знайсці_шафу', 'вярнуцца'])
async def get_hubs(message: types.Message):
    await FSMLocation.lat_lon.set()
    await message.answer("Дадай інфармацыю аб сваім месцазнаходжанні", reply_markup=geolocation_markup())


@dp.message_handler(commands=['падзяліцца_месцазнаходжаннем'])
async def locate_me(message: types.Message):
    reply = "Дадай інфармацыю аб сваім месцазнаходжанні"
    await message.answer(reply, reply_markup=manual_geolocation_markup())


@dp.message_handler(content_types=['location'], state=FSMLocation.lat_lon)
async def get_lat_lon(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(location=[lat, lon])
    await FSMLocation.distance.set()
    await message.answer("У якім радыусе шукаць?", reply_markup=inline_distance_markup())


@dp.message_handler(commands=['задаць_уручную'], state=FSMLocation.lat_lon)
async def get_location_manualy(message: types.Message, state: FSMContext):
    await FSMLocation.country.set()
    await message.answer("Увядзіце вашу краіну", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMLocation.country)
async def get_contry(message: types.Message, state: FSMContext):
    country = message.text.strip().lower()

    async with state.proxy() as data:
        data['contry'] = country
    await FSMLocation.next()

    await message.answer("Увядзіце ваш горад", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMLocation.city)
async def get_city(message: types.Message, state: FSMContext):
    city = message.text.strip().lower()

    async with state.proxy() as data:
        data['city'] = city

    await FSMLocation.next()
    await message.answer("У якім радыусе шукаць?", reply_markup=inline_distance_markup())


@dp.callback_query_handler(state=FSMLocation.distance)
async def get_distance(callback: types.CallbackQuery, state: FSMContext):
    db_session = callback.bot.get("db")
    async with state.proxy() as data:
        data['distance'] = int(callback.data)

    async with state.proxy() as data:
        dict_data = data.as_dict()
        print(dict_data)
        if "location" in dict_data.keys():
            with 
            hubs = db.query(models.BookHub).all()
        elif "city" and "country" in dict_data.keys():
            hubs = db.query(models.BookHub).all()
        else:
            print("state is not valid")


    await callback.message.answer(hubs)
    await state.finish()


if __name__ == '__main__':
    db = get_db()
    executor.start_polling(dp, skip_updates=True)
