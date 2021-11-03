import json
import time

import services
import screens

import sqlite3 as sq


class Sql:
    # need for sqlite and database.json
    def SQL(self, sql):
        print(sql)
        path = 'base/database.db'
        with sq.connect(path) as con:
            cur = con.cursor()
            cur.execute(sql)
            con.commit()
            return cur.fetchall()

    # CARDS
    def _getCard(self, id=None, idOwner=None, name=None, active=None):
        additional = 'where 1'
        if id:
            additional += f' and id = {id}'
        if idOwner:
            additional += f' and idOwner = {idOwner}'
        if name:
            additional += f' and name = "{name}"'
        if active:
            additional += f' and timeDelete is null'

        sql = f"""SELECT * FROM Cards {additional}"""
        return Card(self.SQL(sql)[0])

    def _getCards(self, idOwner, currency=None, output=None):
        additional = ''
        if currency:
            additional += f""" and currency = '{currency}'"""

        if output:
            sql = f"""SELECT {output} FROM Cards where idOwner = {idOwner} and timeDelete IS NULL {additional}"""
            return [i[0] for i in self.SQL(sql)]
        else:
            sql = f"""SELECT * FROM Cards where idOwner = {idOwner} and timeDelete IS NULL {additional}"""
            return [Card(i) for i in self.SQL(sql)]

    # USERS
    def _getUser(self, tradeId=None, telegramId=None):
        if tradeId:
            sql = f"""SELECT * FROM Users where id = {tradeId}"""
        elif telegramId:
            sql = f"""SELECT * FROM Users where telegramId = {telegramId}"""
        else:
            return None

        data = self.SQL(sql)
        if len(data) == 0:  # NOT FOUND
            return None

        return User(data[0])

    # ASKS
    def _getAsk(self, id):
        sql = f"""SELECT * from Asks where id = {id}"""
        return Ask(self.SQL(sql)[0])


class Data:
    # need for settings.json and faq.json
    def __init__(self):
        self.pathFaq = 'base/faq.json'
        self.pathSettings = 'base/settings.json'

    def __getattr__(self, item):
        if item in ['perc_fiat', 'perc_vst', 'card_usd', 'card_eur', 'moderateAsk']:
            with open(self.pathSettings, 'r') as file:
                return json.loads(file.read())[item]

        elif item in ['faq']:
            with open(self.pathFaq, 'r') as file:
                return json.loads(file.read())

        else:
            return super().__getattr__(item)

    def __setattr__(self, key, value):
        if key in ['perc_fiat', 'perc_vst', 'card_usd', 'card_eur', 'moderateAsk']:
            with open(self.pathSettings, 'r') as file:
                data = json.loads(file.read())
            data[key] = value
            with open(self.pathSettings, 'w') as file:
                file.write(json.dumps(data))

        elif key in ['faq']:
            data = value
            with open(self.pathFaq, 'w') as file:
                file.write(json.dumps(data))

        else:
            super().__setattr__(key, value)

    def to_json(self):
        with open(self.pathFaq, 'r') as file:
            faq = json.loads(file.read())
        with open(self.pathSettings, 'r') as file:
            _base = json.loads(file.read())
            perc_fiat = _base['perc_fiat']
            perc_vst = _base['perc_vst']
            card_usd = _base['card_usd']
            card_eur = _base['card_eur']
            moderateAsk = _base['moderateAsk']

        return {
            'perc_vst': perc_vst,
            'perc_fiat': perc_fiat,
            'faq': faq,
            'card_usd': card_usd,
            'card_eur': card_eur,
            'moderateAsk': moderateAsk
        }


class UsersShow:
    def __init__(self):
        self.__base = {}

    def addUser(self, id):
        self.__base.update({id: UserShow(id)})

    def tg_identification(self, message):
        if message.chat.id not in self.__base:
            self.addUser(message.chat.id)
        return self.__base[message.chat.id]


class UserShow:
    def __init__(self, id):
        self.pop_data = {}
        self.tg_id = id

    def clear(self):
        self.pop_data = {}

    def CreateFilter(self):
        have_cur = self.pop_data['d_currency']
        type = 'vst'

        if have_cur in ['veur', 'vusd']:
            type = 'fiat'

        self.pop_data.update({
            'filter': {
                'have_cur': have_cur,
                'get_cur': self.pop_data['d_scurrency'],
                'type': type,
                'index': 0,
                'id': self.tg_id
            }
        })
        return self.pop_data['filter']


class Users(Sql):
    def identification(self, message=None, tradeId=None, telegramId=None):
        if message:
            user = self._getUser(telegramId = message.chat.id)
            if user:
                user.check_tg_data(message)
                return user
            else:
                # CREATE USER
                sql = f"""INSERT INTO Users (telegramId, firstName, lastName, username, timeActive) values 
                ({message.chat.id}, '{message.chat.first_name}', '{message.chat.last_name}','{message.chat.username}',{int(time.time())})"""
                self.SQL(sql)
                return self._getUser(telegramId = message.chat.id)

        elif telegramId:
            return self._getUser(telegramId = telegramId)
        elif tradeId:
            return self._getUser(tradeId = tradeId)

    def check(self, key, value):
        sql = f"""SELECT * from Users where {key} = '{value}'"""
        data = self.SQL(sql)
        if len(data) == 0:
            return True
        return False

    def getUsers(self, output=None):
        sql = f"""SELECT * from Users"""
        users = [User(i) for i in self.SQL(sql)]
        if output == 'web':
            return [[i.trade_id, i.tg_username, i.fio] for i in users]
        else:
            return users

    def referralBonus(self, user, deal):
        if user.referral:
            referralUser = self._getUser(tradeId = user.referral)

            commission = deal.vista_commission * services.referral_bonus

            commission = round(commission, 2)

            if deal.vista_currency == 'vusd':
                referralUser.vusd += commission
                commissionCurrency = 'Vista $'
            else:
                referralUser.veur += commission
                commissionCurrency = 'Vista €'

            return commission, referralUser, commissionCurrency
        return None, None, None

    def amount(self):
        sql = "SELECT count(id) from Users"
        return int(self.SQL(sql)[0][0])


