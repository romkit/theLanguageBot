from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def quize_kb(questions: list):
    builder = InlineKeyboardBuilder()
    for question in questions:
        builder.row(
            InlineKeyboardButton(
                text=question,
                callback_data=f'qst_{question}'
            )
        )
    # builder.row(
    #     InlineKeyboardButton(
    #         text='Cancel',
    #         callback_data='back_home'
    #     )
    # )
    # # Настраиваем размер клавиатуры
    builder.adjust(1)
    return builder.as_markup()


def change_answ():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Я ответил верно",
            callback_data=f'chng_'
        )
    )
    return builder.as_markup()


def see_results():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Results",
            callback_data=f'res_'
        )
    )
    return builder.as_markup()


def choose_translation():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Direct",
            callback_data=f'trslt_Direct'
        ),
        InlineKeyboardButton(
            text="Reverse",
            callback_data=f'trslt_Reverse'
        )
    )
    return builder.as_markup()


def choose_type():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Translation",
            callback_data=f'tpe_Translation'
        ),
        InlineKeyboardButton(
            text="Writing",
            callback_data=f'tpe_Writing'
        )
    )
    return builder.as_markup()
