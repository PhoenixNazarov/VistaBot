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
        if message.text == '👤 Личный кабинет':
            self.send_screen(user, screens.user_info('main', user))
        elif message.text == '❓ Поддержка и информация':
            self.send_screen(user, screens.faq(-1))

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


Bot = Bot()
Bot.initiate()
