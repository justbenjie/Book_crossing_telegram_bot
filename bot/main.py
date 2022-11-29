import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from db.base import Base
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from handlers.handlers import register_handlers
from updates_worker import get_handled_updates_list


async def main():

    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    bot = Bot(token=settings.token_bot)

    bot["db"] = async_session_maker

    # async_geolocator = Nominatim(
    #     user_agent="staronki_bot", adapter_factory=AioHTTPAdapter, timeout=15
    # )
    # bot["geocoder"] = async_geolocator

    storage = MemoryStorage()

    dp = Dispatcher(bot, storage=storage)

    register_handlers(dp)

    try:
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
