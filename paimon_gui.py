# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2023 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

import calendar
import datetime
from typing import List, Tuple

import database as db
import utils as ut
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest


async def _answer(update: Update, msg: str = None) -> None:
    if update.callback_query is not None:
        try:
            await update.callback_query.answer(msg)
        except BadRequest:
            pass


def button(buttons: List[Tuple[str, str]]):
    return [InlineKeyboardButton(bt[0], callback_data=bt[1]) for bt in buttons]


async def main_menu(update: Update) -> None:
    await _answer(update)
    kb = [
        button([("🗒 Daily Notes 🗒", "notes_menu")]),
        button([("📖 Traveler's Diary 📖", "diary_month_menu")]),
        button([("✨ Abyss ✨", "abyss_seasons_menu")]),
        button([("⚙️ Notifications ⚙️", "notifications_menu")]),
    ]
    resp = ut.send
    if update.callback_query is not None:
        resp = ut.edit
    await resp(update, "Menu", reply_markup=InlineKeyboardMarkup(kb))


async def notes_menu(update: Update, context: ut.Context) -> None:
    ut.autoupdate_notes(update, context)
    msg, notes_data = await ut.notes(ut.uid(update))
    await _answer(update)
    ut.notifier_resin(update, context, notes_data.resin_time)
    ut.notifier_teapot(update, context, notes_data)
    ut.notifier_parametric(update, context, notes_data.parametric_time)
    ut.notifier_expedition(update, context, notes_data.expeditions_max)
    kb = [
        button([("🔃 Update 🔃", "notes_menu")]),
        button([("« Back to Menu", "main_menu")]),
    ]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))


async def update_notes(
    update: Update, context: ut.Context, data: Tuple[str, ut.Notes] = None
) -> None:
    if data is None:
        msg, notes_data = await ut.notes(ut.uid(update))
    else:
        msg, notes_data = data
    ut.notifier_resin(update, context, notes_data.resin_time)
    ut.notifier_teapot(update, context, notes_data)
    ut.notifier_parametric(update, context, notes_data.parametric_time)
    ut.notifier_expedition(update, context, notes_data.expeditions_max)
    kb = [
        button([("🔃 Update 🔃", "notes_menu")]),
        button([("« Back to Menu", "main_menu")]),
    ]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))


async def diary_month_menu(update: Update) -> None:
    await _answer(update)
    month = datetime.datetime.now().month
    kb = [
        button(
            [
                (calendar.month_name[month], f"diary_menu_{month}"),
                (calendar.month_name[month - 1], f"diary_menu_{month-1}"),
                (calendar.month_name[month - 2], f"diary_menu_{month-2}"),
            ]
        ),
        button([("« Back to Menu", "main_menu")]),
    ]
    await ut.edit(update, "Traveler's Diary", InlineKeyboardMarkup(kb))


async def diary_menu(update: Update, month: int) -> None:
    msg = await ut.diary(ut.uid(update), month)
    await _answer(update)
    kb = [
        button(
            [
                ("« Back to Diary", "diary_month_menu"),
                ("« Back to Menu", "main_menu"),
            ]
        )
    ]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))


async def abyss_seasons_menu(update: Update) -> None:
    await _answer(update)
    kb = [
        button(
            [
                ("Current", "abyss_floors_menu"),
                ("Previous", "abyss_floors_menu_previous"),
            ]
        ),
        button([("« Back to Menu", "main_menu")]),
    ]
    if update.callback_query is not None:
        resp = ut.edit
    await resp(update, "Abyss Seasons", reply_markup=InlineKeyboardMarkup(kb))


async def abyss_floors_menu(update: Update, previous: bool) -> None:
    await _answer(update)
    suffix = ""
    season = "current"
    if previous:
        suffix = "_previous"
        season = "previous"
    kb = [
        button([("All", f"abyss_menu{suffix}_all")]),
        button(
            [
                ("9", f"abyss_menu{suffix}_9"),
                ("10", f"abyss_menu{suffix}_10"),
                ("11", f"abyss_menu{suffix}_11"),
                ("12", f"abyss_menu{suffix}_12"),
            ]
        ),
        button(
            [
                ("« Back to Seasons", "abyss_seasons_menu"),
                ("« Back to Menu", "main_menu"),
            ]
        ),
    ]
    if update.callback_query is not None:
        resp = ut.edit
    await resp(
        update,
        f"Abyss Floors ({season})",
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def abyss_menu(update: Update, previous: bool, floor: str) -> None:
    msg = await ut.abyss(ut.uid(update), previous, floor)
    await _answer(update)
    suffix = ""
    if previous:
        suffix = "_previous"

    kb = [
        button([("🔃 Update 🔃", f"abyss_menu{suffix}_{floor}")]),
        button(
            [
                ("« Back to Floors", f"abyss_floors_menu{suffix}"),
                ("« Back to Seasons", "abyss_seasons_menu"),
                ("« Back to Menu", "main_menu"),
            ]
        ),
    ]
    await ut.edit(update, msg, InlineKeyboardMarkup(kb))


def notification_icon(value: int) -> str:
    return "🔔" if value == 1 else "🔕"


async def notifications_menu(update: Update) -> None:
    await _answer(update)
    uid = ut.uid(update)
    kb = [
        button(
            [
                (
                    f"Resin ({db.resin(uid)}): "
                    f"{notification_icon(db.resin_warn(uid))}",
                    "notification_toggle_resin",
                )
            ]
        ),
        button(
            [
                (
                    f"Teapot Currency ({db.teapot(uid)}): "
                    f"{notification_icon(db.teapot_warn(uid))}",
                    "notification_toggle_teapot",
                )
            ]
        ),
        button(
            [
                (
                    f"Pt.Transformer: "
                    f"{notification_icon(db.parametric_warn(uid))}",
                    "notification_toggle_parametric",
                )
            ]
        ),
        button(
            [
                (
                    f"Expeditions: "
                    f"{notification_icon(db.expedition_warn(uid))}",
                    "notification_toggle_expedition",
                )
            ]
        ),
        button([("« Back to Menu", "main_menu")]),
    ]
    await ut.edit(update, "Notifications", InlineKeyboardMarkup(kb))


async def notification_toggle(update: Update, toggle: str) -> None:
    await _answer(update)
    uid = ut.uid(update)
    if toggle == "resin":
        db.toggle_resin_warn(uid)
    elif toggle == "teapot":
        db.toggle_teapot_warn(uid)
    elif toggle == "parametric":
        db.toggle_parametric_warn(uid)
    elif toggle == "expedition":
        db.toggle_expedition_warn(uid)
    await notifications_menu(update)
