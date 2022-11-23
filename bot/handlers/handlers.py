import enum
from gettext import find
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ParseMode
from markup import *
from aiogram.dispatcher import FSMContext
from db.models import BookHub
from sqlalchemy import select
import re
from .fsm import FindHubForm, AddHubForm
from geopy.exc import GeocoderTimedOut


async def welcome(message: types.Message, state: FSMContext):
    reply = "Прывітанне👋\n\nЯ дапамагу вам з пошукам і даданнем палічак з беларускімі кнігамі.\n\nВы таксама можаце знайсці кніжкі на [нашым сайце.](https://bbc-max.herokuapp.com/)"
    await state.finish()
    await message.answer(
        reply,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_markup(main_menu_markup_text),
    )


async def start(message: types.Message):
    if message.text == "Знайсці палічку":
        await FindHubForm.location.set()
        reply = "Адпраўце ваша месцазнаходжанне ў дадзены момант, або абярыце лакацыю так: \n📎 -> месцазнаходжанне."
        reply_markup = geolocation_markup()
    else:
        await AddHubForm.name.set()
        reply = "Увядзіце назву."
        reply_markup = types.ReplyKeyboardRemove()

    await message.answer(reply, reply_markup=reply_markup)


async def cancel(message: types.Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.finish()
    await message.answer(
        "❌ Паспяхова адменена!", reply_markup=create_markup(main_menu_markup_text)
    )


async def location_find(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    async with state.proxy() as data:
        data["location"] = (lat, lon)

    await FindHubForm.distance.set()
    await message.answer(
        "У якім радыусе шукаць? \n(Увядзіце адлегласць у кіламетрах)",
        reply_markup=create_markup(distance_markup_text),
    )


async def distance_find(message: types.Message, state: FSMContext):
    distance = float(re.sub("[^0-9]", "", message.text))

    async with state.proxy() as data:
        data["distance"] = distance

    db_session = message.bot.get("db")

    async with state.proxy() as data:
        dict_data = data.as_dict()

    query = select(BookHub.name, BookHub.contacts, BookHub.country, BookHub.city).where(
        BookHub.calculate_distance(dict_data["location"]) < dict_data["distance"]
    )

    async with db_session() as session:
        book_hubs = await session.execute(query)

    book_hubs_info = [
        f"{index+1}. {hub.name}:\n{hub.contacts}\n{hub.country if hub.country else ''}{', ' + hub.city if hub.city else ''}\n"
        for index, hub in enumerate(book_hubs)
    ]

    if len(book_hubs_info) != 0:
        reply = "👌 Знойдзена па вашым запыце:\n\n" + "\n".join(book_hubs_info)
    else:
        reply = "😔 Нажаль паблізу няма бібліятэк ці палічак з беларускімі кнігамі.\n\nМагчыма побач з табой знойдуцца прыватныя кніжкі іншых карыстальнікаў: [пашукай тут](https://bbc-max.herokuapp.com/) "
    await state.finish()
    await message.answer(
        reply,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_markup(main_menu_markup_text),
    )


async def name_add(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data["name"] = message.text

    await AddHubForm.next()
    await message.answer(
        "Увядзіце спасылку на вэб-сайт або старонку ў сацыяльнай сетцы.",
        reply_markup=create_markup(cancel_markup_text),
    )


async def contacts_add(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data["contacts"] = message.text

    await AddHubForm.next()
    await message.answer(
        "Дадайце інфармацыю аб месцазнаходжанні:\n📎 -> месцазнаходжанне.",
        reply_markup=create_markup(cancel_markup_text),
    )


async def location_add(message: types.Message, state: FSMContext):

    lat = message.location.latitude
    lon = message.location.longitude

    async with state.proxy() as data:
        data["location"] = (lat, lon)

    db_session = message.bot.get("db")
    geocoder_session = message.bot.get("geocoder")

    async with state.proxy() as data:
        dict_data = data.as_dict()

    async with geocoder_session as geolocator:
        for i in range(10):
            try:
                location = await geolocator.reverse(
                    dict_data["location"], exactly_one=True
                )
            except GeocoderTimedOut:
                pass

    dict_data["latitude"] = dict_data["location"][0]
    dict_data["longitude"] = dict_data["location"][1]
    dict_data.pop("location", None)

    try:
        dict_data["country"] = location.raw["address"]["country"]
        dict_data["city"] = location.raw["address"]["city"]
    except KeyError:
        pass
    except AttributeError:
        await message.answer("❗ Калі ласка Праверце уведзеную лакацыю")

    new_book_hub = BookHub(**dict_data)

    async with db_session() as session:
        session.add(new_book_hub)
        await session.commit()

    book_hub_info = f"{new_book_hub.name}:\n{new_book_hub.contacts}\n{new_book_hub.country if new_book_hub.country else ''}{', ' + new_book_hub.city if new_book_hub.city else ''}\n"
    reply = "👌 Дададзеная шафа:\n\n" + book_hub_info

    await state.finish()
    await message.answer(reply, reply_markup=create_markup(main_menu_markup_text))


def register_handlers(dp: Dispatcher):

    dp.register_message_handler(
        start, Text(equals=["Знайсці палічку", "Дадаць палічку"])
    )

    dp.register_message_handler(cancel, Text(equals="Адмяніць"), state="*")
    dp.register_message_handler(
        location_find, content_types=["location", "venue"], state=FindHubForm.location
    )
    dp.register_message_handler(distance_find, state=FindHubForm.distance)

    dp.register_message_handler(name_add, state=AddHubForm.name)
    dp.register_message_handler(contacts_add, state=AddHubForm.contacts)
    dp.register_message_handler(
        location_add, content_types=["location", "venue"], state=AddHubForm.location
    )
    dp.register_message_handler(welcome, state="*")