class Pop_data(Sql):
    def __init__(self, id, dict):
        self.id = id
        self.pop_data = dict

    def __setitem__(self, key, value):
        self.update({key: value})

    def __getitem__(self, item):
        if item not in self.pop_data:
            self.pop_data.update({item: ''})
        self.updateBase()
        return self.pop_data[item]

    def __contains__(self, item):
        if item in self.pop_data:
            return 1
        return 0

    def updateBase(self):
        sql = f"""UPDATE Users SET pop_data='{json.dumps(self.pop_data)}' where id = {self.id}"""
        self.SQL(sql)

    def pop(self, item):
        item = self.pop_data.pop(item)
        self.updateBase()
        return item

    def update(self, dict):
        for i in dict:
            self.pop_data.update({i: dict[i]})
        self.updateBase()


class User(Sql):
    def __init__(self, config):
        # data
        self.trade_id = config[0]
        self.tg_id = config[1]
        self.first_name = config[2]
        self.last_name = config[3]
        self.tg_username = config[4]

        # tg service
        self.position = config[5]
        self.pop_data = Pop_data(self.trade_id, json.loads(config[16]))

        # info
        self.mail = config[6]
        self.phone = config[7]
        self.fio = config[8]
        self.time_zone = config[9]
        self.rating = config[10]

        # service
        self.ban = config[11]
        self.last_active = config[12]

        # referral
        self.referral = config[13]

        self.veur = round(config[14], 2)
        self.vusd = round(config[15], 2)

    def __setattr__(self, key, value):
        databaseKeys = {'first_name': 'firstName',
                        'last_name': 'lastName',
                        'tg_username': 'username',
                        'position': 'position',
                        'mail': 'mail',
                        'phone': 'phone',
                        'fio': 'fio',
                        'time_zone': 'timeZone',
                        'rating': 'rating',
                        'ban': 'ban',
                        'last_active': 'timeActive',
                        'referral': 'referral',
                        'veur': 'balanceVEUR',
                        'vusd': 'balanceVUSD'}
        if key in databaseKeys and key in self.__dict__:
            sql = f"""UPDATE Users SET {databaseKeys[key]}='{value}' where id = {self.trade_id}"""
            self.SQL(sql)
        super().__setattr__(key, value)

    def to_json(self):
        return {
            'tg_id': self.tg_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'tg_username': self.tg_username,
            'fio': self.fio,
            'ban': self.ban,
            'position': self.position,
            'mail': self.mail,
            'phone': self.phone,
            'time_zone': self.time_zone,
            'rating': self.rating,
            'trade_id': self.trade_id,
            'cards': [i.collect_full('web') for i in self._getCards(self.trade_id)],
            'main_referral': self.referral,
            'last_active': self.last_active,
            'veur': self.veur,
            'vusd': self.vusd,
            'referrals': [[i.trade_id, i.fio] for i in self.getReferrals()],
        }

    def check_tg_data(self, message):
        if self.first_name != message.chat.first_name:
            self.first_name = message.chat.first_name
        if self.last_name != message.chat.last_name:
            self.last_name = message.chat.last_name
        if self.tg_username != message.chat.username:
            self.tg_username = message.chat.username

        if self.rating == 0:
            self.ban = 1

        self.last_active = int(time.time())

    def clear(self):
        sql = f"""UPDATE Users SET pop_data = '{'{}'}', position = '' where id = {self.trade_id}"""
        self.SQL(sql)
        self.pop_data = Pop_data(self.trade_id, {})
        self.position = ''

    # REFERRALS
    def goReferral(self, ref_id):
        if self.referral:
            return False
        if self.trade_id == ref_id:
            return False

        ref_user = self._getUser(tradeId = ref_id)
        if ref_user:
            self.referral = ref_user.trade_id

    def getReferrals(self):
        sql = f"""SELECT * from Users where referral = {self.trade_id}"""
        return [User(i) for i in self.SQL(sql)]

    # CARDS
    def addCard(self):
        name = self.pop_data.pop('name')
        currency = self.pop_data.pop('currency')

        data1 = ''
        data2 = ''
        data3 = ''
        data4 = ''
        data5 = ''

        if currency in ['veur', 'vusd']:
            if currency == 'veur':
                c_type = 've'
            else:
                c_type = 'vu'
            data1 = self.pop_data.pop('account')
            data2 = self.pop_data.pop('phone')

        elif currency == 'byn':
            c_type = 'b'
            data1 = self.pop_data.pop('bank')
            data2 = self.pop_data.pop('card_type')
            data3 = self.pop_data.pop('fio')
            data4 = self.pop_data.pop('date_end')
            data5 = self.pop_data.pop('card_number')

        else:
            type = self.pop_data.pop('type')
            if type == 'card':
                c_type = 'c'
                data1 = self.pop_data.pop('bank')
                data2 = self.pop_data.pop('card_type')
                data3 = self.pop_data.pop('card_number')
                data4 = self.pop_data.pop('fio')
            elif type == 'account':
                c_type = 'a'
                data1 = self.pop_data.pop('bank')
                data2 = self.pop_data.pop('bik')
                data3 = self.pop_data.pop('account_number')
                data4 = self.pop_data.pop('fio')
            else:
                c_type = 'p'
                data1 = self.pop_data.pop('mail')

        sql = f"""INSERT INTO Cards (idOwner, type, name, currency, data1, data2, data3, data4, data5)
        values ({self.trade_id}, '{c_type}', '{name}', '{currency}', 
        {f"'{data1}'" if data1 else 'null'}, {f"'{data2}'" if data2 else 'null'}, 
        {f"'{data3}'" if data3 else 'null'}, {f"'{data4}'" if data4 else 'null'}, 
        {f"'{data5}'" if data5 else 'null'})"""

        self.SQL(sql)

        return self.getCards()[-1].id

    def getCard(self, id):
        return self._getCard(id)

    def getCards(self, **kwargs):
        return self._getCards(self.trade_id, **kwargs)

    # ASKS
    def make_ask(self, Rates):
        ask = Ask()
        if self.pop_data['fcurrency'] in ['veur', 'vusd']:
            ask.have_currency = self.pop_data.pop('fcurrency').replace('v', '')
            ask.get_currency = self.pop_data.pop('scurrency')
            ask.type = 'vst'

            ask.fiat_cards = []
            ask.fiat_banks = None
            cards = self.getCards()
            for i in self.pop_data['cards_name']:
                if self.pop_data['cards_name'][i]:
                    for card in cards:
                        if card.name == i:
                            ask.fiat_cards.append(card.id)
                            break
            if len(ask.fiat_cards) == 0:
                return 0

        else:
            ask.have_currency = self.pop_data.pop('fcurrency')
            ask.get_currency = self.pop_data.pop('scurrency').replace('v', '')
            ask.type = 'fiat'

            ask.fiat_banks = []
            ask.fiat_cards = None
            for i in self.pop_data['banks']:
                if self.pop_data['banks'][i]:
                    ask.fiat_banks.append(i)

        ask.show_rate = round(self.pop_data.pop('rate'), 2)
        ask.rate = Rates.get_count_rate(ask.have_currency, ask.get_currency, ask.show_rate)

        ask.min_incomplete = None
        if self.pop_data['incomplete']:
            ask.min_incomplete = self.pop_data['count_incomplete']

        ask.have_currency_count = self.pop_data.pop('count')
        ask.vst_card = self.pop_data.pop('vstcard')
        ask.trade_id_owner = self.trade_id
        ask.rating = self.rating
        ask.time_zone = self.time_zone
        return ask

    def CreateFilter(self):
        have_cur = self.pop_data['d_currency']
        type = 'vst'
        banks = []
        if have_cur in ['veur', 'vusd']:
            type = 'fiat'
            cards_name = self.pop_data['d_cards_name']
            for i in cards_name:
                if cards_name[i]:
                    card = self._getCard(idOwner = self.trade_id, name = i, active = 1)
                    if card:
                        banks.append(card)
            if len(banks) == 0:
                return False
        else:
            for i in self.pop_data['d_banks']:
                if self.pop_data['d_banks'][i]:
                    banks.append(i.lower())

        self.pop_data.update({
            'filter': {
                'have_cur': have_cur,
                'get_cur': self.pop_data['d_scurrency'],
                'type': type,
                'banks': banks,
                'index': 0,
                'id': self.trade_id
            }
        })
        return self.pop_data['filter']


