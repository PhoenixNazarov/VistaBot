import json

import services
import Cards


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
        self.time_zone = ''
        self.rating = 10
        self.trade_id = 0
        self.cards = {}

        # service
        self.ban = False

    def load_from_json(self, _json):
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
        self.cards = _json['cards']

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
            'cards': self.cards
        }

    def check_tg_data(self, message):
        def check_str(_string):
            for i in range(len(_string)):
                if _string[i] not in services.printable:
                    _string = _string[:i] + '?' + _string[i+1:]
            return _string

        self.first_name = check_str(message.chat.first_name)
        self.last_name = check_str(message.chat.last_name)
        self.tg_username = check_str(message.chat.username)

    def add_card(self):
        name = self.pop_data.pop('name')
        card_blank = [['Название', name]]

        currency = self.pop_data.pop('currency')
        if currency in ['veur', 'vusd']:
            if currency == 'veur':
                card_blank.append(['Валюта', 'Vista EUR'])
            else:
                card_blank.append(['Валюта', 'Vista USD'])
            card_blank.append(['Номер счет', self.pop_data.pop('account')])
            card_blank.append(['Номер телефона', self.pop_data.pop('phone')])

        elif currency == 'byn':
            card_blank.append(['Банк', self.pop_data.pop('bank')])
            card_blank.append(['Тип карты', self.pop_data.pop('card_type')])
            card_blank.append(['ФИО', self.pop_data.pop('fio')])
            card_blank.append(['Дата действия', self.pop_data.pop('date_end')])

        else:
            type = self.pop_data.pop('type')
            if type == 'card':
                card_blank.append(['Тип', 'Карта'])
                card_blank.append(['Банк', self.pop_data.pop('bank')])
                card_blank.append(['Тип карты', self.pop_data.pop('card_type')])
                card_blank.append(['ФИО', self.pop_data.pop('fio')])
            elif type == 'account':
                card_blank.append(['Тип', 'Счет'])
                card_blank.append(['Банк', self.pop_data.pop('bank')])
                card_blank.append(['БИК', self.pop_data.pop('bik')])
                card_blank.append(['ФИО', self.pop_data.pop('fio')])
            else:
                card_blank.append(['Тип', 'PayPal'])
                card_blank.append(['Mail', self.pop_data.pop('mail')])

        card = ''
        for i in card_blank:
            card += f'{i[0]}: {i[1]}\n'

        self.cards.update({name: card})

        return len(self.cards)-1

    def remove_card(self, id):
        cards_name = list(self.cards.keys())[id]
        self.cards.pop(cards_name)
