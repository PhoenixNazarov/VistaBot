import telebot

import users
import screens

class Bot:
    def __init__(self):
        self.token = '1229678012:AAELEl3SUr3arUWH5sQD2jP6njscOxGZS_c'
        self.bot = telebot.TeleBot(self.token)
        self.Users = users.Users()

    def initiate(self):
        @self.bot.message_handler(commands = ['start'])
        def start_message_oper(message):
            pass

        @self.bot.message_handler(content_types = ['text'])
        def message_oper(message):
            self.__message(message)

        @self.bot.callback_query_handler(func = lambda call: True)
        def query_oper(call):
            pass

        self.bot.polling(none_stop = True, interval = 0)

    def __start_message(self, message):
        self.Users


    def __message(self, message):
        user = self.Users.tg_identification(message)
        if user.ban:
            return

        print(message.chat.first_name)

Bot = Bot()
Bot.initiate()