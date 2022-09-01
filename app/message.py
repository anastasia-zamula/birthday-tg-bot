import logging
import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import BadRequest
from app.notion import Notion

tg_channel = os.environ["TG_BIRTHDAY_CHANNEL"]
bot = Bot(token=os.environ["TG_BIRTHDAY_TOKEN"])
dp = Dispatcher(bot)

logger = logging.getLogger(__name__)


async def send_message(message, channel_id, parse_mode="HTML"):
    try:
        await bot.send_message(channel_id, message, parse_mode=parse_mode)
    except BadRequest:
        pass


async def update_notion_bday():
    notion_birthday = Notion()
    birthdays = notion_birthday.get_data()
    [await send_message(message, tg_channel) for message in birthdays]