class Card(Sql):
    def __init__(self, config):
        # mandatory
        self.id = config[0]
        self.create_type = config[2]
        self.name = config[3]
        self.currency = config[4].upper()

        self.data1 = config[5]
        self.data2 = config[6]
        self.data3 = config[7]
        self.data4 = config[8]
        self.data5 = config[9]

        # optional
        self.bank = ''
        if self.create_type in ['c', 'a', 'b']:
            self.bank = self.data1
        elif self.create_type == 'p':
            self.bank = 'PayPal'

    def collect_full(self, show='tg'):
        if self.create_type == 've':
            text = f'{self.name}, Vista EUR\n' \
                   f'{self.data1}\n' \
                   f'{self.data2}'

        elif self.create_type == 'vu':
            text = f'{self.name}, Vista USD\n' \
                   f'{self.data1}\n' \
                   f'{self.data2}'

        elif self.create_type == 'c':
            text = f'{self.name}, Карта, {self.currency}\n' \
                   f'{self.data1}, {self.data2}\n' \
                   f'{self.data3}, {self.data4}'

        elif self.create_type == 'a':
            text = f'{self.name}, Счёт, {self.currency}\n' \
                   f'{self.data1}\n' \
                   f'Бик: {self.data2}\n' \
                   f'Номер счёта: {self.data3}\n' \
                   f'{self.data4}'

        elif self.create_type == 'p':
            text = f'{self.name}, PayPal, {self.currency}\n' \
                   f'{self.data1}'

        else:
            text = f'{self.name}, BYN\n' \
                   f'{self.data1}, {self.data2}\n' \
                   f'{self.data5}\n' \
                   f'{self.data3}, {self.data4}'

        if show == 'tg':
            return text
        elif show == 'web':
            return text.replace('\n', '<br>')

    def collect_for_deal(self):
        if self.create_type == 've':
            text = f'Vista EUR\n' \
                   f'{self.data1}\n' \
                   f'{self.data2}'

        elif self.create_type == 'vu':
            text = f'Vista USD\n' \
                   f'{self.data1}\n' \
                   f'{self.data2}'

        elif self.create_type == 'c':
            text = f'Карта, {self.currency}\n' \
                   f'{self.data1}, {self.data2}\n' \
                   f'<code>{self.data3}</code>, {self.data4}'

        elif self.create_type == 'a':
            text = f'Счёт, {self.currency}\n' \
                   f'{self.data1}\n' \
                   f'Бик: {self.data2}\n' \
                   f'Номер счёта: <code>{self.data3}</code>\n' \
                   f'{self.data4}'

        elif self.create_type == 'p':
            text = f'PayPal, {self.currency}\n' \
                   f'<code>{self.data1}</code>'

        else:
            text = f'BYN\n' \
                   f'{self.data1}, {self.data2}\n' \
                   f'<code>{self.data3}</code>\n' \
                   f'{self.data4}, {self.data5}\n'
        return text

    def remove(self):
        sql = f"""UPDATE Cards SET timeDelete = {int(time.time())} where id = {self.id}"""
        self.SQL(sql)


