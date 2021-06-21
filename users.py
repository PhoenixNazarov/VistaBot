import json
import datetime
import services


class Users:
    def __init__(self):
        self.__Users = {}

        self.load()

    def load(self):
        with open('base/users.json', 'r') as file:
            _users = json.loads(file.read())

        for i in _users:
            _user = User()
            _user.load_from_json(i)
            self.__Users.update({i['tg_id']: _user})

    def save(self):
        _users = []
        for user in self.__Users.values():
            _users.append(user.to_json())

        with open('base/users.json', 'w') as file:
            file.write(json.dumps(_users))

    def tg_identification(self, message):
        if message.chat.id in self.__Users:
            _user = self.__Users[message.chat.id]
        else:
            _user = User()
            _user.tg_id = message.chat.id
            _user.trade_id = len(self.__Users) + 1
            self.__Users.update({message.chat.id: _user})

        _user.check_tg_data(message)
        return self.__Users[message.chat.id]

    def tg_id_identification(self, id):
        return self.__Users[id]

    def go_referal(self, main_user, ref_id):
        if main_user.referal_to:
            return False
        if not ref_id.isdigit():
            return False

        ref_user = None
        for i in self.__Users.values():
            if i.trade_id == int(ref_id):
                ref_user = i
                break

        if ref_user is None:
            return False

        if ref_user.tg_id in main_user.referal_list:
            return False

        ref_user.referal_list.append(main_user.tg_id)
        main_user.referal_to = ref_user.tg_id

    def find_main_referral(self, user_id):
        for i in self.__Users:
            if user_id in i.referal_list:
                return i

    def check(self, key, value):
        if key == 'mail':
            for i in self.__Users.values():
                if i.mail == value:
                    return False

        elif key == 'phone':
            for i in self.__Users.values():
                if i.phone == value:
                    return False

        return True

    # for admin
    def get_users(self):
        _json = []
        for user in self.__Users.values():
            _json.append([user.trade_id, user.tg_username, user.fio])

        return json.dumps(_json)

    def get_user(self, trade_id):
        user = None
        for i in self.__Users.values():
            if str(i.trade_id) == trade_id:
                return i

        if user is None:
            return False


