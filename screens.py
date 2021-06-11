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
        button = telebot.types.InlineKeyboardButton(text = services.time_zones[i],
                                                    callback_data = 'time_zone_' + str(i))
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

    else:  # main
        text = 'Главное меню:'
        buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons.row('💵 Создать заявку', '💵 Активные заявки')
        buttons.row('💳 Шаблоны моих карт и счетов')
        buttons.row('❓ Поддержка и информация', '👤 Личный кабинет')

    return text, buttons


def user_info(key, user, UserBase = None):
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
        button = telebot.types.InlineKeyboardButton(text = 'Реферальная система', callback_data = 'userdata_referal')
        buttons.row(button)

    elif key == 'change':
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Изменить ФИО', callback_data = 'user_edit_fio')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Изменить mail', callback_data = 'user_edit_mail')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Изменить телефон', callback_data = 'user_edit_phone')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Изменить часовой пояс',
                                                    callback_data = 'user_edit_time_zone')
        buttons.row(button)

    elif key == 'referal':
        text = f'Ваша реферальная ссылка: {services.http_bot+str(user.trade_id)}'
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Список рефералов', callback_data = 'userdata_ref_list')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'userdata_main')
        buttons.row(button)

    elif key == 'referal_list':
        if len(user.referal_list) == 0:
            text = 'Список пуст'
        else:
            text = f'Кол-во рефералов 1ого уровня: {len(user.referal_list)}'
            for i in user.referal_list:
                _referal = UserBase.tg_id_identification(i)
                text += f'\n {_referal.fio}'

        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'userdata_referal')
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

    return text, buttons


def card(key, user):
    buttons = None
    if key == -1:
        text = f'Ваши карты:'
        buttons = telebot.types.InlineKeyboardMarkup()

        cards_name = list(user.cards.keys())
        for i in range(len(cards_name) // 2):
            button1 = telebot.types.InlineKeyboardButton(text = cards_name[i*2], callback_data = 'card_info_'+str(i*2))
            button2 = telebot.types.InlineKeyboardButton(text = cards_name[i*2+1], callback_data = 'card_info_'+str(i*2+1))
            buttons.row(button1, button2)
        if len(cards_name)% 2 == 1:
            button1 = telebot.types.InlineKeyboardButton(text = cards_name[-1], callback_data = 'card_info_'+str(len(cards_name)-1))
            buttons.row(button1)

        button = telebot.types.InlineKeyboardButton(text = '💳 Добавить карту', callback_data = 'card_add')
        buttons.row(button)

    elif key.startswith('card_info'):
        id = int(key.split('_')[-1])
        text = list(user.cards.values())[id]
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = '❌ Удалить', callback_data = 'card_del_'+str(id))
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'card_back')
        buttons.row(button)

    elif key.startswith('del_confirm'):
        id = int(key.split('_')[-1])
        text = list(user.cards.values())[id]
        text += '\n\nВы действительно хотите удалить эту карту?'
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = '✔️ Да', callback_data = 'card_y_del_'+str(id))
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = '❌ Нет', callback_data = 'card_info_'+str(id))
        buttons.row(button)

    # editing
    elif key == 'currency':
        text = 'Выберите валюту для создания карты'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Vista EUR', callback_data = 'card_veur_currency')
        button2 = telebot.types.InlineKeyboardButton(text = 'Vista USD', callback_data = 'card_vusd_currency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'RUB', callback_data = 'card_rub_currency')
        button2 = telebot.types.InlineKeyboardButton(text = 'USD', callback_data = 'card_usd_currency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'EUR', callback_data = 'card_eur_currency')
        button2 = telebot.types.InlineKeyboardButton(text = 'BYN', callback_data = 'card_byn_currency')
        buttons.row(button1, button2)

    elif key == 'name':
        text = 'Напишите название для карты. Например Моя виста'

    elif key == 'name_error':
        text = 'Напишите название для карты. Например Моя виста. Длина должна быть короче 20 символов'

    # only vista
    elif key == 'vista_account':
        text = 'Введите номер счета в формате VST-20140101-123456-978'
    elif key == 'vista_account_error':
        text = 'Неверно. Введите номер счета в формате VST-20140101-123456-978'

    elif key == 'vista_number':
        text = 'Введите привязанный номер телефона'
    elif key == 'vista_number_error':
        text = 'Неверно. Введите привязанный номер телефона'

    # only rub, usd, eur
    elif key == 'choose_type':
        text = 'Выберите тип'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Карта', callback_data = 'card_card_type')
        buttons.row(button1)
        button1 = telebot.types.InlineKeyboardButton(text = 'Счет', callback_data = 'card_account_type')
        buttons.row(button1)
        button1 = telebot.types.InlineKeyboardButton(text = 'PayPal', callback_data = 'card_paypal_type')
        buttons.row(button1)

    elif key == 'choose_bank':
        text = 'Выберите банк или напишите сами'
        buttons = telebot.types.InlineKeyboardMarkup()
        for i in range(len(services.popular_russian_bank)):
            button1 = telebot.types.InlineKeyboardButton(text = services.popular_russian_bank[i],
                                                         callback_data = 'card_' + str(i) + '_bank')
            buttons.row(button1)

    elif key == 'type_card':
        text = 'Тип карты'
        buttons = telebot.types.InlineKeyboardMarkup()
        for i in range(len(services.card_type)):
            button1 = telebot.types.InlineKeyboardButton(text = services.card_type[i],
                                                         callback_data = 'card_' + str(i) + '_tcard')
            buttons.row(button1)

    elif key == 'bik':
        text = 'Отправьте БИК'

    elif key == 'fio':
        text = 'Отправьте ФИО'

    elif key == 'card_number':
        text = 'Отправьте номер карты'

    elif key == 'account_number':
        text = 'Отправьте ФИО'

    elif key == 'mail':
        text = 'Отправьте email, привязанный к PayPal'

    # only byn
    elif key == 'choose_bank_byn':
        text = 'Выберите банк или напишите сами'
        buttons = telebot.types.InlineKeyboardMarkup()
        for i in range(len(services.popular_belarus_bank)):
            button1 = telebot.types.InlineKeyboardButton(text = services.popular_belarus_bank[i],
                                                         callback_data = 'card_' + str(i) + '_bank_byn')
            buttons.row(button1)

    elif key == 'date_end':
        text = 'Отправьте срок действия в формате 01/12'

    return text, buttons