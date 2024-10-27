from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.db_ops import create_connection, get_words, check_user
from keyboards.keyboard import choice_kb, choose_count_words, write_answ
from keyboards.quize_kb import quize_kb, change_answ, see_results, choose_translation, choose_type
import pandas as pd
import asyncio
import random

quize_router = Router()


class Quize(StatesGroup):
    type = State()
    words_count = State()
    user_id = State()
    current_quize = State()
    current_word = State()
    current_question = State()
    true_answ = State()
    current_answ = State()


def get_words_from_words_list(words_list: list, count: int):
    output_words = random.sample(population=words_list, k=count)
    return output_words


def get_words_for_current_question(data, current_quize, i):
    population = current_quize[:]
    population.pop(i)
    random_translate = random.sample(population=population, k=3)
    random_translate = [r["word"] for r in random_translate]
    random_translate.append(data["word"])
    random.shuffle(random_translate)
    return random_translate


@quize_router.message(F.text == '/cancel')
async def cancel(message: Message, state: FSMContext):
    await message.answer('Exit')
    await state.clear()


@quize_router.message(F.text == "/start_quize")
async def start_quizelet(message: Message, state: FSMContext):
    await message.answer('Choose type of quize', reply_markup=choose_type())

# тип квиза
@quize_router.callback_query(F.data.startswith('tpe_'))
async def check_regime(call: CallbackQuery, state: FSMContext):
    await call.answer()
    answ = call.data.replace('tpe_', '')
    if answ == 'Translation':
        await call.message.answer('Choose count of words', reply_markup=choose_count_words(call.message.from_user.id))
        await state.set_state(Quize.words_count)
        await state.update_data(type='Translation')
    elif answ == 'Writing':
        await call.message.answer('Choose count of words', reply_markup=choose_count_words(call.message.from_user.id))
        await state.set_state(Quize.words_count)
        await state.update_data(type='Writing')

# старт квиза в зависимости от типа
@quize_router.message(Quize.words_count)
async def set_current_words(message: Message, state: FSMContext):
    words_count = int(message.text)
    await state.update_data(words_count=words_count, true_answ=0)
    data = await state.get_data()
    tpe = data["type"]
    user_id = str(message.from_user.id)
    conn = await create_connection()
    if await check_user(user_id, conn):
        await message.answer('User is not registered. Please, send /start and than get you words')
        return
    words_list = await get_words(user_id, conn)
    if len(words_list) < words_count:
        await message.answer("You don't have enough words. Append new words and try again")
        return
    current_quize = get_words_from_words_list(words_list, words_count)
    await state.update_data(current_quize=current_quize)
    if tpe == 'Translation':
        await message.answer(
            'Please, select type of translation. In the Direct-regime you need to choose a translation '
            'for your word and in the Reverse-regime you need to choose a word for translation',
            reply_markup=choose_translation())
    elif tpe == 'Writing':
        await state.update_data(current_question=0, current_word=current_quize[0])
        await message.answer(f'{current_quize[0]["translation"]}', reply_markup=write_answ())
        await state.set_state(Quize.current_word)

# проверка вопроса и продолжение квиза для переводов
@quize_router.message(Quize.current_word)
async def check_answer_wrtng(message: Message, state: FSMContext):
    answ = message.text.lower()
    data = await state.get_data()
    current_answer = data["current_word"]["word"].lower()
    if answ == current_answer:
        data["true_answ"] += 1
        await message.answer("✅ " + f'<b>{data["current_word"]["word"]}</b>: {answ}')
    else:
        await message.answer("❌ " + f'<b>{data["current_word"]["word"]}</b>: {answ}', reply_markup=change_answ())
    await state.update_data(true_answ=data["true_answ"], current_answ=answ)

    current_quise = data["current_quize"]
    for i, word in enumerate(current_quise[1::]):
        if i != data["current_question"]:
            continue
        await state.update_data(current_word=word)
        await message.answer(word["translation"], reply_markup=write_answ())
        break
    data["current_question"] += 1
    await state.update_data(current_question=data["current_question"])
    data = await state.get_data()
    if data["current_question"] == data["words_count"] - 1:
        await message.answer("<b>FINISH</b>",
                             reply_markup=see_results())

# получение данных для вопросов
async def frst_qst(current_quize: dict, state: FSMContext):
    data = current_quize[0]
    await state.update_data(current_word=data, current_question=1)
    population = current_quize[:]
    population.pop(0)
    random_translate = random.sample(population=population, k=3)
    random_translate = [r["word"] for r in random_translate]
    random_translate.append(data["word"])
    random.shuffle(random_translate)
    return random_translate


@quize_router.callback_query(F.data.startswith('trslt_'))
async def check_regime(call: CallbackQuery, state: FSMContext):
    await call.answer()
    answ = call.data.replace('trslt_', '')
    data = await state.get_data()
    current_quize = data["current_quize"]
    await call.message.edit_text(call.message.text)
    if answ == 'Direct':
        random_translate = await frst_qst(current_quize, state)
        await call.message.answer(current_quize[0]["translation"], reply_markup=quize_kb(random_translate))
    elif answ == 'Reverse':
        wds = [cur["word"] for cur in current_quize]
        trsnlts = [cur["translation"] for cur in current_quize]
        for cur, wd, trnsl in zip(current_quize, wds, trsnlts):
            cur["word"] = trnsl
            cur["translation"] = wd
        await state.update_data(current_quize=current_quize)
        random_translate = await frst_qst(current_quize, state)
        await call.message.answer(current_quize[0]["translation"], reply_markup=quize_kb(random_translate))


@quize_router.callback_query(F.data.startswith('qst_'))
async def check_answer_trnslt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    answ = call.data.replace('qst_', '')
    data = await state.get_data()
    # print(data)
    current_answer = data["current_word"]["word"]
    if answ == current_answer:
        data["true_answ"] += 1
        await call.message.edit_text("✅ " + f'<b>{call.message.text}</b>: {answ}')
    else:
        await call.message.edit_text("❌ " + f'<b>{call.message.text}</b>: {answ}')
        # reply_markup=change_answ())
    await state.update_data(true_answ=data["true_answ"])

    current_quise = data["current_quize"]
    for i, word in enumerate(current_quise):
        if i != data["current_question"]:
            continue
        random_translate = get_words_for_current_question(word, current_quise, i)
        await state.update_data(current_word=word)
        await call.message.answer(word["translation"], reply_markup=quize_kb(random_translate))
        break
    data["current_question"] += 1
    await state.update_data(current_question=data["current_question"])
    data = await state.get_data()

    if data["current_question"] == data["words_count"] + 1:
        await call.message.answer("<b>FINISH</b>",
                                  reply_markup=see_results())


@quize_router.callback_query(F.data.startswith('res_'))
async def results_output(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    await call.message.edit_text(text='<b>FINISH</b>', reply_markup=None)
    await call.message.answer(text=f"<b>RESULTS</b>\n"
                                   f"Count of true answers: {data['true_answ']}/{data['words_count']}")
    await state.clear()


@quize_router.callback_query(F.data.startswith('chng_'))
async def change_to_true(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    true = data["true_answ"] + 1
    curr_qst = data["current_question"]
    true_answ = data["current_quize"][curr_qst - 1]["word"]
    current_answ = data['current_answ']
    await state.update_data(true_answ=true)
    # msg = call.message.text.split(': ')
    await call.message.edit_text(text='✅' + f"<b>{true_answ}</b>: {current_answ}", reply_markup=None)
