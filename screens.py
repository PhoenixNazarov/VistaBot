import telebot


def welcome(key):
    if key == 'main':
        text = 'Привет, укажи email для регистрации'
    elif key == 'error_format':
        text = 'Неверный формат email'
    elif key == 'error_in_base':
        text = 'Такой email уже зарегистрирован'
    else:
        text = 'Неопознаная ошибка'

    return text, None


def welcome_second(key):
    if key == 'main':
        text = 'Привет, укажи телефон для регистрации'
    elif key == 'error_format':
        text = 'Неверный формат телефона'
    elif key == 'error_in_base':
        text = 'Такой телефон уже зарегистрирован'
    else:
        text = 'Неопознаная ошибка'

    return text, None


def main_screen(key):
    if key == 'main':
        text = 'Главное меню'
        buttons = telebot.types.ReplyKeyboardMarkup()
        buttons.row('Создать заявку на обмен')

    return text, buttons