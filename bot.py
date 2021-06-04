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
            pass

        self.bot.polling(none_stop = True, interval = 0)

    def send_screen(self, user, screen):
        text, buttons = screen
        self.bot.send_message(chat_id = user.tg_id, text = text, reply_markup = buttons)

    def __start_message(self, message):
        user = self.Users.tg_identification(message)
        user.position = 'first_welcome'
        self.send_screen(user, screens.welcome('main'))

    def __message(self, message):
        user = self.Users.tg_identification(message)
        if user.ban:
            return

        if user.position == 'first_welcome':
            self.get_email(user, message.text)
        elif user.position == 'second_welcome':
            self.get_phone(user, message.text)

    def get_email(self, user, text):
        if not services.check_email(text):
            self.send_screen(user, screens.welcome('error_format'))
        elif not self.Users.check('mail', text):
            self.send_screen(user, screens.welcome('error_in_base'))
        else:
            user.mail = text
            user.position = 'second_welcome'
            self.send_screen(user, screens.welcome_second('main'))

    def get_phone(self, user, text):
        if not services.check_phone(text):
            self.send_screen(user, screens.welcome_second('error_format'))
        elif not self.Users.check('phone', text):
            self.send_screen(user, screens.welcome_second('error_in_base'))
        else:
            user.phone = text
            user.position = 'main'
            self.send_screen(user, screens.main_screen('main'))
            self.Users.save()

Bot = Bot()
Bot.initiate()