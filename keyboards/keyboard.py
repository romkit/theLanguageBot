from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from create_bot import admins


def choose_count_words(user_id: int):
    kb_list = [
        [KeyboardButton(text='5')],
        [KeyboardButton(text='10'), KeyboardButton(text='25')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def choice_kb(user_id: str, words: list):
    kb_list = [
        [KeyboardButton(text=words[0]), KeyboardButton(text=words[1])],
        [KeyboardButton(text=words[2]), KeyboardButton(text=words[3])]
    ]
    if user_id in admins:
        kb_list.append([KeyboardButton(text="Админ панель")])

    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def write_answ():
    kb_list = [

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder="Input word's translation:")
    return keyboard


def change_words_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Word",
            callback_data=f'wrdchng_Word'
        ),
        InlineKeyboardButton(
            text="Translation",
            callback_data=f'wrdchng_Translation'
        )
    )
    return builder.as_markup()

def choose_type_of_edit():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="From string",
            callback_data=f'edttype_string'
        ),
        InlineKeyboardButton(
            text="From .xlsx",
            callback_data=f'edttype_xlsx'
        ),
        InlineKeyboardButton(
            text="From .csv",
            callback_data=f'edttype_csv'
        )
    )
    return builder.as_markup()
