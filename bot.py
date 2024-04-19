from aiogram import Bot, Dispatcher, html, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import BOT_TOKEN
import asyncio
import logging


HELP_LIST = """ 
/start - Start the bot
/help - Get help
/setup - setup a message to be deleted after specified time"
/cancel - Cancel the current operation
"""

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
storage = MemoryStorage()

class AddMessageStates(StatesGroup):
    time = State()  # State for capturing the time
    message = State()  # State for capturing the message to delete

router = Router()

@router.message(Command("cancel"))
async def handle_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("No active session to cancel.")
    else:
        await state.clear()
        await message.answer("Your current operation has been cancelled successfully.")
        logger.info(f"Cancelled operation for user {message.from_user.id}")

@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!", parse_mode=ParseMode.HTML)

@router.message(Command("help"))
async def command_list_handler(message: Message) -> None:
    await message.answer(HELP_LIST)

@router.message(Command("setup"))
async def command_setup_handler(message: Message, state: FSMContext) -> None:
    await message.answer("Please type the time when I should delete the message (e.g., '15s', '2m').")
    await state.set_state(AddMessageStates.time)
    logger.debug(f"Set state to time for user {message.from_user.id}")

@router.message(AddMessageStates.time)
async def handle_time_input(message: Message, state: FSMContext) -> None:
    if message.text == '/cancel':
        await handle_cancel(message, state)
        return
    try:
        time_suffix = message.text[-1]
        time = int(message.text[:-1]) * (60 if time_suffix == 'm' else 1)
        await state.update_data(time=time)
        await state.set_state(AddMessageStates.message)
        await message.answer("Please type the message I should delete after this time.")
        logger.debug(f"State set to message with time: {time} for user {message.from_user.id}")
    except ValueError:
        await message.answer("Invalid time format. Use '15s' for seconds or '2m' for minutes.")
        logger.error(f"Invalid time format received from user {message.from_user.id}")


@router.message(AddMessageStates.message)
async def handle_message_input(message: Message, state: FSMContext) -> None:
    if message.text == '/cancel':
        await handle_cancel(message, state)
        return

    user_data = await state.get_data()
    time = user_data['time']
    bot_message = await message.answer(message.text)  # Echo the message
    logger.info(f"Received message to delete: '{message.text}', scheduled after {time} seconds for user {message.from_user.id}")
    await asyncio.sleep(time)
    await bot_message.delete()
    await state.clear()
    logger.info("Message deleted and state cleared for user {message.from_user.id}")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())