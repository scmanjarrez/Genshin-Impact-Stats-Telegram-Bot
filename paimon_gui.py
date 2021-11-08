# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
import genshinstats as gs
import threads as th
import util as ut
import paimon


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
          button([("🌟 Abyss 🌟", 'abyss_menu')]),
          button([("⚙ Settings ⚙", 'settings_menu')])]
    resp = ut.send
    if update.callback_query is not None:
        resp = ut.edit
    resp(update, "Menu", reply_markup=InlineKeyboardMarkup(kb))


def notes_menu(update, context):
    ut.autoupdate_notes(context.job_queue, update)
    notes = gs.get_notes(paimon.CONFIG['uid'])
    _answer(update)
    th.new_thread(update, notes['until_resin_limit'])
    claimed = 'Claimed' if notes['claimed_commission_reward'] else 'Unclaimed'
    msg = (f"<b>Resin:</b> <code>{notes['resin']}/{notes['max_resin']} "
           f"({ut.fmt_sec(notes['until_resin_limit'])})</code>\n"

           f"<b>Commissions:</b> "
           f"<code>{notes['completed_commissions']}/"
           f"{notes['total_commissions']} ({claimed})</code>\n"

           f"<b>Weekly Boss Discounts:</b> "
           f"<code>{notes['remaining_boss_discounts']}/"
           f"{notes['max_boss_discounts']}</code>\n"

           f"<b>Expeditions:</b>\n"
           f"{ut.fmt_exp(notes['expeditions'])}\n"
           )
    kb = [button([("🔃 Update 🔃", 'notes_menu')]),
          button([("« Back to Menu", 'main_menu')])]
    ut.edit(update, msg, InlineKeyboardMarkup(kb))


def abyss_menu(update):
    _answer(update, "Not yet implemented.")


def settings_menu(update):
    _answer(update, "Not yet implemented.")