class User:
    def __init__(self):
        # data
        self.tg_id = ''
        self.first_name = ''
        self.last_name = ''
        self.tg_username = ''

        # tg service
        self.position = ''
        self.pop_data = {}
        self.unsave_pop_data = {}

        # info
        self.mail = ''
        self.phone = ''
        self.fio = ''
        self.time_zone = 'МСК'
        self.rating = 10
        self.trade_id = 0
        self.cards = []

        # service
        self.ban = False
        self.last_active = ''

        # referral
        self.referal_list = []
        self.referal_to = False

    def load_from_json(self, _json):
        # add new stat
        if 'last_active' not in _json:
            _json.update({'last_active': ''})

        self.tg_id = _json['tg_id']
        self.first_name = _json['first_name']
        self.last_name = _json['last_name']
        self.tg_username = _json['tg_username']
        self.fio = _json['fio']
        self.ban = _json['ban']
        self.pop_data = _json['pop_data']
        self.position = _json['position']
        self.mail = _json['mail']
        self.phone = _json['phone']
        self.time_zone = _json['time_zone']
        self.rating = _json['rating']
        self.trade_id = _json['trade_id']
        self.referal_list = _json['referal_list']
        self.referal_to = _json['referal_to']
        self.last_active = _json['last_active']

        for i in _json['cards']:
            self.cards.append(Card(i))

    def to_json(self):
        return {
            'tg_id': self.tg_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'tg_username': self.tg_username,
            'fio': self.fio,
            'ban': self.ban,
            'position': self.position,
            'pop_data': self.pop_data,
            'mail': self.mail,
            'phone': self.phone,
            'time_zone': self.time_zone,
            'rating': self.rating,
            'trade_id': self.trade_id,
            'cards': [i.config for i in self.cards],
            'referal_list': self.referal_list,
            'referal_to': self.referal_to,
            'last_active': self.last_active
        }

    def check_tg_data(self, message):
        def check_str(_string):
            if _string is None:
                return 'none'
            for i in range(len(_string)):
                if _string[i] not in services.printable:
                    _string = _string[:i] + '?' + _string[i + 1:]
            return _string

        self.first_name = check_str(message.chat.first_name)
        self.last_name = check_str(message.chat.last_name)
        self.tg_username = check_str(message.chat.username)

        if self.rating == 0:
            self.ban = True

        self.last_active = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')

    def clear(self):
        self.pop_data = {}
        self.position = ''

    # cards
    def add_card(self):
        name = self.pop_data.pop('name')
        info_card = [name]

        currency = self.pop_data.pop('currency')
        info_card.append(currency)
        if currency in ['veur', 'vusd']:
            if currency == 'veur':
                c_type = 've'
            else:
                c_type = 'vu'
            info_card.append(self.pop_data.pop('account'))
            info_card.append(self.pop_data.pop('phone'))

        elif currency == 'byn':
            c_type = 'b'
            info_card.append(self.pop_data.pop('bank'))
            info_card.append(self.pop_data.pop('card_type'))
            info_card.append(self.pop_data.pop('fio'))
            info_card.append(self.pop_data.pop('date_end'))

        else:
            type = self.pop_data.pop('type')
            if type == 'card':
                c_type = 'c'
                info_card.append(self.pop_data.pop('bank'))
                info_card.append(self.pop_data.pop('card_type'))
                info_card.append(self.pop_data.pop('card_number'))
                info_card.append(self.pop_data.pop('fio'))
            elif type == 'account':
                c_type = 'a'
                info_card.append(self.pop_data.pop('bank'))
                info_card.append(self.pop_data.pop('bik'))
                info_card.append(self.pop_data.pop('account_number'))
                info_card.append(self.pop_data.pop('fio'))
            else:
                c_type = 'p'
                info_card.append(self.pop_data.pop('mail'))

        current_card = [c_type] + info_card

        self.cards.append(Card(current_card))

        return len(self.cards) - 1

    def remove_card(self, id):
        self.cards.pop(id)

    def names_cards(self):
        names = []
        for i in self.cards:
            names.append(i.name)
        return names

    def get_card_currency(self, currency):
        cards = []
        for i in self.cards:
            if i.currency == currency:
                cards.append(i)
        return cards

    # ask
    def make_ask(self, Rates):
        ask = Ask()
        if self.pop_data['fcurrency'] in ['veur', 'vusd']:
            ask.have_currency = self.pop_data.pop('fcurrency').replace('v', '')
            ask.get_currency = self.pop_data.pop('scurrency')
            ask.type = 'vst'

            for i in self.pop_data['cards_name']:
                if self.pop_data['cards_name'][i]:
                    for card in self.cards:
                        if card.name == i:
                            ask.fiat_cards.append(card)

        else:
            ask.have_currency = self.pop_data.pop('fcurrency')
            ask.get_currency = self.pop_data.pop('scurrency').replace('v', '')
            ask.type = 'fiat'

            for i in self.pop_data['banks']:
                if self.pop_data['banks'][i]:
                    ask.fiat_banks.append(i)

        ask.have_currency_count = self.pop_data.pop('count')
        ask.show_rate = self.pop_data.pop('rate')
        ask.rate = Rates.get_count_rate(ask.have_currency, ask.get_currency)
        ask.vst_cards = self.pop_data.pop('vstcard')
        ask.trade_id_owner = self.trade_id
        return ask


class Card:
    def __init__(self, config):
        # mandatory
        self.name = ''
        self.currency = ''
        self.text = ''

        # service
        self.config = config
        self.create_type = ''

        # optional
        self.bank = ''

        self.create()

    def __str__(self):
        return self.name

    def create(self):
        self.create_type = self.config[0]
        self.name = self.config[1]
        self.currency = self.config[2]

        if self.create_type in ['c', 'a', 'b']:
            self.bank = self.config[3]

    def collect_full(self, show = 'tg'):
        if self.create_type == 've':
            text = f'{self.name}, Vista EUR\n' \
                   f'{self.config[3]}\n' \
                   f'{self.config[4]}'

        elif self.create_type == 'vu':
            text = f'{self.name}, Vista USD\n' \
                   f'{self.config[3]}\n' \
                   f'{self.config[4]}'

        elif self.create_type == 'c':
            text = f'{self.name}, Карта, {self.config[2]}\n' \
                   f'{self.config[3]}, {self.config[4]}\n' \
                   f'{self.config[5]}, {self.config[6]}'\

        elif self.create_type == 'a':
            text = f'{self.name}, Счёт, {self.config[2]}\n' \
                   f'{self.config[3]}\n' \
                   f'Бик: {self.config[4]}\n' \
                   f'Номер счёта: {self.config[5]}\n' \
                   f'{self.config[6]}'

        elif self.create_type == 'p':
            text = f'{self.name}, PayPal, {self.config[2]}\n' \
                   f'{self.config[3]}'

        else:
            text = f'{self.name}, BYN\n' \
                   f'{self.config[3]}, {self.config[4]}\n' \
                   f'{self.config[5], self.config[6]}'

        if show == 'tg':
            return text
        elif show == 'web':
            return text.replace('\n', '<br>')