class Asks(Sql):
    def __init__(self):
        self.unSaveAsks = {}

    def addAsk(self, tradeId=None, oldAsk=None):
        # todo check fool (count)

        if tradeId:
            ask = self.unSaveAsks.pop(tradeId)['ask']
            self.clear()
        else:
            ask = oldAsk

        moderateAsk = Data().moderateAsk

        sql = f"""INSERT INTO Asks (idOwner {', status' if moderateAsk=='Off' else ''}, type, haveCurrency, haveCount, getCurrency, rate, rateShow, vistaCard, cards, banks, incompleteMinimal, timeUpdate) 
        VALUES ({ask.trade_id_owner}, {'"ok", ' if moderateAsk=='Off' else ''} '{ask.type}', '{ask.have_currency}', {ask.have_currency_count}, '{ask.get_currency}',
                    {ask.rate}, {ask.show_rate}, {ask.vst_card}, {f"'{ask.fiat_cards}'" if ask.fiat_cards else 'null'}, {f"'{json.dumps(ask.fiat_banks)}'" if ask.fiat_banks else 'null'},
                            {f"'{ask.min_incomplete}'" if ask.min_incomplete else 'null'}, {int(time.time())})"""
        self.SQL(sql)

        newAsk = self.getAsks(idOwner = ask.trade_id_owner)[-1]
        if oldAsk:
            newAsk.setStatus('ok')
        return newAsk

    def getAsk(self, *args, **kwargs):
        return self._getAsk(*args, **kwargs)

    def getAsks(self, idOwner=None, preview=None, limit=None, offset=None, status=None, type=None,
                haveCurrency=None, getCurrency=None, withoutIdOwner=False):
        additional = 'where 1'
        if idOwner is not None:
            if withoutIdOwner:
                additional += f' and idOwner != {idOwner}'
            else:
                additional += f' and idOwner = {idOwner}'
        if status:
            additional += f' and status = "{status}"'
        if type:
            additional += f' and type = "{type}"'
        if haveCurrency:
            additional += f' and haveCurrency = "{haveCurrency}"'
        if getCurrency:
            additional += f' and getCurrency = "{getCurrency}"'

        if limit is not None:
            additional += f' LIMIT {limit}'
        if offset is not None:
            additional += f' OFFSET {offset}'

        sql = f"""SELECT * from Asks {additional}"""

        asks = [Ask(i) for i in self.SQL(sql)]
        if preview == 'web':
            rask = []
            for i in asks:
                if i.status not in ['deal', 'removed']:
                    rask.append([i.id, i.trade_id_owner, i.button_text(), i.status])
            return rask
        else:
            return asks

    def asks_filter(self, filter):
        if filter['have_cur'] == 'all':
            return self.getAsks(idOwner = filter['id'],
                                withoutIdOwner = True,
                                limit = services.count_list_asks,
                                offset = services.count_list_asks * filter['index'],
                                status = 'ok')

        have_cur = filter['have_cur']
        get_cur = filter['get_cur']
        type = filter['type']
        idOwner = filter['id']

        if have_cur in ['veur', 'vusd']:
            have_cur = have_cur[1:]
        else:
            get_cur = get_cur[1:]

        return self.getAsks(limit = services.count_list_asks,
                            offset = services.count_list_asks * filter['index'],
                            haveCurrency = get_cur,
                            getCurrency = have_cur,
                            type = type,
                            idOwner = idOwner,
                            withoutIdOwner = True,
                            status = 'ok')

    def clear(self):
        new_ask = {}
        for i in self.unSaveAsks:
            if time.time() - self.unSaveAsks[i]['time'] < 1 * 60 * 60:
                new_ask.update({i: self.unSaveAsks[i]})
        self.unSaveAsks = new_ask

    def amount(self):
        sql = "SELECT count(id) from Asks where status = 'ok'"
        return int(self.SQL(sql)[0][0])


