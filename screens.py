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
        buttons.row('💵 Активные заявки', '💵 Мои заявки', '💵 Мои сделки')
        buttons.row('💳 Шаблоны моих карт и счетов')
        buttons.row('❓ Поддержка и информация', '👤 Личный кабинет')

    return text, buttons


def user_info(key, user, UserBase=None):
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
        text = f'Ваша реферальная ссылка: {services.http_bot + str(user.trade_id)}'
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

        cards_name = user.names_cards()
        for i in range(len(cards_name) // 2):
            button1 = telebot.types.InlineKeyboardButton(text = cards_name[i * 2],
                                                         callback_data = 'card_info_' + str(i * 2))
            button2 = telebot.types.InlineKeyboardButton(text = cards_name[i * 2 + 1],
                                                         callback_data = 'card_info_' + str(i * 2 + 1))
            buttons.row(button1, button2)
        if len(cards_name) % 2 == 1:
            button1 = telebot.types.InlineKeyboardButton(text = cards_name[-1],
                                                         callback_data = 'card_info_' + str(len(cards_name) - 1))
            buttons.row(button1)

        button = telebot.types.InlineKeyboardButton(text = '💳 Добавить карту', callback_data = 'card_add')
        buttons.row(button)

    elif key.startswith('card_info'):
        id = int(key.split('_')[-1])
        text = user.cards[id].collect_full('tg')
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = '❌ Удалить', callback_data = 'card_del_' + str(id))
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'card_back')
        buttons.row(button)

    elif key.startswith('del_confirm'):
        id = int(key.split('_')[-1])
        text = user.cards[id].collect_full('tg')
        text += '\n\nВы действительно хотите удалить эту карту?'
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = '✔️ Да', callback_data = 'card_y_del_' + str(id))
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = '❌ Нет', callback_data = 'card_info_' + str(id))
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

    elif key == 'name_alr':
        text = 'Это название уже существует'

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
        text = 'Отправьте номер счета'

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


