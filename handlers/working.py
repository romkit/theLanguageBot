from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from keyboards.keyboard import change_words_kb
from aiogram.utils.chat_action import ChatActionSender
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.db_ops import add_word_from_df, add_word_from_text, create_connection, get_words, update_words
from create_bot import bot
import pandas as pd
import asyncio
import openpyxl


working_router = Router()


class Form(StatesGroup):
    words_string = State()
    words_csv = State()
    words_xlsx = State()
    rewrite_type = State()
    changing_line = State()


@working_router.message(F.text == '/cancel')
async def cancel(message: Message, state: FSMContext):
    await message.answer('Exit')
    await state.clear()


@working_router.message(F.text == '/add_from_xlsx')
async def add_words_from_csv(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.reply('Send your foreign word(s) in a one-page excel file'
                            '\n<b>Example:</b>\nbook;книга')
    await state.set_state(Form.words_xlsx)


@working_router.message(F.text == '/add_from_csv')
async def add_words_from_csv(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.reply('Send your foreign word(s) in a .csv-file with ; as separator'
                            '\n<b>Example .csv-row:</b>\nbook;книга')
    await state.set_state(Form.words_csv)


@working_router.message(F.text == '/add_from_string')
async def add_words_from_string_reply(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.reply('Send your foreign word(s) with its translation with ; as separator'
                            '\n<b>Example:</b>\nbook;книга')
    await state.set_state(Form.words_string)


@working_router.message(F.text == '/get_my_words')
async def get_user_words(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    conn = await create_connection()
    words = await get_words(user_id, conn)
    text = 'word,translation\n'
    for word in words:
        text += f'{word["word"]},{word["translation"]}\n'
    text_file = BufferedInputFile(text.encode("cp1251"), filename="words.txt")

    await message.answer_document(text_file)

# изменение слова в базе
@working_router.message(F.text == '/change')
async def change_user_words(message: Message):
    await message.answer('Please choose what do you what to change', reply_markup=change_words_kb())

# получение колонки изменения
@working_router.callback_query(F.data.startswith('wrdchng_'))
async def change_user_words(call: CallbackQuery, state: FSMContext):
    await call.answer()
    type_ = call.data.replace('wrdchng_', '')
    await state.update_data(rewrite_type=type_)
    await call.message.edit_text('Now input changing line with ; as separator')
    await state.set_state(Form.changing_line)

# получение строки изменения
@working_router.callback_query(F.text, Form.changing_line)
async def change_user_words(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    words = [m.split(';').append(user_id) for m in message.text.split('\n')]
    data = await state.get_data()
    upd_type = data['rewrite_type']
    conn = await create_connection()
    await update_words(words, upd_type, conn)

@working_router.message(F.text, Form.words_string)
async def add_words_from_string(message: Message, state: FSMContext):
    data = message.text.split('\n')
    user_id = str(message.from_user.id)
    await state.update_data(words_string=data)
    conn = await create_connection()
    data = await state.get_data()
    await add_word_from_text(data['words_string'], user_id, conn)


@working_router.message(Form.words_csv)
async def add_words_from_csv(message: Message, state: FSMContext):
    file_id = message.document
    file = await bot.download(file_id)
    user_id = str(message.from_user.id)
    await state.update_data(words_csv=file)
    df = pd.read_csv(file, sep=';', names=['word', 'translation'])
    df = df.assign(user_id=[user_id] * df.shape[0])  # ['user_id', 'word', 'translation']
    conn = await create_connection()
    await add_word_from_df(df, conn)


@working_router.message(Form.words_xlsx)
async def add_words_from_csv(message: Message, state: FSMContext):
    file_id = message.document
    file = await bot.download(file_id)
    print(type(file))
    user_id = str(message.from_user.id)
    df = pd.read_excel(file, names=['word', 'translation'])
    df = df.assign(user_id=[user_id] * df.shape[0])
    await state.update_data(words_xlsx=df.to_dict())
    conn = await create_connection()
    await add_word_from_df(df, conn)