class Ask(Sql):
    def __init__(self, config=None):
        self.Data = Data()
        if config is None:
            return

        self.id = config[0]
        # user have vst / fiat
        self.type = config[3]
        self.status = config[2]
        self.trade_id_owner = config[1]

        self.have_currency_count = config[12]
        self.have_currency = config[4]
        self.get_currency = config[5]
        self.show_rate = config[7]
        self.rate = config[6]

        self.vst_card = config[8]

        sql = f"""SELECT timeZone,rating from Users where id={self.trade_id_owner}"""
        data = self.SQL(sql)
        self.time_zone = data[0][0]
        self.rating = data[0][1]

        # optional
        if config[9]:
            self.fiat_cards = json.loads(config[9])
        else:
            self.fiat_cards = None
        if config[10]:
            self.fiat_banks = json.loads(config[10])
        else:
            self.fiat_banks = None

        # incomplete
        self.min_incomplete = config[11]

    def setStatus(self, status):
        sql = f"""UPDATE Asks SET status = '{status}', timeUpdate = {int(time.time())} where id = {self.id}"""
        self.SQL(sql)

    def to_json(self):
        if self.type == 'vst':
            web = {
                'give': f'{self.count("have")} + {self.count("have", commission = True)}  VST {self.have_currency}',
                'get': f'{self.count("get")} + {self.count("get", commission = True)}  {self.get_currency}',
                'rate': f'({self.show_rate}) {self.rate} '
            }
        else:
            web = {
                'give': f'{self.count("have")} + {self.count("have", commission = True)} {self.have_currency}',
                'get': f'{self.count("get")} + {self.count("get", commission = True)}  VST {self.get_currency}',
                'rate': f'({self.show_rate}) {self.rate} '
            }

        if self.fiat_cards:
            fiat_cards = [self._getCard(i).collect_full('web') for i in self.fiat_cards]
        else:
            fiat_cards = None

        return {
            'id': self.id,
            'status': self.status,
            'type': self.type,
            'trade_id_owner': self.trade_id_owner,
            'have_currency_count': self.have_currency_count,
            'have_currency': self.have_currency,
            'get_currency': self.get_currency,
            'show_rate': self.show_rate,
            'rate': self.rate,
            'vst_card': self._getCard(self.vst_card).collect_full('web'),
            'fiat_cards': fiat_cards,
            'fiat_banks': self.fiat_banks,
            'time_zone': self.time_zone,
            'rating': self.rating,
            'min_incomplete': self.min_incomplete,
            'incomplete': self.incomplete_preview(),
            'web': web
        }

    def count(self, type='have', commission=False, withCommission=False):
        if commission and withCommission:
            return 'Error'

        if type == 'have':
            if commission:
                if self.type == 'vst':
                    return round(self.have_currency_count * (self.Data.perc_vst / 100), 2)
                else:
                    return round(self.have_currency_count * (self.Data.perc_fiat / 100), 2)
            elif withCommission:
                return round(self.count('have') + self.count('have', commission = True), 2)
            else:
                return round(self.have_currency_count, 2)
        else:
            if commission:
                if self.type == 'fiat':
                    return round(self.count('get') * (self.Data.perc_vst / 100), 2)
                else:
                    return round(self.count('get') * (self.Data.perc_fiat / 100), 2)
            elif withCommission:
                return round(self.count('get') + self.count('get', commission = True), 2)
            else:
                return round(self.have_currency_count * self.rate, 2)

    def can_show(self):
        if self.status == 'ok':
            return 1
        else:
            return 0

    def incomplete_preview(self):
        if self.min_incomplete:
            if self.type == 'vst':
                return f'\n\nЧастичный выкуп, минимальная сумма {self.min_incomplete} VST {self.have_currency}'
            else:
                return f'\n\nЧастичный выкуп, минимальная сумма {self.min_incomplete} {self.have_currency}'
        else:
            return ''

    def preview(self, type='original'):
        if self.type == 'vst':
            stingBanks = '\n-'.join(set([self._getCard(i).bank.lower() for i in self.fiat_cards]))
            stringGive = f'{self.count("have", withCommission = True)} VST {self.have_currency.upper()}'
            stringGet = f'{self.count("get", withCommission = True)} {self.get_currency.upper()}'
        else:
            if self.fiat_banks == ['everyone']:
                stingBanks = 'Любой'
            else:
                stingBanks = '\n-'.join(self.fiat_banks)
            stringGive = f'{self.count("have", withCommission = True)} {self.have_currency.upper()}'
            stringGet = f'{self.count("get")} VST {self.get_currency.upper()}'

        stingId = ''
        stringIncomplete = ''

        # if ask not in database, first preview
        if hasattr(self, 'id'):
            stingId = f'Информация о заявке <b>№{self.id}:</b>\n\n'
            stringIncomplete = self.incomplete_preview()

        if type == 'original':
            return f'{stingId}' \
                   f'Отдаете: <b>{stringGive}</b>\n' \
                   f'Получаете: <b>{stringGet}</b>\n' \
                   f'Курс обмена: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки: {self.rating}\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{stingBanks}\n' \
                   f'Часовой пояс: <b>{self.time_zone}</b>' \
                   f'{stringIncomplete}'
        else:
            if self.type == 'vst':
                stringGive = f'{self.count("have")} VST {self.have_currency.upper()}'
            else:
                stringGet = f'{self.count("get", withCommission = True)} VST {self.get_currency.upper()}'

            return f'{stingId}' \
                   f'Отдаете: <b>{stringGet}</b>\n' \
                   f'Получаете: <b>{stringGive}</b>\n' \
                   f'Курс обмена: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки: {self.rating}\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{stingBanks}\n' \
                   f'Часовой пояс: <b>{self.time_zone}</b>' \
                   f'{stringIncomplete}'

    def button_text(self, reverse=False):
        sign_have_currency = services.signs[self.have_currency]
        sign_get_currency = services.signs[self.get_currency]
        if not reverse:
            if self.type == 'vst':
                return f'VST {sign_have_currency} {self.count("have", withCommission = True)} ⇒ {sign_get_currency} {self.count("get", withCommission = True)} {self.show_rate}'

            return f'{sign_have_currency} {self.count("have", withCommission = True)} ⇒ VST {sign_get_currency} {self.count("get")} {self.show_rate}'
        else:
            if self.type == 'vst':
                return f'{sign_get_currency} {self.count("get", withCommission = True)} ⇒ VST {sign_have_currency} {self.count("have")} {self.show_rate}'

            return f'VST {sign_get_currency} {self.count("get", withCommission = True)} ⇒ {sign_have_currency} {self.count("have", withCommission = True)} {self.show_rate}'


