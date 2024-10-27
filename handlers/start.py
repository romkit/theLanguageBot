from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
from db.db_ops import *
from create_bot import bot

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    #await message.answer('Запуск сообщения по команде /start используя фильтр CommandStart()')
    print(type(message))
    user_id = str(message.from_user.id)
    #conn = await asyncpg.connect(dsn=config('PG_LINK'))
    #print('WORKING CON', type(conn))
    conn = await create_connection()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        check_result = await check_user(user_id, conn)
    if check_result:
        await add_users(user_id, conn)

@start_router.message(Command('start_2'))
async def cmd_start_2(message: Message):
    await message.answer('Запуск сообщения по команде /start_2 используя фильтр Command()')

@start_router.message(F.text == '/start_3')
async def cmd_start_3(message: Message):
    await message.answer('Запуск сообщения по команде /start_3 используя магический фильтр F.text!')

