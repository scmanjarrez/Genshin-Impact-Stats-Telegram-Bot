# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from typing import List, Optional, Tuple
from telegram import Update


import utils as ut
import calendar
import datetime


async def _answer(update: Update, msg: str = None) -> None:
    if update.callback_query is not None:
        try:
            await update.callback_query.answer(msg)
        except BadRequest:
            pass


def button(buttons: List[Tuple[str, str]]):
    return [InlineKeyboardButton(bt[0], callback_data=bt[1])
            for bt in buttons]


async def main_menu(update: Update) -> None:
    await _answer(update)
    kb = [button([("🗒 Daily Notes 🗒", 'notes_menu')]),
          button([("📖 Traveler's Diary 📖", 'diary_month_menu')]),
          button([("✨ Abyss ✨", 'abyss_seasons_menu')])]
    resp = ut.send
    if update.callback_query is not None:
        resp = ut.edit
    await resp(update, "Menu", reply_markup=InlineKeyboardMarkup(kb))


async def notes_menu(update: Update, context: ut.Context) -> None:
    ut.autoupdate_notes(update, context)
    msg, remaining, parametric = await ut.notes(ut.uid(update))
    ut.notifier(update, context, remaining)
    ut.notifier_parametric(update, context, parametric)
    await _answer(update)
    kb = [button([("🔃 Update 🔃", 'notes_menu')]),
          button([("« Back to Menu", 'main_menu')])]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))


async def update_notes(update: Update, context: ut.Context,
                       data: Optional[
                           Tuple[str, ut.TimeDelta, ut.TimeDelta]] = None
                       ) -> None:
    if data is None:
        msg, remaining, parametric = await ut.notes(ut.uid(update))
    else:
        msg, remaining, parametric = data
    ut.notifier(update, context, remaining)
    ut.notifier_parametric(update, context, parametric)
    kb = [button([("🔃 Update 🔃", 'notes_menu')]),
          button([("« Back to Menu", 'main_menu')])]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))


async def diary_month_menu(update: Update) -> None:
    await _answer(update)
    month = datetime.datetime.now().month
    kb = [button([(calendar.month_name[month], f'diary_menu_{month}'),
                  (calendar.month_name[month-1], f'diary_menu_{month-1}'),
                  (calendar.month_name[month-2], f'diary_menu_{month-2}')]),
          button([("« Back to Menu", 'main_menu')])]
    await ut.edit(update, "Traveler's Diary", InlineKeyboardMarkup(kb))


async def diary_menu(update: Update, month: int) -> None:
    msg = await ut.diary(ut.uid(update), month)
    await _answer(update)
    kb = [button([("« Back to Diary", 'diary_month_menu'),
                  ("« Back to Menu", 'main_menu')])]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))


async def abyss_seasons_menu(update: Update) -> None:
    await _answer(update)
    kb = [button([("Current", 'abyss_floors_menu'),
                  ("Previous", 'abyss_floors_menu_previous')]),
          button([("« Back to Menu", 'main_menu')])]
    if update.callback_query is not None:
        resp = ut.edit
    await resp(update, "Abyss Seasons", reply_markup=InlineKeyboardMarkup(kb))


async def abyss_floors_menu(update: Update, previous: bool) -> None:
    await _answer(update)
    suffix = ''
    season = "current"
    if previous:
        suffix = '_previous'
        season = "previous"
    kb = [button([("All", f'abyss_menu{suffix}_all')]),
          button([("9", f'abyss_menu{suffix}_9'),
                  ("10", f'abyss_menu{suffix}_10'),
                  ("11", f'abyss_menu{suffix}_11'),
                  ("12", f'abyss_menu{suffix}_12')]),
          button([("« Back to Seasons", 'abyss_seasons_menu'),
                  ("« Back to Menu", 'main_menu')])]
    if update.callback_query is not None:
        resp = ut.edit
    await resp(update, f"Abyss Floors ({season})",
               reply_markup=InlineKeyboardMarkup(kb))


async def abyss_menu(update: Update, previous: bool, floor: str) -> None:
    msg = await ut.abyss(ut.uid(update), previous, floor)
    await _answer(update)
    suffix = ''
    if previous:
        suffix = '_previous'

    kb = [button([("🔃 Update 🔃", f'abyss_menu{suffix}_{floor}')]),
          button([("« Back to Floors", f'abyss_floors_menu{suffix}'),
                  ("« Back to Seasons", 'abyss_seasons_menu'),
                  ("« Back to Menu", 'main_menu')])]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))