class Deals(Sql):
    def makeDeal(self, user):
        ask = self._getAsk(user.pop_data.pop('d_ask_id'))
        if not ask.can_show():
            return

        if 'd_count_incomplete' in user.pop_data:
            ask.have_currency_count = user.pop_data.pop('d_count_incomplete')

        type = user.pop_data.pop('d_type')

        if type == 'vst':
            a_idTelegram = self._getUser(tradeId = ask.trade_id_owner).tg_id
            a_vistaCard = ask.vst_card
            a_cards = ask.fiat_cards

            b_idTelegram = user.tg_id
            b_vistaCard = user.pop_data.pop('d_vst_card')
            b_banks = []

            vistaCurrency = 'VST ' + ask.have_currency.upper()
            vistaCount = ask.count('have')
            vistaCommission = ask.count("have", commission = True)

            fiatCurrency = ask.get_currency.upper()
            fiatCount = ask.count("get", withCommission = True)

        else:
            cards = []
            for i in user.pop_data['d_cards_name']:
                if user.pop_data['d_cards_name'][i]:
                    cards.append(self._getCard(idOwner = user.trade_id, name = i, active = 1).id)
            if len(cards) == 0:
                return

            a_idTelegram = user.tg_id
            a_vistaCard = user.pop_data['d_vst_card']
            a_cards = cards

            b_idTelegram = self._getUser(tradeId = ask.trade_id_owner).tg_id
            b_vistaCard = ask.vst_card
            b_banks = json.dumps(ask.fiat_banks)

            vistaCurrency = 'VST ' + ask.get_currency.upper()
            vistaCount = ask.count('get')
            vistaCommission = ask.count('get', commission = True)

            fiatCurrency = ask.have_currency.upper()
            fiatCount = ask.count("have", withCommission = True)

        sql = f"""INSERT INTO Deals (id_ask, a_idTelegram, a_vistaCard, a_cards, b_idTelegram, b_vistaCard,
                                    b_banks, vistaCurrency, fiatCurrency, vistaCount, vistaCommission,
                                    fiatCount, createTime, rate, showRate) 
                    values ({ask.id}, {a_idTelegram}, '{a_vistaCard}', '{a_cards}', {b_idTelegram}, '{b_vistaCard}',
                    '{b_banks}', '{vistaCurrency}', '{fiatCurrency}', {vistaCount}, {vistaCommission},
                    {fiatCount}, {int(time.time())}, {ask.rate}, {ask.show_rate}
                            )"""
        self.SQL(sql)

        ask.setStatus('deal')

        return self.getDeals()[-1]

    def getDeals(self, preview=None, idOwner=None, active=None, date=None):
        additional = 'where 1 '
        if idOwner:
            telegramId = self._getUser(tradeId = idOwner).tg_id
            additional += f' and (a_idTelegram={telegramId} or b_idTelegram={telegramId})'
        if active == 'work':
            additional += f'and status not in ("end", "remove")'
        if active == 'end':
            additional += f'and status = "end"'
        if date:
            if date[0] != '':
                additional += f' and {date[0]} <= updateTime'
            if date[1] != '':
                additional += f' and {date[1]} >= updateTime'
            additional += f' ORDER BY updateTime'

        sql = f"""SELECT * from Deals {additional}"""
        deals = [Deal(i) for i in self.SQL(sql)]

        if preview == 'web':
            return [[i.ask_id, i.previewText('web'), i.status, i.moderate, i.cancel, i.id] for i in deals]
        elif preview == 'end':
            return [[self._getUser(telegramId = i.vista_people).trade_id,
                     self._getUser(telegramId = i.fiat_people).trade_id,
                     i.previewText('button'),
                     i.referralACount,
                     i.referralBCount,
                     i.vista_commission,
                     i.vista_count,
                     i.updateTime] for i in deals]
        else:
            return deals

    def getDeal(self, id):
        sql = f"""SELECT * from Deals where id = {id}"""
        return Deal(self.SQL(sql)[0])

    def amount(self):
        sql = "SELECT count(id) from Deals where (status != 'end' and status != 'remove')"
        return int(self.SQL(sql)[0][0])