class Asks:
    def __init__(self):
        self.__asks = {}
        self.path = 'base/asks.json'
        self.numb = 1

        self.load()

    def add_ask(self, ask):
        # todo check fool
        ask.id = self.numb
        self.numb += 1
        self.__asks.update({ask.id: ask})
        return ask

    def load(self):
        with open(self.path, 'r') as file:
            dc = json.loads(file.read())

        for i in dc:
            _ask = Ask()
            _ask.load_from_json(i)
            self.__asks.update({i['id']: _ask})

    def save(self):
        dc = []
        for i in self.__asks.values():
            dc.append(i.to_json())

        with open(self.path, 'w') as file:
            file.write(json.dumps(dc))

    def get_asks(self, trade_id):
        asks = []
        for i in self.__asks.values():
            if i.trade_id_owner == trade_id:
                asks.append(i)
        return asks

    def get_ask_from_id(self, id):
        return self.__asks[id]

    def remove_ask(self, id):
        return self.__asks.pop(int(id))


class Ask:
    def __init__(self):
        # user have vst / fiat
        self.type = 'vst'
        self.trade_id_owner = 0
        self.id = -1

        self.have_currency_count = 0
        self.have_currency = ''
        self.get_currency = ''
        self.show_rate = 0
        self.rate = 0

        self.vst_card = []

        # optional
        self.fiat_cards = []
        self.fiat_banks = []

    def to_json(self):
        return {
            'id': self.id,
            'type': self.type,
            'trade_id_owner': self.trade_id_owner,
            'have_currency_count': self.have_currency_count,
            'have_currency': self.have_currency,
            'get_currency': self.get_currency,
            'show_rate': self.show_rate,
            'rate': self.rate,
            'vst_card': self.vst_card,
            'fiat_cards': [i.config for i in self.fiat_cards],
            'fiat_banks': self.fiat_banks,
        }

    def load_from_json(self, config):
        self.id = config['id']
        self.type = config['type']
        self.trade_id_owner = config['trade_id_owner']
        self.have_currency_count = config['have_currency_count']
        self.have_currency = config['have_currency']
        self.get_currency = config['get_currency']
        self.show_rate = config['show_rate']
        self.rate = config['rate']
        self.vst_card = config['vst_card']
        self.fiat_banks = config['fiat_banks']

        for i in config['fiat_cards']:
            self.fiat_cards.append(Card(i))

    def preview(self):
        if self.type == 'vst':
            cards_banks = set([i.bank.lower() for i in self.fiat_cards])
            cards_banks = '\n'.join(cards_banks)

            text = f'Отдаете: {self.have_currency_count} VST {self.have_currency}\n' \
                   f'Получаете: {round(self.have_currency_count * self.rate, 2)} {self.get_currency}\n' \
                   f'Курс: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки:\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{cards_banks}\n' \
                   f'Часовой пояс: '
        else:
            if self.fiat_banks == ['everyone']:
                banks = 'Любой'
            else:
                banks = '\n'.join(self.fiat_banks)
            print(self.rate)
            text = f'Отдаете: {self.have_currency_count} {self.have_currency}\n' \
                   f'Получаете: {round(self.have_currency_count * self.rate)} VST {self.get_currency}\n' \
                   f'Курс: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки:\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{banks}\n' \
                   f'Часовой пояс: '

        return text

    def button_text(self):
        return f'{self.have_currency} {self.have_currency_count} => {self.get_currency} {round(self.have_currency_count * self.rate)} {self.rate}'


class Deal:
    def __init__(self):
        self.status = ''

        # users
        self.vista_people = 0
        self.vista_people_vst_card = []
        self.vista_people_fiat_card = []

        self.fiat_people = 0
        self.fiat_people_vst_card = []
        self.fiat_people_banks = []

        # info
        self.count_vst = 0
        self.count_fiat = 0
        self.rate = 0

        # for part buy
        self.can_part = False
        self.min_part = 0