# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from threading import Thread, Event

import paimon_gui as gui
import util as ut


THREAD = None
WARN_THLD = 10 * 8 * 60  # first warn: 10 resin less than cap (150)


def new_thread(update, timer):
    global THREAD
    if THREAD is not None:
        THREAD[1].set()
    flag = Event()
    thread = NotifierThread(update, timer, flag)
    thread.start()
    THREAD = (thread, flag)


class NotifierThread(Thread):
    def __init__(self, update, timer, flag):
        Thread.__init__(self)
        self.update = update
        self.timer = int(timer)
        self.flag = flag
        self.notified = False
        self.daemon = True

    def notify(self, msg):
        ut.send(self.update, msg, button=True)

    def timers(self):
        prewarn = self.timer > WARN_THLD
        warn = self.timer - WARN_THLD if prewarn else self.timer
        return prewarn, warn

    def run(self):
        prewarn, warn = self.timers()
        while not self.flag.wait(warn):
            if prewarn:
                notify, timer = gui.update_notes(self.update)
                if notify:
                    self.notify("❗ Hey, your resin is 150!")
                self.timer = int(timer)
                prewarn, warn = self.timers()
            else:
                self.notify("‼ Hey, you have hit the resin cap!")
                self.flag.set()
