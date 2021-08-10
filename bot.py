import time
import telebot

import screens
import services

from classes import Asks, Users, Deals, ReferralWithdrawal
Asks = Asks()
Users = Users()
Deals = Deals()
ReferralWithdrawal = ReferralWithdrawal()


class Bot:
    def __init__(self, config):
        import config as conf
        self.token = conf.token
        self.bot = telebot.TeleBot(self.token)
        self.Rates = config.Rates

    def initiate(self):

        @self.bot.message_handler(commands = ['start'])
        def start_message_oper(message):
            self.__start_message(message)

        @self.bot.message_handler(content_types = ['text'])
        def message_oper(message):
            # try:
                self.__message(message)
            # except:
            #     pass

        @self.bot.callback_query_handler(func = lambda call: True)
        def query_oper(call):
            # try:
                self.__query(call)
            # except:
            #     pass

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

    def checkUserData(self, user):
        if user.mail == '':
            user.position = 'first_welcome'
            self.send_screen(user, screens.edit_mail('main'))
            return 1
        elif user.phone == '':
            user.position = 'second_welcome'
            self.send_screen(user, screens.edit_phone('main'))
            return 1
        elif user.fio == '':
            user.position = 'third_welcome'
            self.send_screen(user, screens.edit_fio('main'))
            return 1

    def __start_message(self, message):
        user = Users.identification(message = message)
        if user.ban:
            return

        s = message.text.split(' ')
        if len(s) == 2:
            user.goReferral(s[1])

        if self.checkUserData(user) is None:
            user.position = 'main'
            self.send_screen(user, screens.main_screen('main'))

    def __message(self, message):
        user = Users.identification(message = message)
        if user.ban:
            return

        # set email
        if user.position == 'first_welcome':
            if self.get_email(user, message.text):
                self.checkUserData(user)
            else:
                user.position = 'main'
                self.send_screen(user, screens.main_screen('main'))

        # set phone
        elif user.position == 'second_welcome':
            if self.get_phone(user, message.text):
                self.checkUserData(user)
            else:
                user.position = 'main'
                self.send_screen(user, screens.main_screen('main'))

        # set fio
        elif user.position == 'third_welcome':
            if self.get_fio(user, message.text):
                self.checkUserData(user)
                user.position = 'main'
                self.send_screen(user, screens.main_screen('main'))
            else:
                user.position = 'main'
                self.send_screen(user, screens.main_screen('main'))

        elif self.checkUserData(user):
            return

        # registration end, main menu
        elif message.text == '👤 Личный кабинет':
            user.clear()
            self.send_screen(user, screens.user_info('main', user))
        elif message.text == '❓ Поддержка и информация':
            user.clear()
            self.send_screen(user, screens.faq(-1))
        elif message.text == '💳 Шаблоны моих карт и счетов':
            user.clear()
            self.send_screen(user, screens.card(-1, user))
        # elif message.text == '💵 Создать заявку':
        elif message.text == '💵 Мои заявки':
            user.clear()
            self.send_screen(user, screens.my_asks('main', user))
        elif message.text == '💵 Активные заявки':
            user.clear()
            user.pop_data['filter'] = {
                'index': 0,
                'have_cur': 'all',
                'id': user.trade_id
            }
            asks = Asks.asks_filter(user.pop_data['filter'])
            if len(asks) == 0:
                self.send_screen(user, screens.show_asks('asks_not_found', user))
            else:
                self.send_screen(user, screens.show_asks('show_asks', user, asks))

        elif message.text == '💵 Мои сделки':
            user.clear()
            self.send_screen(user, screens.my_deal('my_deal', user))

        # user info - EDIT
        elif user.position.startswith('user_edit'):
            new = False
            if user.position.endswith('fio'):
                if self.get_fio(user, message.text): new = True
            elif user.position.endswith('mail'):
                if self.get_email(user, message.text): new = True
            elif user.position.endswith('phone'):
                if self.get_phone(user, message.text): new = True

            if new:
                self.send_screen(user, screens.user_info('main', user))

        # edit card
        elif user.position.startswith('card_edit'):
            if user.position.endswith('name'):
                if message.text in user.getCards(output = 'name'):
                    self.send_screen(user, screens.card('name_error', user))

                elif services.check_card_name(message.text):
                    user.pop_data.update({'name': message.text})

                    if user.pop_data['currency'] in ['veur', 'vusd']:
                        self.send_screen(user, screens.card('vista_account', user))
                        user.position = 'card_edit_vista_account'
                    elif user.pop_data['currency'] in ['rub', 'usd', 'eur']:
                        self.send_screen(user, screens.card('choose_type', user))
                    else:
                        self.send_screen(user, screens.card('choose_bank_byn', user))
                        user.position = 'card_edit_choose_bank_type'
                else:
                    self.send_screen(user, screens.card('name_alr', user))

            # only vista
            elif user.position.endswith('vista_account'):
                if services.check_vista_account(message.text):
                    user.pop_data.update({'account': message.text})
                    self.send_screen(user, screens.card('vista_number', user))
                    user.position = 'card_edit_vista_number'
                else:
                    self.send_screen(user, screens.card('vista_account_error', user))

            elif user.position.endswith('vista_number'):
                if 1:
                    user.pop_data.update({'phone': message.text})
                    self.card_edit_finish(user)
                else:
                    self.send_screen(user, screens.card('vista_number', user))

            # only rub, usd, eur
            elif user.position.endswith('choose_bank'):
                user.pop_data.update({'bank': message.text})
                if user.pop_data['type'] == 'card':
                    self.send_screen(user, screens.card('type_card', user))
                    user.position = 'card_edit_type_card'
                else:
                    self.send_screen(user, screens.card('bik', user))
                    user.position = 'card_edit_bik'

            elif user.position.endswith('type_card'):
                user.pop_data.update({'type_card': message.text})
                self.send_screen(user, screens.card('fio', user))
                user.position = 'card_edit_fio'

            elif user.position.endswith('bik'):
                if services.check_bik(message.text):
                    user.pop_data.update({'bik': message.text})
                    self.send_screen(user, screens.card('fio', user))
                    user.position = 'card_edit_fio'
                else:
                    self.send_screen(user, screens.card('bik', user))

            elif user.position.endswith('fio'):
                if services.check_fio(message.text) and len(message.text.split(' ')) == 2:
                    fio = message.text.split(' ')
                    fio = f'{fio[1]} {fio[0][0]}.'
                    user.pop_data.update({'fio': fio})
                    if user.pop_data['type'] == 'account':
                        self.send_screen(user, screens.card('account_number', user))
                        user.position = 'card_edit_account_number'
                    else:
                        self.send_screen(user, screens.card('card_number', user))
                        user.position = 'card_edit_card_number'
                else:
                    self.send_screen(user, screens.card('fio', user))

            elif user.position.endswith('card_number'):
                if services.check_card_number(message.text):
                    user.pop_data.update({'card_number': message.text})
                    if user.pop_data['currency'] == 'byn':
                        self.send_screen(user, screens.card('date_end', user))
                        user.position = 'card_edit_date_end'
                    else:
                        self.card_edit_finish(user)
                else:
                    self.send_screen(user, screens.card('card_number', user))

            elif user.position.endswith('account_number'):
                if services.check_account_number(message.text):
                    user.pop_data.update({'account_number': message.text})
                    self.card_edit_finish(user)
                else:
                    self.send_screen(user, screens.card('account_number', user))

            elif user.position.endswith('mail'):
                if services.check_email(message.text):
                    user.pop_data.update({'mail': message.text})
                    self.card_edit_finish(user)
                else:
                    self.send_screen(user, screens.card('mail', user))

            # only byn
            elif user.position.endswith('date_end'):
                if services.check_date_end(message.text):
                    user.pop_data.update({'date_end': message.text})
                    self.card_edit_finish(user)
                else:
                    self.send_screen(user, screens.card('date_end', user))

        # create ask
        elif user.position.startswith('create_ask'):
            if user.position.endswith('count'):
                text = message.text.replace(',', '.')
                if text.isdigit():
                    num = float(message.text)
                    if num > 0:
                        user.pop_data.update({'count': num})
                        self.send_screen(user, screens.create_asks('incomplete', user))
                    else:
                        self.send_screen(user, screens.create_asks('count_error', user))
                else:
                    self.send_screen(user, screens.create_asks('count_error', user))

            elif user.position.endswith('count_incomplete'):
                text = message.text.replace(',', '.')
                if text.isdigit():
                    num = int(message.text)
                    if 0 < num < user.pop_data['count']:
                        user.pop_data.update({'count_incomplete': num})
                        self.send_screen(user, screens.create_asks('choose_s', user))
                    else:
                        self.send_screen(user, screens.create_asks('count_error', user))
                else:
                    self.send_screen(user, screens.create_asks('count_error', user))

            elif user.position.endswith('rate'):
                text = message.text.replace(',', '.')
                try:
                    num = float(text)
                    if num > 0:
                        user.pop_data.update({'rate': num})
                        self.create_ask_5_step(user)
                    else:
                        self.send_screen(user, screens.create_asks('rate_error', user))
                except:
                    self.send_screen(user, screens.create_asks('rate_error', user))

            elif user.position.endswith('banks'):
                user.pop_data['banks'].update({message.text: 1})
                self.send_screen(user, screens.create_asks('get_fiat_banks', user))

        # show ask
        elif user.position.startswith('d_ask'):
            # if user.position.endswith('banks'):
            #     user.pop_data['d_banks'].update({message.text: 1})
            #     self.send_screen(user, screens.show_asks('get_fiat_banks', user, Asks))

            if user.position.endswith('count_incomplete'):
                text = message.text.replace(',', '.')
                if text.isdigit():
                    num = int(message.text)
                    ask = Asks.getAsk(id = user.pop_data['d_ask_id'])
                    if ask.have_currency_count > num >= ask.min_incomplete:
                        user.pop_data.update({'d_count_incomplete': num})
                        self.tg_show_original_rel(user)
                    else:
                        self.send_screen(user, screens.create_asks('count_error', user))
                else:
                    self.send_screen(user, screens.create_asks('count_error', user))

        # deal answer
        elif user.position.startswith('count_answer'):
            num = user.position.split('_')[2]
            deal = Deals.getDeal(num)
            if message.text == str(user.pop_data.pop('answer')):
                if deal.logic_control('fiat_accept', user):
                    user_A = Users.identification(telegramId = deal.vista_people)
                    user_B = Users.identification(telegramId = deal.fiat_people)
                    self.send_screen(user_A, deal.logic_message(user_A))
                    self.send_screen(user_B, deal.logic_message(user_B))
            else:
                self.send_screen(user, screens.deal('5_A_ans', deal, user))

    def __query(self, call):
        user = Users.identification(message = call.message)
        if user.ban:
            return

        # user info - EDIT
        if call.data.startswith('userdata'):
            if call.data.endswith('main'):
                self.edit_screen(user, screens.user_info('main', user), call.message.id)
            elif call.data.endswith('change'):
                self.edit_screen(user, screens.user_info('change', user), call.message.id)
            elif call.data.endswith('referal'):
                self.edit_screen(user, screens.user_info('referal', user), call.message.id)
            elif call.data.endswith('ref_list'):
                self.edit_screen(user, screens.user_info('referal_list', user), call.message.id)
            elif call.data.endswith('ref_getu'):
                if user.vusd > services.referral_withdrawal_usd:
                    self.edit_screen(user, screens.user_info('card_vusd', user), call.message.id)
                else:
                    self.send_screen(user, screens.user_info('low_money', user))
            elif call.data.endswith('ref_gete'):
                if user.veur > services.referral_withdrawal_eur:
                    self.edit_screen(user, screens.user_info('card_veur', user), call.message.id)
                else:
                    self.send_screen(user, screens.user_info('low_money', user))
            elif call.data.endswith('cardsu'):
                if user.vusd > services.referral_withdrawal_usd:
                    num = int(call.data.split('_')[1])
                    ReferralWithdrawal.add(user, num, 'vusd')
                    self.edit_screen(user, screens.user_info('card_choose', user), call.message.id)
                else:
                    self.send_screen(user, screens.user_info('low_money', user))
            elif call.data.endswith('cardse'):
                if user.veur > services.referral_withdrawal_eur:
                    num = int(call.data.split('_')[1])
                    ReferralWithdrawal.add(user, num, 'veur')
                    self.edit_screen(user, screens.user_info('card_choose', user), call.message.id)
                else:
                    self.send_screen(user, screens.user_info('low_money', user))

            elif call.data.endswith('ref_gete'):
                self.edit_screen(user, screens.user_info('referal_list', user), call.message.id)

        elif call.data.startswith('user_edit'):
            if call.data.endswith('fio'):
                self.send_screen(user, screens.edit_fio('main'))
            elif call.data.endswith('mail'):
                self.send_screen(user, screens.edit_mail('main'))
            elif call.data.endswith('phone'):
                self.send_screen(user, screens.edit_phone('main'))
            elif call.data.endswith('time_zone'):
                self.edit_screen(user, screens.edit_time_zone(), call.message.id)
            user.position = call.data

        # faq
        elif call.data.startswith('faq'):
            self.edit_screen(user, screens.faq(int(call.data[4:])), call.message.id)

        # edit time zones
        elif call.data.startswith('time_zone'):
            self.get_time_zone(user, call)

        # edit card
        elif call.data.startswith('card'):
            if call.data.endswith('add'):
                self.send_screen(user, screens.card('currency', user))

            # show
            elif call.data.startswith('card_info'):
                self.edit_screen(user, screens.card(call.data, user), call.message.id)

            elif call.data.startswith('card_del'):
                id = call.data.split('_')[-1]
                self.edit_screen(user, screens.card('del_confirm_' + id, user), call.message.id)

            elif call.data.startswith('card_y_del'):
                id = int(call.data.split('_')[-1])
                user.getCard(id).remove()
                self.edit_screen(user, screens.card(-1, user), call.message.id)

            elif call.data.startswith('card_back'):
                self.edit_screen(user, screens.card(-1, user), call.message.id)

            # editing
            elif call.data.endswith('currency'):
                currency = call.data.split('_')[1]
                user.pop_data.update({'currency': currency})
                self.edit_screen(user, screens.card('name', user), call.message.id)
                user.position = 'card_edit_name'

            # only rub, usd, eur
            elif call.data.endswith('type'):
                type = call.data.split('_')[1]
                user.pop_data.update({'type': type})
                if type in ['card', 'account']:
                    self.edit_screen(user, screens.card('choose_bank', user), call.message.id)
                    user.position = 'card_edit_choose_bank'
                else:
                    self.edit_screen(user, screens.card('mail', user), call.message.id)
                    user.position = 'card_edit_email'

            elif call.data.endswith('bank'):
                bank = int(call.data.split('_')[1])
                user.pop_data.update({'bank': services.popular_russian_bank[bank]})
                if user.pop_data['type'] == 'card':
                    self.edit_screen(user, screens.card('type_card', user), call.message.id)
                    user.position = 'card_edit_type_card'
                else:
                    self.send_screen(user, screens.card('bik', user))
                    user.position = 'card_edit_bik'

            elif call.data.endswith('tcard'):
                card = int(call.data.split('_')[1])
                user.pop_data.update({'card_type': services.card_type[card]})
                user.position = 'card_edit_fio'
                self.edit_screen(user, screens.card('fio', user), call.message.id)

            # only byn
            elif call.data.endswith('bank_byn'):
                bank = int(call.data.split('_')[1])
                user.pop_data.update({'bank': services.popular_belarus_bank[bank]})
                user.pop_data.update({'type': 'card'})
                self.edit_screen(user, screens.card('type_card', user), call.message.id)
                user.position = 'card_edit_type_card'

        # create ask
        elif call.data.startswith('ask'):

            # choose first currency
            if call.data.endswith('fcurrency'):
                currency = call.data.split('_')[1]
                # test card
                cards = user.getCards(currency = currency)
                if len(cards) == 0:
                    self.edit_screen(user, screens.create_asks('havent_cards', user), call.message.id)
                else:
                    user.pop_data.update({'fcurrency': currency})
                    user.position = 'create_ask_count'
                    self.edit_screen(user, screens.create_asks('count', user), call.message.id)

            # incomplete
            elif call.data.endswith('incomplete'):
                incomplete = int(call.data.split('_')[1])
                if incomplete == 1:
                    user.pop_data.update({'incomplete': 1})
                    user.position = 'create_ask_count_incomplete'
                    self.edit_screen(user, screens.create_asks('incomplete_count', user), call.message.id)
                else:
                    user.pop_data.update({'incomplete': 0})
                    self.edit_screen(user, screens.create_asks('choose_s', user), call.message.id)

            # choose second currency
            elif call.data.endswith('scurrency'):
                currency = call.data.split('_')[1]
                cards = user.getCards(currency = currency)
                if len(cards) == 0:
                    self.edit_screen(user, screens.create_asks('havent_cards', user), call.message.id)
                else:
                    user.pop_data.update({'scurrency': currency})
                    self.edit_screen(user, screens.create_asks('rate', user, self.Rates), call.message.id)
                    user.position = 'create_ask_rate'

            # choose rate cbrf
            elif call.data.endswith('rate'):
                user.pop_data.update({'rate': user.pop_data['cbrf_rate']})
                self.create_ask_5_step(user, call.message.id)

            # choose cards
            elif call.data.endswith('cards'):
                pos = call.data.split('_')[1]
                if pos == 'next':
                    self.create_ask_6_step(user, call.message.id)
                else:
                    ind = list(user.pop_data['cards_name'].keys())[int(pos)]
                    if user.pop_data['cards_name'][ind] == 1:
                        user.pop_data['cards_name'][ind] = 0
                    else:
                        user.pop_data['cards_name'][ind] = 1

                    self.edit_screen(user, screens.create_asks('get_fiat_card', user, self.Rates), call.message.id)

            elif call.data.endswith('vscard'):
                num = int(call.data.split('_')[1])
                vst_cards = user.getCards(currency = 'v' + user.pop_data['vst'])
                card = vst_cards[int(num)]
                user.pop_data.update({'vstcard': card.id})
                ask = user.make_ask(self.Rates)
                Asks.unSaveAsks.update({user.trade_id: {'ask':ask, 'time': time.time()}})
                self.edit_screen(user, screens.create_asks('preview', user, Ask = ask), call.message.id)

            # choose banks
            elif call.data.endswith('banks'):
                num = call.data.split('_')[1]
                if num == 'next':
                    # fool check
                    if sum([i for i in user.pop_data['banks'].values()]):
                        self.create_ask_6_step(user, call.message.id)
                    else:
                        self.edit_screen(user, screens.create_asks('get_fiat_banks', user), call.message.id)
                elif num == 'everyone':
                    user.pop_data['banks'] = {'everyone': 1}
                    self.create_ask_6_step(user, call.message.id)
                else:
                    num = int(num)
                    ind = list(user.pop_data['banks'].keys())[num]
                    if user.pop_data['banks'][ind] == 0:
                        user.pop_data['banks'][ind] = 1
                    else:
                        user.pop_data['banks'][ind] = 0
                    self.edit_screen(user, screens.create_asks('get_fiat_banks', user), call.message.id)

            # ready
            elif call.data.endswith('prew'):
                ans = call.data.split('_')[1]
                if ans == 'yes':
                    ask = Asks.addAsk(user.trade_id)
                    self.edit_screen(user, screens.create_asks('public', user, Ask = ask), call.message.id)
                else:
                    Asks.unSaveAsks.pop(user.trade_id)
                    self.edit_screen(user, screens.create_asks('not_public', user), call.message.id)

        # my asks
        elif call.data.startswith('myask'):
            if call.data.endswith('add'):
                user.clear()
                self.edit_screen(user, screens.create_asks('choose_f', user), call.message.id)

            elif call.data.endswith('_show'):
                id = call.data.split('_')[1]
                self.edit_screen(user, screens.my_asks(f'show{id}', user), call.message.id)

            elif call.data.endswith('_del'):
                id = call.data.split('_')[1]
                self.edit_screen(user, screens.my_asks(f'del_confirm{id}', user), call.message.id)

            elif call.data.endswith('_delconf'):
                id = call.data.split('_')[1]
                Asks.getAsk(id).setStatus('removed')
                self.edit_screen(user, screens.my_asks(f'confdel{id}', user), call.message.id)
                self.send_screen(user, screens.my_asks('main', user))

            else:
                self.edit_screen(user, screens.my_asks('main', user), call.message.id)

        # find asks
        elif call.data.startswith('d_ask'):
            if call.data.endswith('fcurrency'):
                cur = call.data.split('_')[2]

                cards = user.getCards(currency = cur)
                if len(cards) == 0:
                    self.edit_screen(user, screens.create_asks('havent_cards', user), call.message.id)
                    return

                user.pop_data.update({'d_currency': cur})
                if cur in ['veur', 'vusd']:
                    user.pop_data.update({'d_type': 'fiat'})
                    self.edit_screen(user, screens.show_asks('choose_fiat_cur', user), call.message.id)
                else:
                    user.pop_data.update({'d_type': 'vst'})
                    self.edit_screen(user, screens.show_asks('choose_vst_cur', user), call.message.id)

            elif call.data.endswith('scurrency'):
                cur = call.data.split('_')[2]

                cards = user.getCards(currency = cur)
                if len(cards) == 0:
                    self.edit_screen(user, screens.create_asks('havent_cards', user), call.message.id)
                    return

                user.pop_data.update({'d_scurrency': cur})
                vst_cur, fiat_cur = services.find_vst_fiat(user.pop_data['d_currency'], cur)
                user.pop_data.update({
                    'd_vst': vst_cur,
                    'd_fiat': fiat_cur
                })

                if user.pop_data['d_type'] == 'fiat':
                    cards = user.getCards(currency = user.pop_data['d_fiat'])
                    cards_name = {i.name: 0 for i in cards}
                    user.pop_data.update({'d_cards_name': cards_name})
                    self.edit_screen(user, screens.show_asks('get_fiat_card', user), call.message.id)
                else:
                    banks = services.all_banks
                    banks_name = {i: 0 for i in banks}
                    user.pop_data.update({'d_banks': banks_name})
                    user.position = 'd_ask_banks'
                    self.edit_screen(user, screens.show_asks('get_fiat_banks', user), call.message.id)

            elif call.data.endswith('cards'):
                pos = call.data.split('_')[2]
                if pos == 'next':
                    if user.pop_data['d_card_after']:
                        self.edit_screen(user, screens.show_asks('vst_send', user), call.message.id)
                    else:
                        self.show_ask_filter(user, call.message.id)
                else:
                    ind = list(user.pop_data['d_cards_name'].keys())[int(pos)]
                    if user.pop_data['d_cards_name'][ind] == 1:
                        user.pop_data['d_cards_name'][ind] = 0
                    else:
                        user.pop_data['d_cards_name'][ind] = 1

                    self.edit_screen(user, screens.show_asks('get_fiat_card', user), call.message.id)

            elif call.data.endswith('banks'):
                num = call.data.split('_')[2]
                if num == 'next':
                    # fool check
                    if sum([i for i in user.pop_data['d_banks'].values()]):
                        self.show_ask_filter(user, call.message.id)
                    else:
                        self.edit_screen(user, screens.show_asks('get_fiat_banks', user), call.message.id)
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
                    self.edit_screen(user, screens.show_asks('get_fiat_banks', user), call.message.id)

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
                    self.send_screen(user, screens.show_asks('show_ask', user, ask))
                else:
                    self.delete_message(user, call.message.id)

            elif call.data.endswith('dealAccept'):
                num = call.data.split('_')[2]
                user.pop_data.update({'d_ask_id': num})
                self.tg_show_original_rel(user, call.message.id)

            elif call.data.endswith('dealIncomplete'):
                num = call.data.split('_')[2]
                user.pop_data.update({'d_ask_id': num, 'd_ask_incomplete': 1})
                user.position = 'd_ask_count_incomplete'
                ask = Asks.getAsk(num)
                self.edit_screen(user, screens.show_asks('incompleteCount', user, ask), call.message.id)

            elif call.data.endswith('vscard'):
                num = call.data.split('_')[2]
                vst_cards = user.getCards(currency = 'v' + user.pop_data['d_vst'])
                card = vst_cards[int(num)]
                user.pop_data.update({'d_vst_card': card.id})
                deal = Deals.makeDeal(user)
                self.delete_message(user, call.message.id)
                self.notification_deal_users(deal)

        # my deals
        elif call.data.startswith('mydeal'):
            if call.data.endswith('show'):
                num = call.data.split('_')[1]
                deal = Deals.getDeal(num)
                self.edit_screen(user, deal.logic_message(user), call.message.id)

        # deal control
        elif call.data.startswith('deal'):
            num = call.data.split('_')[1]
            deal = Deals.getDeal(num)
            user_A = Users.identification(telegramId = deal.vista_people)
            user_B = Users.identification(telegramId = deal.fiat_people)

            if call.data.endswith('vst_sended'):
                if deal.logic_control('vst_sended', user):
                    self.edit_screen(user_A, deal.logic_message(user_A), call.message.id)
                    self.send_screen(user_B, deal.logic_message(user_B))

            elif call.data.endswith('fiat_sended'):
                if deal.logic_control('fiat_sended', user):
                    self.send_screen(user_A, deal.logic_message(user_A))
                    self.edit_screen(user_B, deal.logic_message(user_B), call.message.id)

            elif call.data.endswith('fiat_accept'):
                self.edit_screen(user, screens.deal('5_A_ans', deal, user), call.message.id)

            elif call.data.endswith('vst_after'):
                minutes = int(call.data.split('_')[2])
                deal.vista_send_over = int(time.time() + minutes * 60)
                self.edit_screen(user_A, deal.logic_message(user_A), call.message.id)
                self.edit_screen(user_B, deal.logic_message(user_A), call.message.id)

            # choose card and set timer
            elif call.data.endswith('show_card'):
                card = int(call.data.split('_')[2])
                card = deal.vista_people_fiat_card[card]
                self.edit_screen(user_B, deal.logic_message(user_B, ['show', card]), call.message.id)

            elif call.data.endswith('see_card'):
                self.edit_screen(user_B, deal.logic_message(user_B), call.message.id)

            elif call.data.endswith('choosed_card'):
                card = int(call.data.split('_')[2])
                deal.fiat_choose_card = card
                self.edit_screen(user_B, deal.logic_message(user_B), call.message.id)
                self.edit_screen(user_A, deal.logic_message(user_B), call.message.id)

            elif call.data.endswith('fiat_after'):
                minutes = int(call.data.split('_')[2])
                deal.fiat_send_over = int(time.time() + minutes * 60)
                self.edit_screen(user_B, deal.logic_message(user_B), call.message.id)
                self.edit_screen(user_A, deal.logic_message(user_B), call.message.id)

            elif call.data.endswith('cancel'):
                self.edit_screen(user, screens.deal('cancel', deal), call.message.id)
            elif call.data.endswith('cancel_accept'):
                if deal.logic_control('cancel', user):
                    user.rating -= 1
                    deal.cancel = user.tg_id
                    self.edit_screen(user, deal.logic_message(user), call.message.id)
                    if user_A.tg_id == user.tg_id:
                        self.send_screen(user_B, deal.logic_message(user_B))
                    else:
                        self.send_screen(user_A, deal.logic_message(user_A))

            elif call.data.endswith('moder'):
                self.edit_screen(user, screens.deal('moder', deal), call.message.id)
            elif call.data.endswith('moder_accept'):
                if deal.logic_control('moderate', user):
                    deal.moderate = user.tg_id
                    self.edit_screen(user, deal.logic_message(user), call.message.id)
                    if user_A.tg_id == user.tg_id:
                        self.send_screen(user_B, deal.logic_message(user_B))
                    else:
                        self.send_screen(user_A, deal.logic_message(user_A))

            elif call.data.endswith('none'):
                self.edit_screen(user, deal.logic_message(user), call.message.id)

        elif call.data == 'delete':
            self.delete_message(user, call.message.id)

    # userdata

    def get_email(self, user, text):
        if not services.check_email(text):
            self.send_screen(user, screens.edit_mail('error_format'))
        elif not Users.check('mail', text):
            self.send_screen(user, screens.edit_mail('error_in_base'))
        else:
            user.mail = text
            return True

    def get_phone(self, user, text):
        if not services.check_phone(text):
            self.send_screen(user, screens.edit_phone('error_format'))
        elif not Users.check('phone', text):
            self.send_screen(user, screens.edit_phone('error_in_base'))
        else:
            user.phone = text
            return True

    def get_fio(self, user, text):
        if 5 > len(text) or len(text) > 50:
            self.send_screen(user, screens.edit_fio('error_format'))
        elif not services.check_fio(text):
            self.send_screen(user, screens.edit_fio('error_format'))
        else:
            user.fio = text
            return True

    def get_time_zone(self, user, call):
        key = int(call.data.split('_')[-1])
        if len(services.time_zones) <= key:
            self.send_screen(user, screens.edit_time_zone())
        else:
            user.time_zone = services.time_zones[key]
            self.edit_screen(user, screens.user_info('main', user), call.message.id)

    # card
    def card_edit_finish(self, user):
        id = user.addCard()
        self.send_screen(user, screens.card('card_info_' + str(id), user))

    # ask
    def create_ask_5_step(self, user, edit=None):
        if user.pop_data['fcurrency'] in ['veur', 'vusd']:
            cards = user.getCards(currency = user.pop_data['fiat'])
            cards_name = {i.name: 0 for i in cards}
            user.pop_data.update({'cards_name': cards_name})

            if edit is None:
                self.send_screen(user, screens.create_asks('get_fiat_card', user, self.Rates))
            else:
                self.edit_screen(user, screens.create_asks('get_fiat_card', user, self.Rates), edit)
        else:
            banks = services.all_banks
            banks_name = {i: 0 for i in banks}
            user.pop_data.update({'banks': banks_name})
            user.position = 'create_ask_banks'

            if edit is None:
                self.send_screen(user, screens.create_asks('get_fiat_banks', user))
            else:
                self.edit_screen(user, screens.create_asks('get_fiat_banks', user), edit)

    def create_ask_6_step(self, user, edit=None):
        if user.pop_data['fcurrency'] in ['veur', 'vusd']:
            if edit is None:
                self.send_screen(user, screens.create_asks('vst_send', user, self.Rates))
            else:
                self.edit_screen(user, screens.create_asks('vst_send', user, self.Rates), edit)
        else:
            if edit is None:
                self.send_screen(user, screens.create_asks('get_send', user, self.Rates))
            else:
                self.edit_screen(user, screens.create_asks('get_send', user, self.Rates), edit)

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

    # deal
    def tg_show_original_rel(self, user, tp=0):
        ask = Asks.getAsk(user.pop_data['d_ask_id'])
        if 'd_type' not in user.pop_data or 'd_vst' not in user.pop_data:
            user.pop_data['d_type'] = ask.type
            if user.pop_data['d_type'] == 'fiat':
                user.pop_data.update({
                    'd_vst': ask.get_currency,
                    'd_fiat': ask.have_currency
                })
                user.pop_data['d_card_after'] = 1
                cards = user.getCards(currency = user.pop_data['d_fiat'])
                cards_name = {i.name: 0 for i in cards}
                user.pop_data.update({'d_cards_name': cards_name})
                if tp:
                    self.edit_screen(user, screens.show_asks('get_fiat_card', user), tp)
                else:
                    self.send_screen(user, screens.show_asks('get_fiat_card', user))

            else:
                user.pop_data.update({
                    'd_vst': ask.have_currency,
                    'd_fiat': ask.get_currency,
                    'd_banks': {'everyone': 1}
                })
                if tp:
                    self.edit_screen(user, screens.show_asks('vst_send', user), tp)
                else:
                    self.send_screen(user, screens.show_asks('vst_send', user))

        else:
            if tp:
                self.edit_screen(user, screens.show_asks('vst_send', user), tp)
            else:
                self.send_screen(user, screens.show_asks('vst_send', user))

    def notification_deal_users(self, deal):
        user_A = Users.identification(telegramId = deal.vista_people)
        user_B = Users.identification(telegramId = deal.fiat_people)

        screen_A = deal.logic_message(user_A)
        screen_B = deal.logic_message(user_B)
        if screen_A:
            self.send_screen(user_A, screen_A)
        if screen_B:
            self.send_screen(user_B, screen_B)
