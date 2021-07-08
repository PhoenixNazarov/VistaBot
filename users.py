import json
import datetime
import services
import screens


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

    def trade_id_identification(self, id):
        for i in self.__Users:
            if self.__Users[i].trade_id == id:
                return self.__Users[i]

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

    def get_count(self):
        return len(self.__Users)


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
                            break
                    else:
                        1/0

        else:
            ask.have_currency = self.pop_data.pop('fcurrency')
            ask.get_currency = self.pop_data.pop('scurrency').replace('v', '')
            ask.type = 'fiat'

            for i in self.pop_data['banks']:
                if self.pop_data['banks'][i]:
                    ask.fiat_banks.append(i)

        ask.show_rate = round(self.pop_data.pop('rate'), 2)
        ask.rate = Rates.get_count_rate(ask.have_currency, ask.get_currency, ask.show_rate)

        ask.have_currency_count = self.pop_data.pop('count')
        ask.vst_card = Card(self.pop_data.pop('vstcard'))
        ask.trade_id_owner = self.trade_id
        ask.rating = self.rating
        ask.time_zone = self.time_zone
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

    def collect_full(self, show='tg'):
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
                   f'{self.config[5]}, {self.config[6]}'

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

    def collect_for_deal(self):
        if self.create_type == 've':
            text = f'Vista EUR\n' \
                   f'{self.config[3]}\n' \
                   f'{self.config[4]}'

        elif self.create_type == 'vu':
            text = f'Vista USD\n' \
                   f'{self.config[3]}\n' \
                   f'{self.config[4]}'

        elif self.create_type == 'c':
            text = f'Карта, {self.config[2]}\n' \
                   f'{self.config[3]}, {self.config[4]}\n' \
                   f'{self.config[5]}, {self.config[6]}'

        elif self.create_type == 'a':
            text = f'Счёт, {self.config[2]}\n' \
                   f'{self.config[3]}\n' \
                   f'Бик: {self.config[4]}\n' \
                   f'Номер счёта: {self.config[5]}\n' \
                   f'{self.config[6]}'

        elif self.create_type == 'p':
            text = f'PayPal, {self.config[2]}\n' \
                   f'{self.config[3]}'

        else:
            text = f'BYN\n' \
                   f'{self.config[3]}, {self.config[4]}\n' \
                   f'{self.config[5], self.config[6]}'
        return text


class Asks:
    def __init__(self, config):
        self.__asks = {}
        self.path = 'base/asks.json'
        self.numb = 1

        self.Rates = config.Rates

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

        self.numb = dc['numb']

        for i in dc['asks']:
            _ask = Ask()
            _ask.load_from_json(i)
            self.__asks.update({i['id']: _ask})

    def save(self):
        dc = []
        for i in self.__asks.values():
            dc.append(i.to_json())

        with open(self.path, 'w') as file:
            file.write(json.dumps({
                'numb': self.numb,
                'asks': dc
            }))

    def asks_filter(self, user):
        have_cur = user.pop_data['d_currency']
        get_cur = user.pop_data['d_scurrency']
        type = 'vst'
        banks = []
        if have_cur in ['veur', 'vusd']:
            cards_name = user.pop_data['d_cards_name']
            for i in cards_name:
                if cards_name[i]:
                    for card in user.cards:
                        print(card.name,i)
                        if card.name == i:
                            banks.append(card.bank.lower())
                            break
                    else:
                        1/0
            type = 'fiat'
        else:
            for i in user.pop_data['d_banks']:
                if user.pop_data['d_banks'][i]:
                    banks.append(i.lower())

        asks = []

        for i in self.__asks.values():
            if not i.can_show(): continue

            if i.type == type:
                if i.type == 'vst':
                    if 'v' + i.have_currency == get_cur and i.get_currency == have_cur:
                        if 'everyone' in user.pop_data['d_banks']:
                            asks.append(i)
                        else:
                            for bank in banks:
                                if any([bank in card.bank.lower() for card in i.fiat_cards]):
                                    asks.append(i)
                                    break
                else:
                    if i.have_currency == get_cur and 'v' + i.get_currency == have_cur:
                        if 'everyone' in i.fiat_banks:
                            asks.append(i)
                        else:
                            for bank in i.fiat_banks:
                                if any([bank.lower() in x for x in banks]):
                                    asks.append(i)
                                    break

        asks = sorted(asks, key = lambda x: x.rate, reverse = True)

        return asks

    def get_asks(self, trade_id):
        asks = []
        for i in self.__asks.values():
            if i.trade_id_owner == trade_id:
                asks.append(i)
        return asks

    def get_ask_from_id(self, id):
        return self.__asks[int(id)]

    def remove_ask(self, id):
        return self.__asks.pop(int(id))

    # for admin_panel
    def get_asks_web(self):
        _list = []
        for i in self.__asks.values():
            _list.append([i.id, i.trade_id_owner, i.button_text(), i.status])
        return _list

    def get_count(self):
        return len(self.__asks)


