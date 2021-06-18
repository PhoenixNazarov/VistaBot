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

    # bids


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
        self.__asks = []


class Ask:
    def __init__(self):
        # vst / fiat
        self.type = 'vst'


class Bid:
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