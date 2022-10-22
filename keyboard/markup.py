from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# button_search_bookcase = KeyboardButton('знайсці_шафу')

# keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

# keyboard.add(button_search_bookcase)

back_message = "/вярнуцца"

def create_markup(texts):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for text in texts:
        markup.add(KeyboardButton(text=text))

    return markup


def geolocation_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(KeyboardButton(
        "Падзяліцца месцазнаходжаннем", request_location=True))
    markup.add("Задаць уручную")

    return markup