class Ask_ch:
    def set_Data(self, Data):
        self.Data = Data
        self.Rates = None


class Ask(Ask_ch):
    def __init__(self):
        self.Rates = None
        # user have vst / fiat
        self.type = 'vst'
        self.status = 'wait_allow'
        self.trade_id_owner = 0
        self.id = -1

        self.have_currency_count = 0
        self.have_currency = ''
        self.get_currency = ''
        self.show_rate = 0
        self.rate = 0

        self.vst_card = None

        self.time_zone = ''
        self.rating = 0

        # optional
        self.fiat_cards = []
        self.fiat_banks = []

    def to_json(self):
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
            'vst_card': self.vst_card.config,
            'fiat_cards': [i.config for i in self.fiat_cards],
            'fiat_banks': self.fiat_banks,
            'time_zone': self.time_zone,
            'rating': self.rating,
        }

    def load_from_json(self, config):
        self.id = config['id']
        self.status = config['status']
        self.type = config['type']
        self.trade_id_owner = config['trade_id_owner']
        self.have_currency_count = config['have_currency_count']
        self.have_currency = config['have_currency']
        self.get_currency = config['get_currency']
        self.show_rate = config['show_rate']
        self.rate = config['rate']
        self.vst_card = Card(config['vst_card'])
        self.fiat_banks = config['fiat_banks']
        self.time_zone = config['time_zone']
        self.rating = config['rating']

        for i in config['fiat_cards']:
            self.fiat_cards.append(Card(i))

    def get_count(self):
        return round(self.have_currency_count * self.rate, 2)

    def have_count_w_com(self):
        if self.type == 'vst':
            return round(self.have_currency_count + self.have_currency_count * (self.Data.perc_vst / 100), 2)
        else:
            return round(self.have_currency_count + self.have_currency_count * (self.Data.perc_fiat / 100), 2)

    def get_count_w_com(self):
        if self.type == 'fiat':
            return round(self.get_count() + self.get_count() * (self.Data.perc_vst / 100), 2)
        else:
            return round(self.get_count() + self.get_count() * (self.Data.perc_fiat / 100), 2)

    def have_count_com(self):
        if self.type == 'vst':
            return round(self.have_currency_count * (self.Data.perc_vst / 100), 2)
        else:
            return round(self.have_currency_count * (self.Data.perc_fiat / 100), 2)

    def get_count_com(self):
        if self.type == 'fiat':
            return round(self.get_count() * (self.Data.perc_vst / 100), 2)
        else:
            return round(self.get_count() * (self.Data.perc_fiat / 100), 2)

    def can_show(self):
        if self.status == 'ok':
            return 1
        else:
            return 0

    def preview(self):
        sign_have_currency = services.signs[self.have_currency]
        sign_get_currency = services.signs[self.get_currency]
        if self.type == 'vst':
            cards_banks = set([i.bank.lower() for i in self.fiat_cards])
            cards_banks = '\n'.join(cards_banks)

            text = f'Отдаете: {self.have_count_w_com()} VST {sign_have_currency}\n' \
                   f'Получаете: {self.get_count_w_com()} {sign_get_currency}\n' \
                   f'Курс: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки: {self.rating}\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{cards_banks}\n' \
                   f'Часовой пояс: {self.time_zone}'
        else:
            if self.fiat_banks == ['everyone']:
                banks = 'Любой'
            else:
                banks = '\n'.join(self.fiat_banks)
            print(self.rate)
            text = f'Отдаете: {self.have_count_w_com()} {sign_have_currency}\n' \
                   f'Получаете: {self.get_count_w_com()} VST {sign_get_currency}\n' \
                   f'Курс: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки: {self.rating}\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{banks}\n' \
                   f'Часовой пояс: {self.time_zone}'

        return text

    def preview_for_deal(self):
        sign_have_currency = services.signs[self.have_currency]
        sign_get_currency = services.signs[self.get_currency]
        if self.type == 'vst':
            cards_banks = set([i.bank.lower() for i in self.fiat_cards])
            cards_banks = '\n'.join(cards_banks)

            text = f'Получаете: {self.have_count_w_com()} VST {sign_have_currency}\n' \
                   f'Отдаете: {self.get_count_w_com()} {sign_get_currency}\n' \
                   f'Курс: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки: {self.rating}\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{cards_banks}\n' \
                   f'Часовой пояс: {self.time_zone}'
        else:
            if self.fiat_banks == ['everyone']:
                banks = 'Любой'
            else:
                banks = '\n'.join(self.fiat_banks)
            print(self.rate)
            text = f'Получаете: {self.have_count_w_com()} {sign_have_currency}\n' \
                   f'Отдаете: {self.get_count_w_com()} VST {sign_get_currency}\n' \
                   f'Курс: {self.show_rate}\n' \
                   f'Рейтинг создателя заявки: {self.rating}\n' \
                   f'Возможные способы получить {self.get_currency}:\n' \
                   f'{banks}\n' \
                   f'Часовой пояс: {self.time_zone}'

        return text

    def button_text(self):
        sign_have_currency = services.signs[self.have_currency]
        sign_get_currency = services.signs[self.get_currency]
        if self.type == 'vst':
            return f'VST {sign_have_currency} {self.have_count_w_com()} ⇒ {sign_get_currency} {self.get_count_w_com()} {self.show_rate}'

        return f'{sign_have_currency} {self.have_count_w_com()} ⇒ VST {sign_get_currency} {self.get_count_w_com()} {self.show_rate}'

    def web(self):
        if self.type == 'vst':
            return {
                'give': f'{self.have_currency_count} + {self.have_count_com()}  VST {self.have_currency}',
                'get': f'{round(self.get_count(), 2)} + {self.get_count_com()}  {self.get_currency}',
                'rate': f'({self.show_rate}) {self.rate} '
            }
        else:
            return {
                'give': f'{self.have_currency_count} + {self.have_count_com()} {self.have_currency}',
                'get': f'{round(self.get_count(), 2)} + {self.get_count_com()}  VST {self.get_currency}',
                'rate': f'({self.show_rate}) {self.rate} '
            }


