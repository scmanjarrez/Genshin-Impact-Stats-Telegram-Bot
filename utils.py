# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram import Bot, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, JobQueue
from telegram.constants import ParseMode
from telegram.error import BadRequest
from typing import List, Tuple, Union
from enum import Enum

import paimon_gui as gui
import traceback
import calendar
import datetime
import genshin
import json
import pytz


# Global
CONF_FILE = '.config.json'
CONFIG = None
CLIENT = {}
UPD_TIME = 4 * 60 * 60  # update every 4 hours
WARN_TIME = 10 * 8 * 60  # 10 resin time
FLOORS = ('9', '10', '11', '12')

# Type aliases
Context = ContextTypes.DEFAULT_TYPE
TimeDelta = datetime.timedelta
ExpChars = List[genshin.models.genshin.chronicle.notes.Expedition]
Floors = List[genshin.models.genshin.chronicle.abyss.Floor]
Battles = List[genshin.models.genshin.chronicle.abyss.Battle]
Stats = genshin.models.genshin.chronicle.abyss.CharacterRanks
StatChars = List[genshin.models.genshin.chronicle.abyss.AbyssRankCharacter]


class CMD(Enum):
    NOP = ''
    GIFT = 'redeem'


def set_up() -> None:
    global CONFIG, CLIENT
    with open(CONF_FILE) as f:
        CONFIG = json.load(f)
    for acc in CONFIG['accounts']:
        CLIENT[acc] = genshin.Client(
            {
                'ltoken': account(acc, 'ltoken'),
                'ltuid': account(acc, 'ltuid'),
                'account_id': account(acc, 'ltuid'),
                'cookie_token': account(acc, 'ctoken')
            }
        )
        CLIENT[acc].default_game = 'genshin'


def setting(key: str) -> str:
    return CONFIG['settings'][key]


def account(uid: str, key: str) -> Union[str, int]:
    return CONFIG['accounts'][uid][key]


def uid(update: Update) -> str:
    return str(update.effective_message.chat.id)


async def send(update: Update, msg: str, button: bool = False,
               quote: bool = True,
               reply_markup: InlineKeyboardMarkup = None) -> None:
    if button:
        await (update
               .callback_query
               .message.chat.send_message(msg, ParseMode.HTML))
    else:
        await (update
               .message
               .reply_html(msg, quote=quote, reply_markup=reply_markup,
                           disable_web_page_preview=True))


async def send_bot(bot: Bot, uid: int, msg: str,
                   reply_markup: InlineKeyboardMarkup = None) -> None:
    await (bot
           .send_message(uid, msg, ParseMode.HTML, reply_markup=reply_markup,
                         disable_web_page_preview=True))


async def edit(update: Update, msg: str,
               reply_markup: InlineKeyboardMarkup = None) -> None:
    try:
        await (update
               .callback_query
               .edit_message_text(msg, ParseMode.HTML,
                                  reply_markup=reply_markup,
                                  disable_web_page_preview=True))
    except BadRequest as br:
        if not str(br).startswith("Message is not modified:"):
            print(f"***  Exception caught in edit "
                  f"({update.effective_message.chat.id}): ", br)
            traceback.print_stack()


def _remove_job(queue: JobQueue, name: str) -> None:
    current_jobs = queue.get_jobs_by_name(name)
    if current_jobs:
        for job in current_jobs:
            # print(f"INFO: Removing job: {name}")
            job.schedule_removal()


async def daily_callback(context: Context = None) -> None:
    for uid, client in CLIENT.items():
        try:
            # reward = await client.claim_daily_reward()
            await client.claim_daily_reward()
        except genshin.AlreadyClaimed:
            # print(f"INFO: Daily already claimed: {uid}")
            pass
        else:
            # print(f"INFO: Claimed {reward.amount}x {reward.name}")
            pass


async def daily_checkin(context: Context) -> None:
    await daily_callback()
    midnight = datetime.time(
        minute=10, tzinfo=pytz.timezone('Asia/Shanghai'))
    context.job_queue.run_daily(
        daily_callback, midnight, name='daily_checkin')


async def update_notes(context: Context) -> None:
    await gui.update_notes(context.job.data, context)


def autoupdate_notes(update: Update, context: Context) -> None:
    queue = context.job_queue
    _remove_job(queue, f'autoupdate_notes_{uid(update)}')
    queue.run_repeating(
        update_notes, UPD_TIME,
        name=f'autoupdate_notes_{uid(update)}', data=update)


async def notify(context: Context) -> None:
    update = context.job.data
    msg, remaining, parametric = await notes(uid(update))
    seconds = remaining.seconds
    if not seconds:
        await send(update, "‼ Hey, your resin has reached the cap!",
                   button=True)
    else:
        if seconds <= WARN_TIME:
            await send(update, "❗ Hey, your resin is over 150!",
                       button=True)
        notifier(update, context, remaining)
    await gui.update_notes(update, context, (msg, remaining, parametric))


def notifier(update: Update, context: Context, remaining: TimeDelta) -> None:
    queue = context.job_queue
    _remove_job(queue, f'notifier_{uid(update)}')
    seconds = remaining.seconds
    if seconds:
        warn = seconds - WARN_TIME
        if warn <= 0:
            warn = seconds
        queue.run_once(
            notify, warn,
            name=f'notifier_{uid(update)}', data=update)


async def notify_parametric(context: Context) -> None:
    update = context.job.data
    await send(update, "‼ Hey, your parametric is out of cooldown!",
               button=True)


def notifier_parametric(update: Update, context: Context,
                        parametric: TimeDelta) -> None:
    queue = context.job_queue
    if not queue.get_jobs_by_name(f'parametric_{uid(update)}'):
        queue.run_once(
            notify_parametric, parametric,
            name=f'parametric_{uid(update)}', data=update)