class Deal(Sql):
    def __init__(self, config):
        # wait_vst, wait_vst_proof, wait_fiat, wait_fiat_proof, wait_garant_vst
        self.status = config[2]
        self.id = config[0]
        self.ask_id = config[1]

        # users, vista - have vista (A)
        self.vista_people = config[3]
        self.vista_people_vst_card = config[4]
        self.vista_people_fiat_card = json.loads(config[5])
        self.vista_currency = config[9]
        self.vista_count = config[11]
        self.vista_commission = config[12]
        self.vista_send_over = config[24]
        self.vista_last_notification = config[14]

        # (B)
        self.fiat_people = config[6]
        self.fiat_people_vst_card = config[7]
        self.fiat_people_banks = config[8]
        self.fiat_currency = config[10]
        self.fiat_count = config[13]
        self.fiat_send_over = config[25]
        self.fiat_last_notification = config[15]
        self.fiat_choose_card = config[26]

        # info
        self.updateTime = config[17]
        self.show_rate = config[28]
        self.rate = config[27]

        self.cancel = config[22]
        self.moderate = config[23]

        self.Data = Data()

        # referral
        self.referralA = config[18]
        self.referralB = config[19]
        self.referralACount = config[20]
        self.referralBCount = config[21]

    def __setattr__(self, key, value):
        database = {
            'fiat_choose_card': 'b_chooseCard',
            'vista_send_over': 'a_timeOver',
            'fiat_send_over': 'b_timeOver',
            'cancel': 'cancel',
            'moderate': 'moderate'}

        if key in database and key in self.__dict__:
            sql = f"""UPDATE Deals SET {database[key]} = '{value}' where id={self.id}"""
            self.SQL(sql)

        super().__setattr__(key, value)

    def getCards(self, type=None, id=None):
        if id:
            return self._getCard(id)
        if type == 'fiat_cards':
            return [self._getCard(i) for i in self.vista_people_fiat_card]
        elif type == 'fiat_choose_card':
            return self._getCard(self.fiat_choose_card)

    def updateStatus(self, status):
        self.status = status
        sql = f"""UPDATE Deals SET status='{status}', updateTime={int(time.time())} where id = {self.id}"""
        self.SQL(sql)

    def updateTimeActive(self, user):
        if user == 'a':
            sql = f"""UPDATE Deals SET timeA={int(time.time())} where id={self.id}"""
        else:
            sql = f"""UPDATE Deals SET timeB={int(time.time())} where id={self.id}"""
        self.SQL(sql)

    def previewText(self, type='button'):
        if type == 'button':
            return f'№{self.ask_id} {self.vista_count + self.vista_commission} {self.vista_currency} ⇒ {self.fiat_count} {self.fiat_currency}'
        elif type == 'web':
            return f'{self.vista_count + self.vista_commission} VST {self.vista_currency} ⇒ {self.fiat_count} {self.fiat_currency} {self.rate}'

    def garant_card(self):
        if '$' in self.vista_currency:
            return self.Data.card_usd
        else:
            return self.Data.card_eur

    def logic_message(self, user, optional=None):
        user_id = user.tg_id
        if user_id == self.vista_people:
            self.updateTimeActive('a')
        else:
            self.updateTimeActive('b')

        if self.cancel:
            return screens.deal('cancel_accept', self)

        if self.moderate:
            return screens.deal('moder_accept', self)

        if self.status == 'wait_vst':
            if user_id == self.vista_people:
                return screens.deal('1_A', self)
            else:
                return screens.deal('1_B', self)

        elif self.status == 'wait_vst_proof':
            if user_id == self.vista_people:
                return screens.deal('2_A', self)
            else:
                return screens.deal('2_B', self)

        elif self.status == 'wait_fiat':
            if user_id == self.vista_people:
                return screens.deal('3_A', self)
            else:
                if optional is not None:
                    if optional[0] == 'show':
                        return screens.deal('3_B_card', self, optional[1])
                elif not self.fiat_choose_card:
                    return screens.deal('3_B', self)
                else:
                    return screens.deal('3_B_with_card', self)

        elif self.status == 'wait_fiat_proof':
            if user_id == self.vista_people:
                return screens.deal('4_A', self)
            else:
                return screens.deal('4_B', self)

        elif self.status == 'wait_garant_vst':
            if user_id == self.vista_people:
                return screens.deal('5_A', self)
            else:
                return screens.deal('5_B', self)

        elif self.status == 'end':
            if user_id == self.vista_people:
                return screens.deal('6_A', self)
            else:
                return screens.deal('6_B', self)

    def logic_control(self, key, user):
        if key == 'moderate' or key == 'cancel':
            if self.moderate == 0 or self.cancel == 0:
                return True

        if user == 'admin':
            # 2
            if key == 'garant_accept':
                if self.status == 'wait_vst_proof':
                    self.updateStatus('wait_fiat')
                    return 1
            # 5
            if key == 'garant_send':
                if self.status == 'wait_garant_vst':
                    self.updateStatus('end')
                    return 1

        elif user.tg_id == self.vista_people:
            # 1
            if key == 'vst_sended':
                if self.status == 'wait_vst':
                    self.updateStatus('wait_vst_proof')
                    return 1
            # 4
            elif key == 'fiat_accept':
                if self.status == 'wait_fiat_proof':
                    self.updateStatus('wait_garant_vst')
                    return 1

        elif user.tg_id == self.fiat_people:
            # 3
            if key == 'fiat_sended':
                if self.status == 'wait_fiat':
                    self.updateStatus('wait_fiat_proof')
                    return 1

    def to_json(self):
        return {
            'status': self.status,
            'id': self.id,
            'ask_id': self.ask_id,
            'vista_people': self.vista_people,
            'vista_people_vst_card': self.vista_people_vst_card,
            'vista_people_fiat_card': [i for i in self.vista_people_fiat_card],
            'vista_currency': self.vista_currency,
            'vista_count': self.vista_count + self.vista_commission,
            'fiat_people': self.fiat_people,
            'fiat_people_vst_card': self.fiat_people_vst_card,
            'fiat_people_banks': self.fiat_people_banks,
            'fiat_currency': self.fiat_currency,
            'fiat_count': self.fiat_count,
            'rate': self.rate,
            'vista_count_without_com': self.vista_count,
            'vista_send_over': self.vista_send_over,
            'vista_last_notification': self.vista_last_notification,
            'fiat_send_over': self.fiat_send_over,
            'fiat_last_notification': self.fiat_last_notification,
            'fiat_choose_card': self._getCard(self.fiat_choose_card).collect_full('web'),
            'cancel': self.cancel,
            'moderate': self.moderate,
            'show_rate': self.show_rate,
            'a_vst_card': self._getCard(self.vista_people_vst_card).collect_full('web'),
            'b_vst_card': self._getCard(self.fiat_people_vst_card).collect_full('web'),
            'g_vst_card': self.garant_card().replace('\n', '<br>'),
            'a_trade_id': self._getUser(telegramId = self.vista_people).trade_id,
            'b_trade_id': self._getUser(telegramId = self.fiat_people).trade_id
        }

    def end(self):
        user_A = self._getUser(telegramId = self.vista_people)
        user_B = self._getUser(telegramId = self.fiat_people)
        user_A.rating += 1
        user_B.rating += 1

        # referral program
        referralCommission = round(self.vista_commission * services.referral_bonus, 2)

        referral_A = None
        referral_B = None

        if user_A.referral:
            referral_A = self._getUser(tradeId = user_A.referral)
        if user_B.referral:
            referral_B = self._getUser(tradeId = user_B.referral)

        if self.vista_currency == 'vusd':
            commissionCurrency = 'Vista USD'
            if referral_A:
                referral_A.vusd += referralCommission
                sql = f"""UPDATE Deals SET referralA={referral_A.trade_id}, referralACount={referralCommission} where id = {self.id}"""
                self.SQL(sql)
            if referral_B:
                referral_B.vusd += referralCommission
                sql = f"""UPDATE Deals SET referralB={referral_B.trade_id}, referralBCount={referralCommission} where id = {self.id}"""
                self.SQL(sql)
        else:
            commissionCurrency = 'Vista EUR'
            if referral_A:
                referral_A.veur += referralCommission
                sql = f"""UPDATE Deals SET referralA={referral_A.trade_id}, referralACount={referralCommission} where id = {self.id}"""
                self.SQL(sql)
            if referral_B:
                referral_B.veur += referralCommission
                sql = f"""UPDATE Deals SET referralB={referral_B.trade_id}, referralBCount={referralCommission} where id = {self.id}"""
                self.SQL(sql)
        referralMessage={
            'referral_A': referral_A,
            'referral_B': referral_B,
            'commission': referralCommission,
            'commissionCurrency': commissionCurrency
        }

        # create ask
        ask = self._getAsk(self.ask_id)
        if ask.min_incomplete:
            if ask.type == 'vst':
                remains = ask.count('have') - self.vista_count
            else:
                remains = ask.count('have') - self.fiat_count

            if remains < ask.min_incomplete:
                ask = None
            else:
                ask.have_currency_count = remains
        else:
            ask = None

        return referralMessage, ask


