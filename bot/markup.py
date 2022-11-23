from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu_markup_text = ["Знайсці палічку", "Дадаць палічку"]
find_markup_text = ["Шукаць", "Адмяніць"]
add_markup_text = ["Дадаць", "Адмяніць"]
cancel_markup_text = ["Адмяніць"]
distance_markup_text = ["2 км.", "5 км.", "10 км."]


def create_markup(texts):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for text in texts:
        markup.add(KeyboardButton(text=text))

    return markup


def geolocation_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(KeyboardButton("Падзяліцца месцазнаходжаннем", request_location=True))

    return markup