def create_asks(key, user, Rates = None):
    buttons = None
    if key == 'choose_f':
        text = 'Выберите валюту, которую хотите отдать'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Vista EUR', callback_data = 'ask_veur_fcurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'Vista USD', callback_data = 'ask_vusd_fcurrency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'RUB', callback_data = 'ask_rub_fcurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'USD', callback_data = 'ask_usd_fcurrency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'EUR', callback_data = 'ask_eur_fcurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'BYN', callback_data = 'ask_byn_fcurrency')
        buttons.row(button1, button2)

    elif key == 'havent_cards':
        text = 'У вас нет подходящих карт, добавьте карты в шаблоны.'

    elif key == 'count':
        text = 'Введите сумму, которую хотите обменять'

    elif key == 'count_error':
        text = 'Вы ввели не число. Введите сумму, которую хотите обменять'

    elif key == 'choose_s':
        text = 'Выберите валюту, которую хотите получить'
        if 'fcurrency' not in user.pop_data:
            return create_asks('choose_f', user)

        fcurrency = user.pop_data['fcurrency']
        buttons = telebot.types.InlineKeyboardMarkup()
        if fcurrency in ['veur', 'vusd']:
            button1 = telebot.types.InlineKeyboardButton(text = 'RUB', callback_data = 'ask_rub_scurrency')
            button2 = telebot.types.InlineKeyboardButton(text = 'USD', callback_data = 'ask_usd_scurrency')
            buttons.row(button1, button2)
            button1 = telebot.types.InlineKeyboardButton(text = 'EUR', callback_data = 'ask_eur_scurrency')
            button2 = telebot.types.InlineKeyboardButton(text = 'BYN', callback_data = 'ask_byn_scurrency')
            buttons.row(button1, button2)
        else:
            button1 = telebot.types.InlineKeyboardButton(text = 'Vista EUR', callback_data = 'ask_veur_scurrency')
            button2 = telebot.types.InlineKeyboardButton(text = 'Vista USD', callback_data = 'ask_vusd_scurrency')
            buttons.row(button1, button2)

    elif key == 'rate':
        if 'fcurrency' not in user.pop_data or 'scurrency' not in user.pop_data:
            return create_asks('choose_f', user)

        vst_cur, fiat_cur = services.find_vst_fiat(user.pop_data['fcurrency'], user.pop_data['scurrency'])

        rate = Rates.get_rate(fiat_cur, vst_cur)
        user.pop_data.update({
            'cbrf_rate': rate,
            'fiat': fiat_cur,
            'vst': vst_cur
            })
        text = f'Какой курс хотите использовать? Курс ЦБРФ {rate}'

        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = f'Оставить курс ЦБРФ {rate}', callback_data = 'ask_rate')
        buttons.row(button1)

    elif key == 'rate_error':
        text = 'Неверный курс, укажите правильный курс'

    # elif key == 'get_card':
    #     text = 'На какую карту '
    #     if 'fcurrency' not in user.pop_data or 'scurrency' not in user.pop_data:
    #         return create_asks('choose_f', user)
    #
    #     buttons = telebot.types.InlineKeyboardMarkup()
    #     button1 = telebot.types.InlineKeyboardButton(text = 'Да', callback_data = 'ask_1_alr')
    #     button2 = telebot.types.InlineKeyboardButton(text = 'Нет, создать', callback_data = 'ask_0_alr')
    #     buttons.row(button1, button2)

    elif key == 'get_fiat_card':
        text = f'Выберите карты, куда вы хотите получить {user.pop_data["fiat"]}'
        buttons = telebot.types.InlineKeyboardMarkup()
        
        if sum([i for i in user.pop_data['cards_name'].values()]):
            button1 = telebot.types.InlineKeyboardButton(text = 'Продолжить', callback_data = 'ask_next_cards')
            buttons.row(button1)

        num = 0
        for i in user.pop_data['cards_name']:
            button_text = i
            if user.pop_data['cards_name'][i] == 1:
                button_text += ' ✅'
            button1 = telebot.types.InlineKeyboardButton(text = button_text, callback_data = f'ask_{num}_cards')
            buttons.row(button1)
            num += 1

    elif key == 'get_fiat_banks':
        text = f'Выберите карты, куда вы можете отправить {user.pop_data["fiat"]}'
        buttons = telebot.types.InlineKeyboardMarkup()

        if sum([i for i in user.pop_data['banks'].values()]):
            button1 = telebot.types.InlineKeyboardButton(text = 'Продолжить', callback_data = 'ask_next_banks')
            buttons.row(button1)

        if sum([i for i in user.pop_data['banks'].values()]) != len(user.pop_data['banks']):
            button1 = telebot.types.InlineKeyboardButton(text = 'Любой банк', callback_data = 'ask_everyone_banks')
            buttons.row(button1)

        num = 0
        banks = list(user.pop_data['banks'].keys())
        # make two column
        for i in range(len(banks) // 2):
            button_text1 = banks[i*2]
            if user.pop_data['banks'][button_text1] == 1:
                button_text1 += ' ✅'

            button_text2 = banks[i*2+1]
            if user.pop_data['banks'][button_text2] == 1:
                button_text2 += ' ✅'

            button1 = telebot.types.InlineKeyboardButton(text = button_text1, callback_data = f'ask_{i*2}_banks')
            button2 = telebot.types.InlineKeyboardButton(text = button_text2, callback_data = f'ask_{i*2+1}_banks')
            buttons.row(button1, button2)
            num += 1
        if len(banks) % 2 == 1:
            button_text1 = banks[-1]
            if user.pop_data['banks'][button_text1] == 1:
                button_text1 += ' ✅'
            button1 = telebot.types.InlineKeyboardButton(text = button_text1, callback_data = f'ask_{len(banks) - 1}_banks')
            buttons.row(button1)

    elif key in ['vst_send', 'get_send']:
        if key == 'vst_send':
            text = f'Выберите карту, с которой вы будете отправлять VST {user.pop_data["vst"]}'
        else:
            text = f'Выберите карту, на которую вы хотите получить VST {user.pop_data["vst"]}'

        buttons = telebot.types.InlineKeyboardMarkup()

        vst_cards = user.get_card_currency('v'+ user.pop_data['vst'])

        num = 0
        for i in vst_cards:
            button1 = telebot.types.InlineKeyboardButton(text = i.name, callback_data = f'ask_{num}_vscard')
            buttons.row(button1)
            num += 1

    elif key == 'preview':
        text = user.unsave_pop_data['ask'].preview()
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Опубликовать', callback_data = 'ask_yes_prew')
        button2 = telebot.types.InlineKeyboardButton(text = 'Отмена', callback_data = 'ask_no_prew')
        buttons.row(button1,button2)

    elif key == 'public':
        text = 'Ваша заявка передана на рассмотрение'

    elif key == 'not_public':
        text = 'Заявка не опубликована'

    return text, buttons


def my_asks(key, user, Asks):
    buttons = None
    if key == 'main':
        text = 'Ваши заявки:'
        asks = Asks.get_asks(user.trade_id)
        buttons = telebot.types.InlineKeyboardMarkup()
        for i in asks:
            button1 = telebot.types.InlineKeyboardButton(text = i.button_text(), callback_data = f'myask_{i.id}_show')
            buttons.row(button1)

        button1 = telebot.types.InlineKeyboardButton(text = 'Добавить заявку', callback_data = f'myask_add')
        buttons.row(button1)

    elif key.startswith('show'):
        id = int(key.replace('show', ''))
        ask = Asks.get_ask_from_id(id)
        text = ask.preview()
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Удалить', callback_data = f'myask_{id}_del')
        buttons.row(button1)
        button1 = telebot.types.InlineKeyboardButton(text = 'Назад', callback_data = f'myask')
        buttons.row(button1)

    elif key.startswith('del_confirm'):
        id = int(key.replace('del_confirm', ''))
        ask = Asks.get_ask_from_id(id)
        text = ask.preview()
        text += '\n\n Вы уверены, что хотите удалить эту заявку?'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Да', callback_data = f'myask_{id}_delconf')
        buttons.row(button1)
        button1 = telebot.types.InlineKeyboardButton(text = 'Нет', callback_data = f'myask')
        buttons.row(button1)

    elif key.startswith('confdel'):
        id = key.replace('confdel', '')
        text = f'Ваша заявка <b>{id}</b> была удалена'

    return text, buttons


def show_asks(key, user, Asks, Asks_list = None):
    buttons = None

    if key == 'choose_cur':
        text = 'Выберите валюту, которую хотите отдать'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Vista EUR', callback_data = 'd_ask_veur_fcurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'Vista USD', callback_data = 'd_ask_vusd_fcurrency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'RUB', callback_data = 'd_ask_rub_fcurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'USD', callback_data = 'd_ask_usd_fcurrency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'EUR', callback_data = 'd_ask_eur_fcurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'BYN', callback_data = 'd_ask_byn_fcurrency')
        buttons.row(button1, button2)

    elif key == 'choose_fiat_cur':
        text = 'Выберите валюту, которую хотите получить'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'RUB', callback_data = 'd_ask_rub_scurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'USD', callback_data = 'd_ask_usd_scurrency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'EUR', callback_data = 'd_ask_eur_scurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'BYN', callback_data = 'd_ask_byn_scurrency')
        buttons.row(button1, button2)

    elif key == 'choose_vst_cur':
        text = 'Выберите валюту, которую хотите получить'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Vista EUR', callback_data = 'd_ask_veur_scurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'Vista USD', callback_data = 'd_ask_vusd_scurrency')
        buttons.row(button1, button2)

    elif key == 'get_fiat_card':
        text = f'Выберите карты, куда вы хотите получить {user.pop_data["d_fiat"]}'
        buttons = telebot.types.InlineKeyboardMarkup()

        if sum([i for i in user.pop_data['d_cards_name'].values()]):
            button1 = telebot.types.InlineKeyboardButton(text = 'Продолжить', callback_data = 'd_ask_next_cards')
            buttons.row(button1)

        num = 0
        for i in user.pop_data['d_cards_name']:
            button_text = i
            if user.pop_data['d_cards_name'][i] == 1:
                button_text += ' ✅'
            button1 = telebot.types.InlineKeyboardButton(text = button_text, callback_data = f'd_ask_{num}_cards')
            buttons.row(button1)
            num += 1

    elif key == 'get_fiat_banks':
        text = f'Выберите карты, куда вы можете отправить {user.pop_data["d_fiat"]}'
        buttons = telebot.types.InlineKeyboardMarkup()

        if sum([i for i in user.pop_data['d_banks'].values()]):
            button1 = telebot.types.InlineKeyboardButton(text = 'Продолжить', callback_data = 'd_ask_next_banks')
            buttons.row(button1)

        if sum([i for i in user.pop_data['d_banks'].values()]) != len(user.pop_data['d_banks']):
            button1 = telebot.types.InlineKeyboardButton(text = 'Любой банк', callback_data = 'd_ask_everyone_banks')
            buttons.row(button1)

        num = 0
        banks = list(user.pop_data['d_banks'].keys())
        # make two column
        for i in range(len(banks) // 2):
            button_text1 = banks[i * 2]
            if user.pop_data['d_banks'][button_text1] == 1:
                button_text1 += ' ✅'

            button_text2 = banks[i * 2 + 1]
            if user.pop_data['d_banks'][button_text2] == 1:
                button_text2 += ' ✅'

            button1 = telebot.types.InlineKeyboardButton(text = button_text1, callback_data = f'd_ask_{i * 2}_banks')
            button2 = telebot.types.InlineKeyboardButton(text = button_text2, callback_data = f'd_ask_{i * 2 + 1}_banks')
            buttons.row(button1, button2)
            num += 1
        if len(banks) % 2 == 1:
            button_text1 = banks[-1]
            if user.pop_data['d_banks'][button_text1] == 1:
                button_text1 += ' ✅'
            button1 = telebot.types.InlineKeyboardButton(text = button_text1,
                                                         callback_data = f'd_ask_{len(banks) - 1}_banks')
            buttons.row(button1)

    elif key == 'asks_not_found':
        text = 'Заявка по вашему фильтру не найдена'

    elif key == 'show_asks':
        text = 'Подходящие заявки:'
        buttons = telebot.types.InlineKeyboardMarkup()
        for i in Asks_list[:10]:
            button_text = i.button_text()
            button = telebot.types.InlineKeyboardButton(text = button_text, callback_data = f'd_ask_{i.id}_deal')
            buttons.row(button)

    elif key == 'show_ask':
        text = Asks_list.preview_for_deal()
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Принять', callback_data = f'd_ask_{Asks_list.id}_deal')
        button1 = telebot.types.InlineKeyboardButton(text = 'Не интересно', callback_data = f'delete')
        buttons.row(button, button1)


    return text, buttons