import time

import telebot

import screens

import services


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
        banks = []
        if have_cur in ['veur', 'vusd']:
            banks = ['everyone']
            type = 'fiat'
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
                'id': 'show'
            }
        })
        return self.pop_data['filter']


class BotShow:
    def __init__(self, config):
        import config as conf
        self.token = conf.token_show
        self.bot = telebot.TeleBot(self.token)
        self.UsersOriginal = config.Users
        self.Rates = config.Rates
        self.Asks = config.Asks
        self.OriginalBot = config.Bot
        self.Users = UsersShow()

    def initiate(self):
        @self.bot.message_handler(commands = ['start'])
        def start_message_oper(message):
            self.__start_message(message)

        @self.bot.message_handler(content_types = ['text'])
        def message_oper(message):
            try:
                self.__message(message)
            except:
                pass

        @self.bot.callback_query_handler(func = lambda call: True)
        def query_oper(call):
            try:
                self.__query(call)
            except:
                pass

        # self.bot.polling(none_stop = True, interval = 0)

    def send_screen(self, user, screen):
        text, buttons = screen
        self.bot.send_message(chat_id = user.tg_id, text = text, reply_markup = buttons, parse_mode = 'HTML')

    def edit_screen(self, user, screen, message_id):
        text, buttons = screen
        self.bot.edit_message_text(chat_id = user.tg_id, text = text, reply_markup = buttons, message_id = message_id,
                                   parse_mode = 'HTML')

    def delete_message(self, user, message_id):
        self.bot.delete_message(user.tg_id, message_id)

    def __start_message(self, message):
        user = self.Users.tg_identification(message)
        self.send_screen(user, screens.main_screen_show('main'))

    def __message(self, message):
        user = self.Users.tg_identification(message)

        if message.text == '💵 Фильтр заявок':
            user.clear()
            self.send_screen(user, screens.show_asks('choose_cur', user, self.Asks))
        elif message.text == '💵 Все заявки':
            user.clear()
            user.pop_data['filter'] = {
                'index': 0,
                'have_cur': 'all'
            }
            asks = self.Asks.asks_filter(user.pop_data['filter'])
            self.send_screen(user, screens.show_asks('show_asks', user, self.Asks, asks))

    def __query(self, call):
        user = self.Users.tg_identification(call.message)

        # find asks
        if call.data.startswith('d_ask'):
            if call.data.endswith('fcurrency'):
                cur = call.data.split('_')[2]

                user.pop_data.update({'d_currency': cur})
                if cur in ['veur', 'vusd']:
                    user.pop_data.update({'d_type': 'fiat'})
                    self.edit_screen(user, screens.show_asks('choose_fiat_cur', user, self.Asks), call.message.id)
                else:
                    user.pop_data.update({'d_type': 'vst'})
                    self.edit_screen(user, screens.show_asks('choose_vst_cur', user, self.Asks), call.message.id)

            elif call.data.endswith('scurrency'):
                cur = call.data.split('_')[2]

                user.pop_data.update({'d_scurrency': cur})
                vst_cur, fiat_cur = services.find_vst_fiat(user.pop_data['d_currency'], cur)
                user.pop_data.update({
                    'd_vst': vst_cur,
                    'd_fiat': fiat_cur
                })

                if user.pop_data['d_type'] == 'fiat':
                    self.show_ask_filter(user, call.message.id)
                else:
                    banks = services.all_banks
                    banks_name = {i: 0 for i in banks}
                    user.pop_data.update({'d_banks': banks_name})
                    user.position = 'd_ask_banks'
                    self.edit_screen(user, screens.show_asks('get_fiat_banks', user, self.Asks), call.message.id)

            elif call.data.endswith('banks'):
                num = call.data.split('_')[2]
                if num == 'next':
                    # fool check
                    if sum([i for i in user.pop_data['d_banks'].values()]):
                        self.show_ask_filter(user, call.message.id)
                    else:
                        self.edit_screen(user, screens.show_asks('get_fiat_banks', user, self.Asks), call.message.id)
                elif num == 'everyone':
                    user.pop_data['d_banks'] = {'everyone': 1}
                    self.show_ask_filter(user, call.message.id)
                else:
                    num = int(num)
                    ind = list(user.pop_data['d_banks'].keys())[num]
                    if user.pop_data['d_banks'][ind] == 0:
                        user.pop_data['d_banks'][ind] = 1
                    else:
                        user.pop_data['d_banks'][ind] = 0
                    self.edit_screen(user, screens.show_asks('get_fiat_banks', user, self.Asks), call.message.id)

            elif call.data.endswith('next'):
                user.pop_data['filter']['index'] += 1
                self.show_ask_filter(user, call.message.id)

            elif call.data.endswith('prev'):
                user.pop_data['filter']['index'] -= 1
                self.show_ask_filter(user, call.message.id)

            elif call.data.endswith('deal'):
                num = call.data.split('_')[2]
                ask = self.Asks.get_ask_from_id(num)
                if ask.can_show():
                    self.send_screen(user, screens.show_asks('show_ask', user, self.Asks, ask))
                else:
                    self.delete_message(user, call.message.id)

            elif call.data.endswith('dealAccept'):
                num = call.data.split('_')[2]
                ask = self.Asks.get_ask_from_id(num)
                if ask.can_show():
                    if self.UsersOriginal.tg_id_identification(user.tg_id):
                        self.send_screen(user, screens.show_asks('original_send', user, self.Asks, ask))
                        userOr = self.UsersOriginal.tg_id_identification(user.tg_id)
                        userOr.clear()
                        self.OriginalBot.send_screen(user, screens.show_asks('show_ask', user, self.Asks, ask))
                    else:
                        self.send_screen(user, screens.show_asks('not_reg', user, self.Asks, ask))
                else:
                    self.delete_message(user, call.message.id)


        elif call.data == 'delete':
            self.delete_message(user, call.message.id)


    def show_ask_filter(self, user, message_id):
        if 'filter' in user.pop_data:
            filter = user.pop_data['filter']
        else:
            filter = user.CreateFilter()
        asks = self.Asks.asks_filter(filter)
        if len(asks) == 0:
            self.edit_screen(user, screens.show_asks('asks_not_found', user, self.Asks), message_id)
        else:
            self.edit_screen(user, screens.show_asks('show_asks', user, self.Asks, asks), message_id)
