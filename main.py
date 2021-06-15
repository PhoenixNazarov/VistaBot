import bot
import users
import admin_panel

import threading


class Config:
    def __init__(self):
        self.Users = users.Users()
        self.Bot = bot.Bot(self)
        self.Admin_panel = admin_panel.Admin_panel(self)

    def initiate(self):
        threading.Thread(target = self.Bot.initiate).start()
        print('Bot has started')
        threading.Thread(target = self.Admin_panel.initiate).start()
        print('Admin_panel has started')


if __name__ == '__main__':
    Config = Config()
    Config.initiate()
