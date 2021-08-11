import telebot

import screens
import services
from classes import Asks, Users, Deals, ReferralWithdrawal, UsersShow

Asks = Asks()
UsersOriginal = Users()
Users = UsersShow()
Deals = Deals()
ReferralWithdrawal = ReferralWithdrawal()


class BotShow:
    def __init__(self, config):
        import config as conf
        self.token = conf.token_show
        self.bot = telebot.TeleBot(self.token)
        self.Rates = config.Rates
        self.OriginalBot = config.Bot

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

        self.bot.polling(none_stop = True, interval = 0)

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
        user = Users.tg_identification(message)
        self.send_screen(user, screens.main_screen_show('main'))

    def __message(self, message):
        user = Users.tg_identification(message)

        if message.text == '💵 Фильтр заявок':
            user.clear()
            self.send_screen(user, screens.show_asks('choose_cur', user))
        elif message.text == '💵 Все заявки':
            user.clear()
            tradeId = UsersOriginal.identification(telegramId = user.tg_id).trade_id
            if tradeId is None: tradeId = 0
            user.pop_data['filter'] = {
                'index': 0,
                'have_cur': 'all',
                'id': tradeId
            }
            asks = Asks.asks_filter(user.pop_data['filter'])
            self.send_screen(user, screens.show_asks('show_asks', user, asks))

    def __query(self, call):
        user = Users.tg_identification(call.message)

        # find asks
        if call.data.startswith('d_ask'):
            if call.data.endswith('fcurrency'):
                cur = call.data.split('_')[2]

                user.pop_data.update({'d_currency': cur})
                if cur in ['veur', 'vusd']:
                    user.pop_data.update({'d_type': 'fiat'})
                    self.edit_screen(user, screens.show_asks('choose_fiat_cur', user), call.message.id)
                else:
                    user.pop_data.update({'d_type': 'vst'})
                    self.edit_screen(user, screens.show_asks('choose_vst_cur', user), call.message.id)

            elif call.data.endswith('scurrency'):
                cur = call.data.split('_')[2]

                user.pop_data.update({'d_scurrency': cur})
                vst_cur, fiat_cur = services.find_vst_fiat(user.pop_data['d_currency'], cur)
                user.pop_data.update({
                    'd_vst': vst_cur,
                    'd_fiat': fiat_cur
                })
                self.show_ask_filter(user, call.message.id)

            elif call.data.endswith('next'):
                user.pop_data['filter']['index'] += 1
                self.show_ask_filter(user, call.message.id)

            elif call.data.endswith('prev'):
                user.pop_data['filter']['index'] -= 1
                self.show_ask_filter(user, call.message.id)

            elif call.data.endswith('deal'):
                num = call.data.split('_')[2]
                ask = Asks.getAsk(num)
                if ask.can_show():
                    self.send_screen(user, screens.show_asks('show_ask_for_show', user, ask))
                else:
                    self.delete_message(user, call.message.id)

            elif call.data.endswith('dealAccept'):
                num = call.data.split('_')[2]
                ask = Asks.getAsk(num)
                if ask.can_show():
                    if UsersOriginal.identification(telegramId = user.tg_id):
                        self.send_screen(user, screens.show_asks('original_send', user, ask))
                        userOr = UsersOriginal.identification(telegramId = user.tg_id)
                        userOr.clear()
                        self.OriginalBot.send_screen(user, screens.show_asks('show_ask', user, ask))
                    else:
                        self.send_screen(user, screens.show_asks('not_reg', user, ask))
                else:
                    self.delete_message(user, call.message.id)

        elif call.data == 'delete':
            self.delete_message(user, call.message.id)

    def show_ask_filter(self, user, message_id):
        if 'filter' in user.pop_data:
            filter = user.pop_data['filter']
        else:
            filter = user.CreateFilter()
        asks = Asks.asks_filter(filter)
        if len(asks) == 0:
            self.edit_screen(user, screens.show_asks('asks_not_found', user), message_id)
        else:
            self.edit_screen(user, screens.show_asks('show_asks', user, asks), message_id)
