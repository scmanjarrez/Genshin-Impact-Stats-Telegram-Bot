# SPDX-License-Identifier: MIT

# Copyright (c) 2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from threading import Thread, Event

import paimon_gui as gui
import utils as ut


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

    def run(self):
        warn = self.timer - WARN_THLD if self.timer > WARN_THLD else self.timer
        while not self.flag.wait(warn):
            timer = gui.update_notes(self.update)
            if timer == 0:
                self.notify("‼ Hey, your resin has reached the cap!")
                self.flag.set()
            else:
                if timer <= WARN_THLD:
                    self.notify("❗ Hey, your resin is over 150!")
                warn = timer