def last_updated() -> str:
    return datetime.datetime.now(
        pytz.timezone(setting('timezone'))).strftime('%Y/%m/%d %H:%M:%S')


async def redeem(uid: str, code: str) -> None:
    try:
        await CLIENT[uid].redeem_code(code)
    except genshin.errors.RedemptionException as e:
        msg = e.msg
    else:
        msg = "Code redeemed successfully."
    return msg


async def notes(uid: str) -> Tuple[str, TimeDelta, TimeDelta]:
    data = await CLIENT[uid].get_genshin_notes(account(uid, 'uid'))
    claimed = 'Claimed' if data.claimed_commission_reward else 'Unclaimed'
    msg = (
        f"<b>Resin:</b> "
        f"<code>"
        f"{data.current_resin}/{data.max_resin} "
        f"({data.remaining_resin_recovery_time})"
        f"</code>\n"

        f"<b>Teapot Currency:</b> "
        f"<code>"
        f"{data.current_realm_currency}/{data.max_realm_currency} "
        f"({data.remaining_realm_currency_recovery_time})"
        f"</code>\n"

        f"<b>Parametric Transformer:</b> "
        f"<code>"
        f"{data.remaining_transformer_recovery_time}"
        f"</code>\n"

        f"<b>Commissions:</b> "
        f"<code>"
        f"{data.completed_commissions}/{data.max_commissions} ({claimed})"
        f"</code>\n"

        f"<b>Weekly Boss Discounts:</b> "
        f"<code>"
        f"{data.remaining_resin_discounts}/{data.max_resin_discounts}"
        f"</code>\n"

        f"<b>Expeditions:</b>\n"
        f"{fmt_exp_chars(data.expeditions)}\n"

        f"<b>Last updated</b>: <code>{last_updated()}</code>"
    )
    return (msg, data.remaining_resin_recovery_time,
            data.remaining_transformer_recovery_time)


def fmt_exp_chars(characters: ExpChars) -> str:
    exp = [f"    - {chr.character.name} => "
           f"<code>"
           f"{chr.remaining_time if not chr.finished else 'Finished'}"
           f"</code>\n"
           for chr in characters]
    return "".join(exp)


async def diary(uid: str, month: int) -> str:
    info = await CLIENT[uid].get_diary(month=month)
    msg = [f"<b>Primogems earned in {calendar.month_name[month]}</b>: "
           f"<code>{info.data.current_primogems}</code>"]
    for category in info.data.categories:
        msg.append(f"    - {category.name}: "
                   f"<code>{category.amount} "
                   f"({category.percentage} %)</code>")
    return "\n".join(msg)


async def abyss(uid: str, previous: bool = False, floor: str = 'all') -> str:
    data = await CLIENT[uid].get_spiral_abyss(
        account(uid, 'uid'), previous=previous)
    sea = "Current"
    if previous:
        sea = 'Previous'

    msg = (f"⚜ <b>{sea} Season</b> ⚜\n\n"
           f"<b>Summary</b>:\n"
           f"    - <b>Deepest Descent:</b> "
           f"<code>"
           f"{data.max_floor}"
           f"</code>\n"

           f"    - <b>Battles Fought:</b> "
           f"<code>"
           f"{data.total_battles} ({data.total_stars} ⭐️)"
           f"</code>\n\n"

           f"{fmt_stats(data.ranks)}"


           f"{fmt_floors(data.floors, floor)}")
    return msg


def _floor(floors: Floors, floor: str) -> Floors:
    if floor in FLOORS:
        return [fl for fl in floors if str(fl.floor) == floor]
    else:
        return [fl for fl in floors if str(fl.floor) in FLOORS]


def fmt_floors(floors: Floors, floor: str) -> str:
    data = _floor(floors, floor)
    msg = ""
    parsed = "\n".join([
        "".join([(f"    - <b>{fl.floor} - {ch.chamber}</b>: "
                  f"{ch.stars}/{ch.max_stars} ⭐️\n"
                  f"{fmt_battle_chars(ch.battles)}\n")
                 for ch in fl.chambers])
        for fl in data])
    if parsed:
        msg = f"<b>Floors:</b>\n{parsed}"
    return msg


def fmt_battle_chars(battles: Battles) -> str:
    msg = []
    for battle in battles:
        half = [char.name for char in battle.characters]
        msg.append(f"    » <code>{', '.join(half)}</code>")
    return "\n".join(msg)


def fmt_stats(stats: Stats) -> str:
    chars = sum([len(getattr(stats, category)) for category in stats.dict()])
    msg = ""
    if chars:
        msg = (f"<b>Stats</b>:\n"
               f"    - <b>Most played</b>:\n"
               f"{fmt_stat_chars(stats.most_played)}\n"
               f"    - <b>Most kills</b>:\n"
               f"{fmt_stat_chars(stats.most_kills)}\n"
               f"    - <b>Strongest strike</b>:\n"
               f"{fmt_stat_chars(stats.strongest_strike)}\n"
               f"    - <b>Most damage taken</b>:\n"
               f"{fmt_stat_chars(stats.most_damage_taken)}\n"
               f"    - <b>Most bursts used</b>:\n"
               f"{fmt_stat_chars(stats.most_bursts_used)}\n"
               f"    - <b>Most skills used</b>:\n"
               f"{fmt_stat_chars(stats.most_skills_used)}\n\n")
    return msg


def fmt_stat_chars(characters: StatChars) -> str:
    msg = []
    for ch in characters:
        msg.append(f"    » <code>{ch.name} ({ch.value})</code>")
    return "\n".join(msg)
