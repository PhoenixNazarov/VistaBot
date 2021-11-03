import bot
import bot_show
import admin_panel
import rates

import threading
import time


class Config:
    def __init__(self):
        self.Rates = rates.Rates()
        self.Bot = bot.Bot(self)
        self.BotShow = bot_show.BotShow(self)
        self.Admin_panel = admin_panel.Admin_panel(self)

    def initiate(self):
        # time.sleep(5)
        threading.Thread(target = self.Rates.updater).start()
        print('Rates has started')
        time.sleep(0.5)

        threading.Thread(target = self.Bot.initiate).start()
        print('Bot has started')
        time.sleep(0.5)

        threading.Thread(target = self.Admin_panel.initiate).start()
        print('Admin_panel has started')
        time.sleep(0.5)

        threading.Thread(target = self.BotShow.initiate).start()
        print('Bot_show has started')


if __name__ == '__main__':
    Config = Config()
    Config.initiate()