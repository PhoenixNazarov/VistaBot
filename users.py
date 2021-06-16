import json
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

        # referral
        self.referal_list = []
        self.referal_to = False

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
        self.referal_list = _json['referal_list']
        self.referal_to = _json['referal_to']

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
            'cards': self.cards,
            'referal_list': self.referal_list,
            'referal_to': self.referal_to
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

        # check rating == 0
        if self.rating == 0:
            self.ban = True

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

        self.cards.append(current_card)

        return len(self.cards) - 1

    def remove_card(self, id):
        self.cards.pop(id)

    def names_cards(self):
        names = []
        for i in self.cards:
            names.append(i[1])
        return names
