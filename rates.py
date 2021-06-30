import requests
import time


class Rates:
    def __init__(self):
        self.eur = 85.9943
        self.usd = 72.2216
        self.byn = 28.7415

        self.rates = {}

    def get_rate(self, fiat_cur, vst_cur):
        if fiat_cur == 'usd' and vst_cur in 'eur':
            rate = self.eur / self.usd
        else:
            rate = self.rates[vst_cur] / self.rates[fiat_cur]

        return round(rate, 2)

    def get_count_rate(self, cur_have, cur_need, rate):
        if cur_have == 'rub':
            return 1 / rate
        if cur_have == 'usd' and cur_need == 'eur':
            return 1 / rate
        if cur_have == 'byn':
            return 1 / rate
        return rate

    def updater(self):
        while 1:
            time.sleep(5)
            req = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
            self.byn = req['Valute']['BYN']['Value']
            self.usd = req['Valute']['USD']['Value']
            self.eur = req['Valute']['EUR']['Value']

            self.rates = {
                'rub': 1,
                'usd': self.usd,
                'eur': self.eur,
                'byn': self.byn,
            }

            time.sleep(24 * 60)