class Deals:
    def __init__(self, config):
        self.__deals = {}
        self.Asks = config.Asks
        self.load()

    def make_deal(self, user, Users):
        ask = self.Asks.get_ask_from_id(user.pop_data.pop('d_ask_id'))
        if not ask.can_show():
            return

        deal = Deal()
        type = user.pop_data.pop('d_type')
        if type == 'vst':
            banks = []
            for i in user.pop_data['d_banks']:
                if user.pop_data['d_banks'][i]:
                    banks.append(i)

            deal.fiat_people = user.tg_id
            deal.fiat_people_vst_card = user.pop_data.pop('d_vst')
            deal.fiat_people_banks = banks

            deal.vista_people = Users.trade_id_identification(ask.trade_id_owner).tg_id
            deal.vista_people_vst_card = ask.vst_card.config
            deal.vista_people_fiat_card = [i.config for i in ask.fiat_cards]
            deal.vista_currency = 'VST ' + services.signs[ask.have_currency]
            deal.fiat_currency = services.signs[ask.get_currency]
            deal.vista_count = ask.have_count_w_com()
            deal.vista_count_without_com = ask.have_currency_count
            deal.fiat_count = ask.get_count_w_com()

        else:
            cards = []
            for i in user.pop_data['d_cards_name']:
                if user.pop_data['d_cards_name'][i]:
                    for card in user.cards:
                        if card.name == i:
                            cards.append(card.config)
                            break
                    else:
                        1/0

            deal.vista_people = user.tg_id
            deal.vista_people_vst_card = user.pop_data.pop('d_vst')
            deal.vista_people_fiat_card = cards

            deal.fiat_people = Users.trade_id_identification(ask.trade_id_owner).tg_id
            deal.fiat_people_vst_card = ask.vst_card.config
            deal.fiat_people_banks = ask.fiat_banks
            deal.vista_currency = 'VST ' + services.signs[ask.get_currency]
            deal.fiat_currency = services.signs[ask.have_currency]
            deal.vista_count = ask.get_count_w_com()
            deal.vista_count_without_com = ask.have_currency_count
            deal.fiat_count = ask.have_count_w_com()

        deal.reload_cards()

        # info
        deal.rate = ask.rate
        deal.owner_id = ask.trade_id_owner
        deal.trade_id = user.trade_id
        deal.id = ask.id

        self.__deals.update({ask.id: deal})
        self.Asks.remove_ask(ask.id) #todo remove

        return deal

    def get_deal(self, id):
        return self.__deals[int(id)]

    def get_deals_for_user(self, id):
        deals = []
        for i in self.__deals.values():
            if i.owner_id == id or i.trade_id == id:
                deals.append(i)
        return deals

    def remove_deal(self, id):
        return self.__deals.pop(int(id))

    def load(self):
        with open('base/deals.json', 'r') as file:
            base = json.loads(file.read())

        for i in base:
            _deal = Deal()
            _deal.load_from_json(i)
            self.__deals.update({i['id']: _deal})

    def save(self):
        base = []
        for i in self.__deals.values():
            base.append(i.to_json())

        with open('base/deals.json', 'w') as file:
            file.write(json.dumps(base))

    def get_deals_for_web(self):
        _list = []
        for i in self.__deals.values():
            _list.append([i.id, i.admin_description(), i.status])
        return _list

    def get_count(self):
        return len(self.__deals)


