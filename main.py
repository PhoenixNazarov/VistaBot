import bot
import users
import admin_panel
import rates

import threading
import time
import json


class Data:
    def __init__(self):
        self.perc_vst = 1
        self.perc_fiat = 0.5
        self.faq = []
        self.card_eur = ''
        self.card_usd = ''

        self.load()

    def to_json(self):
        return {
            'perc_vst': self.perc_vst,
            'perc_fiat': self.perc_fiat,
            'faq': self.faq,
            'card_usd': self.card_usd,
            'card_eur': self.card_eur
        }

    def save(self):
        with open('base/faq.json', 'w') as file:
            file.write(json.dumps(self.faq))

        with open('base/settings.json', 'w') as file:
            file.write(json.dumps({
                'perc_vst': self.perc_vst,
                'perc_fiat': self.perc_fiat,
                'card_usd': self.card_usd,
                'card_eur': self.card_eur
            }))

    def load(self):
        with open('base/faq.json', 'r') as file:
            self.faq = json.loads(file.read())

        with open('base/settings.json', 'r') as file:
            _base = json.loads(file.read())
            self.perc_fiat = _base['perc_fiat']
            self.perc_vst = _base['perc_vst']
            self.card_usd = _base['card_usd']
            self.card_eur = _base['card_eur']


class Config:
    def __init__(self):
        self.Data = Data()
        self.Rates = rates.Rates()
        self.Asks = users.Asks(self)
        self.Deals = users.Deals(self)
        self.Users = users.Users()
        self.Bot = bot.Bot(self)
        self.Admin_panel = admin_panel.Admin_panel(self)

        users.Ask_ch.Rates = self.Rates
        users.Ask_ch.Data = self.Data
        users.Deal_ch.Data = self.Data

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
            self.Data.save()
            self.Deals.save()
            time.sleep(1)




if __name__ == '__main__':
    Config = Config()
    Config.initiate()
