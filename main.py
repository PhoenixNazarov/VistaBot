import bot
import users
import admin_panel
import rates

import threading
import time


class Config:
    def __init__(self):
        self.Rates = rates.Rates()
        self.Asks = users.Asks()
        self.Users = users.Users()
        self.Bot = bot.Bot(self)
        self.Admin_panel = admin_panel.Admin_panel(self)

    def initiate(self):
        threading.Thread(target = self.Rates.updater).start()
        print('Rates has started')
        time.sleep(1)

        threading.Thread(target = self.Bot.initiate).start()
        print('Bot has started')
        time.sleep(1)

        threading.Thread(target = self.saving_base).start()
        print('Saving_base has started')
        time.sleep(1)

        threading.Thread(target = self.Admin_panel.initiate).start()
        print('Admin_panel has started')

    def saving_base(self):
        while 1:
            self.Users.save()
            self.Asks.save()
            time.sleep(1)




if __name__ == '__main__':
    Config = Config()
    Config.initiate()
