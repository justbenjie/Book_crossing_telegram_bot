from aiogram.dispatcher.filters.state import State, StatesGroup


class FindHubForm(StatesGroup):
    location = State()
    distance = State()


class AddHubForm(StatesGroup):
    name = State()
    description = State()
    contacts = State()
    location = State()
    # address = State()
