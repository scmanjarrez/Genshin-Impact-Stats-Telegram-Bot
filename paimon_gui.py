# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

import genshinstats as gs
import utils as ut


def _answer(update, msg=None):
    if update.callback_query is not None:
        try:
            update.callback_query.answer(msg)
        except BadRequest:
            pass


def button(buttons):
    return [InlineKeyboardButton(bt[0], callback_data=bt[1]) for bt in buttons]


def main_menu(update):
    _answer(update)
    kb = [button([("🗒 Daily Notes 🗒", 'notes_menu')]),
          button([("✨ Abyss ✨", 'abyss_seasons_menu')])]
    resp = ut.send
    if update.callback_query is not None:
        resp = ut.edit
    resp(update, "Menu", reply_markup=InlineKeyboardMarkup(kb))


def notes_menu(update, context):
    ut.autoupdate_notes(context.job_queue, update)
    notes = gs.get_notes(ut.config('uid'))
    ut.notifier(context.job_queue, update, notes['until_resin_limit'])
    _answer(update)
    claimed = 'Claimed' if notes['claimed_commission_reward'] else 'Unclaimed'
    msg = (f"<b>Resin:</b> <code>{notes['resin']}/{notes['max_resin']} "
           f"({ut.fmt_seconds(notes['until_resin_limit'])})</code>\n"

           f"<b>Teapot Currency:</b> <code>{notes['realm_currency']}/"
           f"{notes['max_realm_currency']} "
           f"({ut.fmt_seconds(notes['until_realm_currency_limit'])})</code>\n"

           f"<b>Commissions:</b> "
           f"<code>{notes['completed_commissions']}/"
           f"{notes['total_commissions']} ({claimed})</code>\n"

           f"<b>Weekly Boss Discounts:</b> "
           f"<code>{notes['remaining_boss_discounts']}/"
           f"{notes['max_boss_discounts']}</code>\n"

           f"<b>Expeditions:</b>\n"
           f"{ut.fmt_expeditions(notes['expeditions'])}\n"

           f"<code>Last updated: {ut.last_updated()}</code>")
    kb = [button([("🔃 Update 🔃", 'notes_menu')]),
          button([("« Back to Menu", 'main_menu')])]
    ut.edit(update, msg, InlineKeyboardMarkup(kb))


def update_notes(queue, update):
    notes = gs.get_notes(ut.config('uid'))
    ut.notifier(queue, update, notes['until_resin_limit'])
    claimed = 'Claimed' if notes['claimed_commission_reward'] else 'Unclaimed'
    msg = (f"<b>Resin:</b> <code>{notes['resin']}/{notes['max_resin']} "
           f"({ut.fmt_seconds(notes['until_resin_limit'])})</code>\n"

           f"<b>Teapot Currency:</b> <code>{notes['realm_currency']}/"
           f"{notes['max_realm_currency']} "
           f"({ut.fmt_seconds(notes['until_realm_currency_limit'])})</code>\n"

           f"<b>Commissions:</b> "
           f"<code>{notes['completed_commissions']}/"
           f"{notes['total_commissions']} ({claimed})</code>\n"

           f"<b>Weekly Boss Discounts:</b> "
           f"<code>{notes['remaining_boss_discounts']}/"
           f"{notes['max_boss_discounts']}</code>\n"

           f"<b>Expeditions:</b>\n"
           f"{ut.fmt_expeditions(notes['expeditions'])}\n"

           f"<code>Last updated: {ut.last_updated()}</code>")
    kb = [button([("🔃 Update 🔃", 'notes_menu')]),
          button([("« Back to Menu", 'main_menu')])]
    ut.edit(update, msg, InlineKeyboardMarkup(kb))


def abyss_seasons_menu(update):
    _answer(update)
    kb = [button([("Current", 'abyss_floors_menu'),
                  ("Previous", 'abyss_floors_menu_previous')]),
          button([("« Back to Menu", 'main_menu')])]
    if update.callback_query is not None:
        resp = ut.edit
    resp(update, "Abyss Seasons", reply_markup=InlineKeyboardMarkup(kb))


def abyss_floors_menu(update, previous):
    _answer(update)
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
    resp(update, f"Abyss Floors ({season})",
         reply_markup=InlineKeyboardMarkup(kb))


def abyss_menu(update, previous, floor):
    abyss = gs.get_spiral_abyss(ut.config('uid'), previous)
    _answer(update)
    suffix = ''
    season = "Current Season"
    if previous:
        suffix = '_previous'
        season = "Previous Season"
    msg = (f"<b>⚜ {season} ⚜\n\n</b>"

           f"<b>Deepest Descent:</b> "
           f"<code>{abyss['stats']['max_floor']}</code>\n"

           f"<b>Battles Fought:</b> <code>{abyss['stats']['total_battles']} "
           f"({abyss['stats']['total_stars']}*)</code>\n"

           f"<b>Floors:</b>\n"
           f"{ut.fmt_floors(abyss['floors'], floor, previous)}")
    kb = [button([("🔃 Update 🔃", f'abyss_menu{suffix}_{floor}')]),
          button([("« Back to Floors", f'abyss_floors_menu{suffix}'),
                  ("« Back to Seasons", 'abyss_seasons_menu'),
                  ("« Back to Menu", 'main_menu')])]
    ut.edit(update, msg, InlineKeyboardMarkup(kb))
