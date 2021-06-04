import json
import string


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
        for user in self.__Users:
            _users.append(user.to_json())

        with open('base/users.json', 'w') as file:
            file.write()

    def tg_identification(self, message):
        if message.id in self.__Users:
            _user = self.__Users[message.id]
        else:
            _user = User()
            _user.tg_id = message.id

        _user.check_tg_data(message)
        return self.__Users[message.id]


class User:
    def __init__(self):
        self.tg_id = ''
        self.first_name = ''
        self.last_name = ''
        self.tg_username = ''

        self.trade_username = ''

        self.ban = False

    def load_from_json(self, _json):

    def to_json(self):



    def check_tg_data(self, message):
        def check_str(_string):
            for i in range(len(_string)):
                if _string[i] not in string.printable:
                    _string[i] = '?'
            return _string

        self.first_name = check_str(message.chat.first_name)
        self.last_name = check_str(message.chat.last_name)
        self.tg_username = check_str(message.chat.username)

        if self.trade_username == '':
            self.trade_username = self.tg_username

