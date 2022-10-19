from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# button_search_bookcase = KeyboardButton('знайсці_шафу')

# keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

# keyboard.add(button_search_bookcase)

back_message = "/вярнуцца"


def manual_geolocation_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(KeyboardButton("/задаць_уручную"))
    markup.add(back_message)

    return markup


def geolocation_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(KeyboardButton(
        "/падзяліцца_месцазнаходжаннем", request_location=True))
    markup.add("/задаць_уручную")

    return markup


def find_hub_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(KeyboardButton('/знайсці_шафу'))

    return markup


def distance_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("1 км.", "5 км.", "10 км.", back_message)

    return markup


def inline_distance_markup():
    markup = InlineKeyboardMarkup(row_width=3)
    button_1 = InlineKeyboardButton('1 км.', callback_data=1)

    markup.add(InlineKeyboardButton('1 км.', callback_data=1),
               InlineKeyboardButton('5 км.', callback_data=5),
               InlineKeyboardButton('20 км.', callback_data=20))
    return markup
