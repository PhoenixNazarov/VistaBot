import telebot
import json
import services


def edit_mail(key):
    if key == 'main':
        text = 'Привет, укажи email'
    elif key == 'error_format':
        text = 'Неверный формат email'
    elif key == 'error_in_base':
        text = 'Такой email уже зарегистрирован'
    else:
        text = 'Неопознаная ошибка'

    return text, None


def edit_phone(key):
    if key == 'main':
        text = 'Привет, укажи телефон'
    elif key == 'error_format':
        text = 'Неверный формат телефона'
    elif key == 'error_in_base':
        text = 'Такой телефон уже зарегистрирован'
    else:
        text = 'Неопознаная ошибка'

    return text, None


def edit_fio(key):
    if key == 'main':
        text = 'Привет, укажи своё ФИО'
    elif key == 'error_format':
        text = 'Неверный формат ФИО'
    else:
        text = 'Неопознаная ошибка'

    return text, None


def edit_time_zone():
    text = 'Выберите часовой пояс, относительно Москвы'
    buttons = telebot.types.InlineKeyboardMarkup()
    for i in range(len(services.time_zones)):
        button = telebot.types.InlineKeyboardButton(text = services.time_zones[i], callback_data = 'time_zone_'+str(i))
        buttons.row(button)

    return text, buttons


def main_screen(key):
    if key == 'info':
        text = 'Поддержка и информация:'
        buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons.row('Техподдержка', 'Мои партнеры')
        buttons.row('Правила обмена')
        buttons.row('Обучение', 'Сайт', 'VK')
        buttons.row('Мои активные заявки', 'Назад')

    else:# main
        text = 'Главное меню:'
        buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons.row('💵 Создать заявку', '💵 Активные заявки')
        buttons.row('💳 Шаблоны моих карт и счетов')
        buttons.row('❓ Поддержка и информация', '👤 Личный кабинет')

    return text, buttons


def user_info(key, user):
    text = f'<b>Ваш личный кабинет:</b>' \
           f'\n' \
           f'\n🆔 Идентификатор: {user.trade_id}' \
           f'\n🧰 Количество ваших заявок: 0' \
           f'\n⭐ Рейтинг: {user.rating}' \
           f'\n' \
           f'\nФИО: {user.fio}' \
           f'\nНомер телефона: {user.phone}' \
           f'\nE-Mail: {user.mail}' \
           f'\nЧасовой пояс: {user.time_zone}'

    if key == 'main':
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Редактировать данные', callback_data = 'userdata_change')
        buttons.row(button)

    elif key == 'change':
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Изменить ФИО', callback_data = 'user_edit_fio')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Изменить mail', callback_data = 'user_edit_mail')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Изменить телефон', callback_data = 'user_edit_phone')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Изменить часовой пояс', callback_data = 'user_edit_time_zone')
        buttons.row(button)

    return text, buttons


def faq(key):
    with open('base/faq.json', 'r', encoding = 'utf-8') as file:
        question_base = json.loads(file.read())
    if key == -1 or key >= len(question_base):
        text = 'Что вас интересует?'
    else:
        text = question_base[key][1]

    buttons = telebot.types.InlineKeyboardMarkup()
    for i in range(len(question_base)):
        if key == i:
            button = telebot.types.InlineKeyboardButton(text = question_base[i][0], callback_data = 'None')
        else:
            button = telebot.types.InlineKeyboardButton(text = question_base[i][0], callback_data = 'faq_' + str(i))
        buttons.row(button)

    return text,buttons



