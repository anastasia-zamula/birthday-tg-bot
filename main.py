import asyncio
import logging
import os

import aioschedule
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from app.message import update_notion_bday

bot = Bot(token=os.environ["TG_BIRTHDAY_TOKEN"])
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


async def scheduler():
    aioschedule.every().day.at("10:00").do(update_notion_bday)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    asyncio.create_task(scheduler())


def start_bot():
    executor.start_polling(dp, on_startup=on_startup)  # skip_updates=True,


if __name__ == "__main__":
    start_bot()
