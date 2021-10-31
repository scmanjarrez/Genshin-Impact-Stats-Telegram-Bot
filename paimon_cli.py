# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

import genshinstats.errors as err
import genshinstats as gs
import paimon_gui as gui
import util as ut
import paimon


ADMIN = None
UID = None
STATE = None
HELP = (
    "Hello Traveler, use the following commands to interact with me:"
    "\n\n"

    "❔ /menu - Interact with me using UI."
    "\n"
    "❔ /redeem <code>[#]</code> - Redeem the gift code."
    "\n\n"

    "<b>Bot Usage</b>\n"
    "❔ /help - List of commands."
    "\n"
    "❔ /cancel - Cancel current action."
    "\n\n"

    "<i><b>Note:</b> Arguments inside brackets are optional.</i>"
)


def _state(state=ut.CMD.NOP):
    global STATE
    STATE = state


def allowed(uid):
    global ADMIN, UID
    if ADMIN is None:
        cfg = paimon.load_config()
        ADMIN = int(cfg['admin'])
        UID = int(cfg['uid'])
        gs.set_cookie(ltoken=cfg['ltoken'], ltuid=cfg['ltuid'])
    return uid == ADMIN


def bot_help(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        ut.send(update, HELP)


def menu(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        gui.main_menu(update)


def _redeem(code, msg):
    try:
        gs.redeem_code(code)
        msg = "Coded redeemed successfully."
    except err.CodeRedeemException:
        return msg


def redeem(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        msg = "❗ Argument must be a valid code."
        if context.args:
            msg = _redeem(context.args[0], msg)
        else:
            msg = "Tell me the gift code to redeem:"
            _state(ut.CMD.GIFT)


def text(update, context):
    pass


def cancel(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        if STATE != ut.CMD.NOP:
            msg = (f"The command <code>{STATE[uid].value}</code> "
                   f"has been cancelled. Anything else I can do for you?"
                   f"\n\n"
                   f"Send /help for a list of commands.")
        else:
            msg = ("No active command to cancel. "
                   "I wasn't doing anything anyway.\nZzzzz...")
            ut.send(update, msg)
        _state()