class ReferralWithdrawal(Sql):
    def add(self, user, cardID, currency):
        if currency == 'vusd':
            count = user.vusd
            user.vusd = 0
        else:
            count = user.veur
            user.veur = 0

        sql = f"""INSERT INTO ReferralWithdrawals (idOwner, currency, card, count, timeUpdate) 
                    values ({user.trade_id}, 
                            '{currency}', 
                            {cardID},
                            {count},
                            {int(time.time())}
                            )"""
        self.SQL(sql)

    def done(self, id):
        sql = f"""UPDATE ReferralWithdrawals SET status = 'done', timeUpdate = {int(time.time())} where id = {id}"""
        self.SQL(sql)

    def getWait(self):
        sql = """SELECT * from ReferralWithdrawals where status = 'wait'"""
        return [[i[0], i[1], i[2], self._getCard(id = i[3]).collect_full('web'), i[4]] for i in self.SQL(sql)]


class AdminNotifications(Sql):
    def get(self, time, acceptAsks, dealGetVista, dealSendVista, referralWithdrawals):
        notifications = []

        if type(time) == list:
            addTime = f'<= {time[0]}'
        else:
            addTime = f'= {time}'

        if acceptAsks:
            sql = f"SELECT * from Asks where status = 'wait_allow' and timeUpdate {addTime}"
            asks = [Ask(i) for i in self.SQL(sql)]
            for ask in asks:
                notifications.append(['ask_allow', ask.id, ask.button_text()])

        if dealGetVista:
            sql = f"SELECT * from Deals where status = 'wait_vst_proof' and updateTime {addTime}"
            deals = [Deal(i) for i in self.SQL(sql)]
            for deal in deals:
                notifications.append(['deal_getVista', deal.id, deal.ask_id,
                                      self._getCard(id=deal.vista_people_vst_card).collect_full('web'),
                                      round(deal.vista_count + deal.vista_commission,2), deal.vista_currency])

        if dealSendVista:
            sql = f"SELECT * from Deals where status = 'wait_garant_vst' and updateTime {addTime}"
            deals = [Deal(i) for i in self.SQL(sql)]
            for deal in deals:
                notifications.append(['deal_sendVista', deal.id, deal.ask_id,
                                      self._getCard(id=deal.fiat_people_vst_card).collect_full('web'),
                                      round(deal.vista_count,2), deal.vista_currency])

        if referralWithdrawals:
            sql = f"""SELECT * from ReferralWithdrawals where status = 'wait' and timeUpdate {addTime}"""
            for i in self.SQL(sql):
                notifications.append(['referralWithdrawal', i[0], i[1], i[2], self._getCard(id = i[3]).collect_full('web'), i[4]])

        # if dealCancel:
        #     sql = f"SELECT * from Deals where status = 'cancel' and updateTime > {time}"
        #     deals = [Deal(i) for i in self.SQL(sql)]
        #     for deal in deals:
        #         notifications.append(['deal_sendVista', deal.id, deal.previewText('web')])


        return notifications

    def getAnalyze(self, dealCancel, dealModerate, askTimeOver, dealUserTimeOver, dealTimeOver):
        notifications = []

        if dealCancel:
            sql = f"""SELECT * from Deals where Deals.cancel == 1 and (status != 'end' and status != 'remove')"""
            deals = [Deal(i) for i in self.SQL(sql)]
            for deal in deals:
                notifications.append(['dealCancel', deal.id, deal.ask_id])

        if dealModerate:
            sql = f"""SELECT * from Deals where moderate != 0 and (status != 'end' and status != 'remove')"""
            deals = [Deal(i) for i in self.SQL(sql)]
            for deal in deals:
                notifications.append(['dealModerate', deal.id, deal.ask_id])

        if dealUserTimeOver:
            sql = f"""SELECT * from Deals where ((a_timeOver < {int(time.time())} and a_timeOver != 0) or (b_timeOver < {int(time.time())} and b_timeOver != 0)) and (status != 'end' and status != 'remove')"""
            deals = [Deal(i) for i in self.SQL(sql)]
            for deal in deals:
                notifications.append(['dealUserTimeOver', deal.id, deal.ask_id])

        if dealTimeOver:
            sql = f"""SELECT * from Deals where updateTime < {int(time.time()) - 12*60*60} and (status != 'end' and status != 'remove')"""
            deals = [Deal(i) for i in self.SQL(sql)]
            for deal in deals:
                notifications.append(['dealOver', deal.id, deal.ask_id])

        if askTimeOver:
            sql = f"""SELECT * from Asks where timeUpdate < {int(time.time()) - 3*24*60*60} and status = 'ok'"""
            asks = [Ask(i) for i in self.SQL(sql)]
            for ask in asks:
                notifications.append(['askOver', ask.id])

        return notifications