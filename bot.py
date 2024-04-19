import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Router
from config import BOT_TOKEN

HELP_LIST = """
/start - Start the bot
/help - Get help
or just type anything and I will copy and delete it after 15 seconds
"""

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    #q:is there a way to print these answers together? 

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    await message.answer(HELP_LIST)

@dp.message(Command("help"))
async def command_list_handler(message: Message) -> None:
    """
    This handler receives messages with `/help` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"List of commands:\n{HELP_LIST}")




@dp.message()
async def echo_handler(message: Message) -> None:
    # Send a copy of the received message
    sent_message = await message.send_copy(chat_id=message.chat.id)
    # Schedule message deletion
    asyncio.create_task(delete_message_after_timeout(sent_message.chat.id, sent_message.message_id))

async def delete_message_after_timeout(chat_id: int, message_id: int, timeout: int = 15):  # Reduced timeout for testing
    await asyncio.sleep(timeout)  # Wait for specified timeout
    bot = Bot(token=BOT_TOKEN)  # You might want to use a shared Bot instance instead of creating a new one
    try:
        await bot.delete_message(chat_id, message_id)
    finally:
        await bot.session.close()  # Ensure the session is closed properly


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())