class Deal_ch:
    def set_data(self):
        self.Data = None


class Deal(Deal_ch):
    def __init__(self):
        # wait_vst, wait_vst_proof, wait_fiat, wait_fiat_proof, wait_garant_vst
        self.status = 'wait_vst'
        self.id = -1
        self.ask_id = 0

        # users, vista - have vista (A)
        self.vista_people = 0
        self.vista_people_vst_card = []
        self.vista_people_fiat_card = []
        self.vista_currency = ''
        self.vista_count = 0
        self.vista_count_without_com = 0
        self.vista_send_over = 0
        self.vista_last_notification = ''

        # (B)
        self.fiat_people = 0
        self.fiat_people_vst_card = []
        self.fiat_people_banks = []
        self.fiat_currency = ''
        self.fiat_count = 0
        self.fiat_send_over = 0
        self.fiat_last_notification = ''
        self.fiat_choose_card = []

        # info
        self.rate = 0
        self.owner_id = 0
        self.trade_id = 0

    def reload_cards(self):
        self.vista_people_vst_card = Card(self.vista_people_vst_card)
        self.fiat_people_vst_card = Card(self.fiat_people_vst_card)
        cards = []
        for i in self.vista_people_fiat_card:
            cards.append(Card(i))
        self.vista_people_fiat_card = cards

    def button_text(self):
        return f'№{self.id} {self.vista_count} {self.vista_currency} ⇒ {self.fiat_count} {self.fiat_currency}'

    def garant_card(self):
        if '$' in self.vista_currency:
            return self.Data.card_usd
        else:
            return self.Data.card_eur

    def logic_message(self, user, optional=None):
        user_id = user.tg_id
        if user_id == self.vista_people:
            self.vista_last_notification = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
        else:
            self.fiat_last_notification = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')

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
        if user == 'admin':
            # 2
            if key == 'garant_accept':
                if self.status == 'wait_vst_proof':
                    self.status = 'wait_fiat'
                    return 1
            # 5
            if key == 'garant_send':
                if self.status == 'wait_garant_vst':
                    self.status = 'end'
                    return 1

        elif user.tg_id == self.vista_people:
            # 1
            if key == 'vst_sended':
                if self.status == 'wait_vst':
                    self.status = 'wait_vst_proof'
                    return 1
            # 4
            elif key == 'fiat_accept':
                if self.status == 'wait_fiat_proof':
                    self.status = 'wait_garant_vst'
                    return 1

        elif user.tg_id == self.fiat_people:
            # 3
            if key == 'fiat_sended':
                if self.status == 'wait_fiat':
                    self.status = 'wait_fiat_proof'
                    return 1

    def to_json(self):
        if self.fiat_choose_card:
            fiat_choose_card = self.fiat_choose_card.config
        else:
            fiat_choose_card = []

        return {
            'status': self.status,
            'id': self.id,
            'ask_id': self.ask_id,
            'vista_people': self.vista_people,
            'vista_people_vst_card': self.vista_people_vst_card.config,
            'vista_people_fiat_card': [i.config for i in self.vista_people_fiat_card],
            'vista_currency': self.vista_currency,
            'vista_count': self.vista_count,
            'fiat_people': self.fiat_people,
            'fiat_people_vst_card': self.fiat_people_vst_card.config,
            'fiat_people_banks': self.fiat_people_banks,
            'fiat_currency': self.fiat_currency,
            'fiat_count': self.fiat_count,
            'rate': self.rate,
            'owner_id': self.owner_id,
            'trade_id': self.trade_id,
            'vista_count_without_com': self.vista_count_without_com,
            'vista_send_over': self.vista_send_over,
            'vista_last_notification': self.vista_last_notification,
            'fiat_send_over': self.fiat_send_over,
            'fiat_last_notification': self.fiat_last_notification,
            'fiat_choose_card': fiat_choose_card,
        }

    def load_from_json(self, config):
        self.status = config['status']
        self.id = config['id']
        self.ask_id = config['ask_id']
        self.vista_people = config['vista_people']
        self.vista_people_vst_card = config['vista_people_vst_card']
        self.vista_people_fiat_card = config['vista_people_fiat_card']
        self.vista_currency = config['vista_currency']
        self.vista_count = config['vista_count']
        self.fiat_people = config['fiat_people']
        self.fiat_people_vst_card = config['fiat_people_vst_card']
        self.fiat_people_banks = config['fiat_people_banks']
        self.fiat_currency = config['fiat_currency']
        self.fiat_count = config['fiat_count']
        self.rate = config['rate']
        self.owner_id = config['owner_id']
        self.trade_id = config['trade_id']
        self.vista_count_without_com = config['vista_count_without_com']
        self.vista_send_over = config['vista_send_over']
        self.vista_last_notification = config['vista_last_notification']
        self.fiat_send_over = config['fiat_send_over']
        self.fiat_last_notification = config['fiat_last_notification']
        self.fiat_choose_card = config['fiat_choose_card']
        if self.fiat_choose_card:
            self.fiat_choose_card = Card(self.fiat_choose_card)
        self.reload_cards()

    def admin_description(self):
        return f'{self.vista_count} VST {self.vista_currency} ⇒ {self.fiat_count} {self.fiat_currency} {self.rate}'
