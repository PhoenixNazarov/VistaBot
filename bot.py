import telebot

import users
import screens

import services


class Bot:
    def __init__(self):
        self.token = '1229678012:AAELEl3SUr3arUWH5sQD2jP6njscOxGZS_c'
        self.bot = telebot.TeleBot(self.token)
        self.Users = users.Users()

    def initiate(self):
        @self.bot.message_handler(commands = ['start'])
        def start_message_oper(message):
            self.__start_message(message)

        @self.bot.message_handler(content_types = ['text'])
        def message_oper(message):
            self.__message(message)

        @self.bot.callback_query_handler(func = lambda call: True)
        def query_oper(call):
            self.__query(call)

        self.bot.polling(none_stop = True, interval = 0)

    def send_screen(self, user, screen):
        text, buttons = screen
        self.bot.send_message(chat_id = user.tg_id, text = text, reply_markup = buttons, parse_mode = 'HTML')

    def edit_screen(self, user, screen, message_id):
        text, buttons = screen
        self.bot.edit_message_text(chat_id = user.tg_id, text = text, reply_markup = buttons, message_id = message_id,
                                   parse_mode = 'HTML')

    def __start_message(self, message):
        user = self.Users.tg_identification(message)
        if user.ban:
            return

        if user.mail == '' or user.fio == '' or user.phone == '':
            user.position = 'first_welcome'
            self.send_screen(user, screens.edit_mail('main'))
        else:
            user.position = 'main'
            self.send_screen(user, screens.main_screen('main'))

    def __message(self, message):
        user = self.Users.tg_identification(message)
        if user.ban:
            return

        # set email
        if user.position == 'first_welcome':
            if self.get_email(user, message.text):
                user.position = 'second_welcome'
                self.send_screen(user, screens.edit_phone('main'))

        # set phone
        elif user.position == 'second_welcome':
            if self.get_phone(user, message.text):
                user.position = 'third_welcome'
                self.send_screen(user, screens.edit_fio('main'))

        # set fio
        elif user.position == 'third_welcome':
            if self.get_fio(user, message.text):
                user.position = 'main'
                self.send_screen(user, screens.main_screen('main'))
                self.Users.save()

        # registration end, main menu
        elif message.text == '👤 Личный кабинет':
            user.position = ''
            self.send_screen(user, screens.user_info('main', user))
        elif message.text == '❓ Поддержка и информация':
            user.position = ''
            self.send_screen(user, screens.faq(-1))
        elif message.text == '💳 Шаблоны моих карт и счетов':
            user.position = ''
            self.send_screen(user, screens.card(-1, user))

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
                if services.check_card_name(message.text):
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
                    self.send_screen(user, screens.card('name_error', user))

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
                    user.add_card()
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
                if services.check_fio(message.text):
                    user.pop_data.update({'fio': message.text})
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

    def __query(self, call):
        user = self.Users.tg_identification(call.message)
        if user.ban:
            return

        # user info - EDIT
        if call.data.startswith('userdata'):
            if call.data.endswith('change'):
                self.edit_screen(user, screens.user_info('change', user), call.message.id)
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
                self.edit_screen(user, screens.card('del_confirm_'+id, user), call.message.id)

            elif call.data.startswith('card_del_y'):
                id = int(call.data.split('_')[-1])
                user.remove_card(id)
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
                user.pop_data.update({'type_card': services.card_type[card]})
                user.position = 'card_edit_fio'
                self.edit_screen(user, screens.card('fio', user), call.message.id)

            # only byn
            elif call.data.endswith('bank_byn'):
                bank = int(call.data.split('_')[1])
                user.pop_data.update({'bank': services.popular_belarus_bank[bank]})
                self.edit_screen(user, screens.card('type_card', user), call.message.id)
                user.position = 'card_edit_type_card'

    # userdata
    def get_email(self, user, text):
        if not services.check_email(text):
            self.send_screen(user, screens.edit_mail('error_format'))
        elif not self.Users.check('mail', text):
            self.send_screen(user, screens.edit_mail('error_in_base'))
        else:
            user.mail = text
            return True

    def get_phone(self, user, text):
        if not services.check_phone(text):
            self.send_screen(user, screens.edit_phone('error_format'))
        elif not self.Users.check('phone', text):
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
        id = user.add_card()
        self.send_screen(user, screens.card('card_info_' + str(id), user))
        self.Users.save()


Bot = Bot()
Bot.initiate()
