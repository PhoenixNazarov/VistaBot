import time

import telebot
import json
import services

from classes import Asks, Users, Deals, ReferralWithdrawal
Asks = Asks()
Users = Users()
Deals = Deals()
ReferralWithdrawal = ReferralWithdrawal()


def edit_mail(key):
    if key == 'main':
        text = 'Привет! Для регистрации укажите Ваш e-mail!'
    elif key == 'error_format':
        text = 'Неверный формат email'
    elif key == 'error_in_base':
        text = 'Такой email уже зарегистрирован'

    return text, None


def edit_phone(key):
    if key == 'main':
        text = 'Укажите свой действующий номер телефона в формате с кодом (+7, +375, +380 ит.д.)для связи администратора с Вами в случае возникновения проблем по Вашим обменам!'
    elif key == 'error_format':
        text = 'Неверный формат номера телефона!' \
               '\nУкажите свой действующий номер телефона в формате  с кодом (+7, +375, +380 ит.д.)для связи администратора с вами в случае возникновения проблем по Вашим обменам!'
    elif key == 'error_in_base':
        text = 'Такой телефон уже зарегистрирован'

    return text, None


def edit_fio(key):
    if key == 'main':
        text = 'Укажите ФИО (в формате Иванов Иван Иванович или Ivanov Ivan Ivanovich)'
    elif key == 'error_format':
        text = 'Неверный формат ФИО'

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
    text = 'Главное меню:'
    buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
    buttons.row('💵 Активные заявки', '💵 Мои заявки', '💵 Мои сделки')
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
    buttons = None

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
        text = f'Ваша реферальная ссылка: {services.http_bot + str(user.trade_id)}' \
               f'\nVista USD: {user.vusd}' \
               f'\nVista EUR: {user.veur}'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Вывести Vista Usd', callback_data = 'userdata_ref_getu')
        button2 = telebot.types.InlineKeyboardButton(text = 'Вывести Vista Eur', callback_data = 'userdata_ref_gete')
        buttons.row(button1, button2)
        button = telebot.types.InlineKeyboardButton(text = 'Список рефералов', callback_data = 'userdata_ref_list')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'userdata_main')
        buttons.row(button)

    elif key == 'card_vusd':
        if len(user.getCards(currency = 'vusd')) == 0:
            text = 'Создайте шаблон счета VISTA USD или VISTA EUR для вывода вознаграждения'
        else:
            text = 'Выберите соответствующий шаблон для вывода VISTA USD'

            buttons = telebot.types.InlineKeyboardMarkup()
            num = 0
            for i in user.getCards(currency = 'vusd'):
                button1 = telebot.types.InlineKeyboardButton(text = i.name, callback_data = f'userdata_{num}_cardsu')
                buttons.row(button1)
                num += 1
            button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'userdata_main')
            buttons.row(button)

    elif key == 'card_veur':
        if len(user.getCards(currency = 'veur')) == 0:
            text = 'Создайте шаблон счета VISTA USD или VISTA EUR для вывода вознаграждения'
        else:
            text = 'Выберите соответствующий шаблон для вывода VISTA EUR'

            buttons = telebot.types.InlineKeyboardMarkup()
            num = 0
            for i in user.getCards(currency = 'veur'):
                button1 = telebot.types.InlineKeyboardButton(text = i.name, callback_data = f'userdata_{num}_cardse')
                buttons.row(button1)
                num += 1
            button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'userdata_main')
            buttons.row(button)

    elif key == 'card_choose':
        text = 'Ваша заявка добавлена в очередь на вывод'

    elif key == 'low_money':
        text = f'Минимальная сумма для вывода:' \
               f'\nVISTA USD: {services.referral_withdrawal_usd} VST USD' \
               f'\nVISTA EUR: {services.referral_withdrawal_eur} VST EUR'

    elif key == 'referal_list':
        referrals = user.getReferrals()
        if len(referrals) == 0:
            text = 'Список пуст'
        else:
            text = f'Кол-во рефералов 1ого уровня: {len(referrals)}'
            for i in referrals:
                text += f'\n{i.fio}'

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
    text = 'error card'
    buttons = None
    if key == -1:
        text = f'Ваши карты:'
        buttons = telebot.types.InlineKeyboardMarkup()

        cards = [(i.name, i.id) for i in user.getCards()]
        for i in range(len(cards) // 2):
            button1 = telebot.types.InlineKeyboardButton(text = cards[i * 2][0],
                                                         callback_data = 'card_info_' + str(cards[i * 2][1]))
            button2 = telebot.types.InlineKeyboardButton(text = cards[i * 2 + 1][0],
                                                         callback_data = 'card_info_' + str(cards[i * 2][1]))
            buttons.row(button1, button2)
        if len(cards) % 2 == 1:
            button1 = telebot.types.InlineKeyboardButton(text = cards[-1][0],
                                                         callback_data = 'card_info_' + str(cards[-1][1]))
            buttons.row(button1)

        button = telebot.types.InlineKeyboardButton(text = '💳 Добавить карту', callback_data = 'card_add')
        buttons.row(button)

    elif key.startswith('card_info'):
        id = int(key.split('_')[-1])
        text = user.getCard(id).collect_full('tg')
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = '❌ Удалить', callback_data = 'card_del_' + str(id))
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = '⬅️ Назад', callback_data = 'card_back')
        buttons.row(button)

    elif key.startswith('del_confirm'):
        id = int(key.split('_')[-1])
        text = user.getCard(id).collect_full('tg')
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
        text = 'Введите привязанный к счету номер телефона в формате указанном при регистрации счета VISTA'
    elif key == 'vista_number_error':
        text = 'Неверно. Введите привязанный к счету номер телефона в формате указанном при регистрации счета VISTA'

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
        text = 'Отправьте фамилию и имя, привязанные к карте'

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


def create_asks(key, user, Rates=None, Ask=None):
    text = 'error create_asks'
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
        text = 'У Вас нет подходящего шаблона. Создайте шаблон!'

    elif key == 'count':
        text = 'Введите сумму, которую хотите обменять'

    elif key == 'count_error':
        text = 'Вы ввели неправильное число.'

    elif key == 'incomplete':
        text = 'Разрешить частичный выкуп?'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Да', callback_data = 'ask_1_incomplete')
        button2 = telebot.types.InlineKeyboardButton(text = 'Нет', callback_data = 'ask_0_incomplete')
        buttons.row(button1, button2)

    elif key == 'incomplete_count':
        text = 'Напишите минимальную сумму для выкупа:'

    elif key == 'choose_s':
        text = 'Выберите валюту, которую хотите получить:'
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
        text = f'Выберите шаблон, куда Вы хотите получить {user.pop_data["fiat"]}'
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
        text = f'Выберите банки, куда вы можете отправить {user.pop_data["fiat"]}' \
               f'\n<b>ВНИМАНИЕ!</b> При отправке на другие банки может взиматься дополнительная комиссия, тем самым выбрав другой банк Вы соглашаетесь с комиисией, которую заплатите!'
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
            button_text1 = banks[i * 2]
            if user.pop_data['banks'][button_text1] == 1:
                button_text1 += ' ✅'

            button_text2 = banks[i * 2 + 1]
            if user.pop_data['banks'][button_text2] == 1:
                button_text2 += ' ✅'

            button1 = telebot.types.InlineKeyboardButton(text = button_text1, callback_data = f'ask_{i * 2}_banks')
            button2 = telebot.types.InlineKeyboardButton(text = button_text2, callback_data = f'ask_{i * 2 + 1}_banks')
            buttons.row(button1, button2)
            num += 1
        if len(banks) % 2 == 1:
            button_text1 = banks[-1]
            if user.pop_data['banks'][button_text1] == 1:
                button_text1 += ' ✅'
            button1 = telebot.types.InlineKeyboardButton(text = button_text1,
                                                         callback_data = f'ask_{len(banks) - 1}_banks')
            buttons.row(button1)

    elif key in ['vst_send', 'get_send']:
        if key == 'vst_send':
            text = f'Выберите шаблон VISTA, с которого Вы будете отправлять VST {user.pop_data["vst"]}'
        else:
            text = f'Выберите шаблон VISTA, на который Вы хотите получить VST {user.pop_data["vst"]}'

        buttons = telebot.types.InlineKeyboardMarkup()

        vst_cards = user.getCards(currency = 'v' + user.pop_data['vst'])

        num = 0
        for i in vst_cards:
            button1 = telebot.types.InlineKeyboardButton(text = i.name, callback_data = f'ask_{num}_vscard')
            buttons.row(button1)
            num += 1

    elif key == 'preview':
        text = Ask.preview()
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Опубликовать', callback_data = 'ask_yes_prew')
        button2 = telebot.types.InlineKeyboardButton(text = 'Отмена', callback_data = 'ask_no_prew')
        buttons.row(button1, button2)

    elif key == 'public':
        text = f'<b>Ваша заявка №{Ask.id}</b> передана на рассмотрение'

    elif key == 'not_public':
        text = 'Заявка не опубликована'

    elif key == 'admin_public':
        text = 'Заявка опубликована на витрине\n'
        text += Ask.preview()

    elif key == 'admin_unpublic':
        text = 'Заявка отклонена администратором\n'
        text += Ask.preview()

    return text, buttons


def my_asks(key, user):
    text = 'error my_asks'
    buttons = None
    if key == 'main':
        text = 'Ваши заявки:'
        asks = Asks.getAsks(idOwner = user.trade_id, status = 'ok')
        buttons = telebot.types.InlineKeyboardMarkup()
        for i in asks:
            button1 = telebot.types.InlineKeyboardButton(text = i.button_text(), callback_data = f'myask_{i.id}_show')
            buttons.row(button1)

        button1 = telebot.types.InlineKeyboardButton(text = 'Добавить заявку', callback_data = f'myask_add')
        buttons.row(button1)

    elif key.startswith('show'):
        id = int(key.replace('show', ''))
        ask = Asks.getAsk(id)
        text = ask.preview()
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Удалить', callback_data = f'myask_{id}_del')
        buttons.row(button1)
        button1 = telebot.types.InlineKeyboardButton(text = 'Назад', callback_data = f'myask')
        buttons.row(button1)

    elif key.startswith('del_confirm'):
        id = int(key.replace('del_confirm', ''))
        ask = Asks.getAsk(id)
        text = ask.preview()
        text += '\n\nВы уверены, что хотите удалить эту заявку?'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Да', callback_data = f'myask_{id}_delconf')
        buttons.row(button1)
        button1 = telebot.types.InlineKeyboardButton(text = 'Нет', callback_data = f'myask')
        buttons.row(button1)

    elif key.startswith('confdel'):
        id = key.replace('confdel', '')
        text = f'Ваша заявка <b>{id}</b> была удалена'

    return text, buttons


def show_asks(key, user, Asks_list=None):
    text = 'error show_asks'
    buttons = None

    if key == 'choose_cur':
        text = 'Выберите валюту, которую хотите отдать:'
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
        text = 'Выберите валюту, которую хотите получить:'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'RUB', callback_data = 'd_ask_rub_scurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'USD', callback_data = 'd_ask_usd_scurrency')
        buttons.row(button1, button2)
        button1 = telebot.types.InlineKeyboardButton(text = 'EUR', callback_data = 'd_ask_eur_scurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'BYN', callback_data = 'd_ask_byn_scurrency')
        buttons.row(button1, button2)

    elif key == 'choose_vst_cur':
        text = 'Выберите валюту, которую хотите получить:'
        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Vista EUR', callback_data = 'd_ask_veur_scurrency')
        button2 = telebot.types.InlineKeyboardButton(text = 'Vista USD', callback_data = 'd_ask_vusd_scurrency')
        buttons.row(button1, button2)

    elif key == 'get_fiat_card':
        text = f'Выберите шаблон, куда вы хотите получить {user.pop_data["d_fiat"]}' \
               f'\n\n<b>ВНИМАНИЕ!</b>' \
               f'\nЕсли вы приняли заявку, в которой указаны конкретные банки и регионы, куда создатель заявки может отправить средства, но при этом в качестве своих реквизитов для получения средств указали другой банк, отправитель переведет вам меньшую сумму, на величину комиссии, которую он заплатит за перевод вам.' \
               f'\nВсегда обращайте внимание на список банков, указанных в заявках.'

        buttons = telebot.types.InlineKeyboardMarkup()

        if sum([i for i in user.pop_data['d_cards_name'].values()]):
            button1 = telebot.types.InlineKeyboardButton(text = 'Продолжить', callback_data = 'd_ask_next_cards')
            buttons.row(button1)
            text = f'Вы можете принимать средства на любую карту и счёт, для которых создали шаблоны.' \
                   f'\nТаким образом, ваш партнер по обмену сможет перевести средства на удобную ему карту или счёт с минимальной комиссией.' \
                   f'\n\nЧтобы добавить другие карты или счета для получения средств, выберите их из списка ниже, либо нажмите кнопку «Продолжить» для продолжения:'

        num = 0
        for i in user.pop_data['d_cards_name']:
            button_text = i
            if user.pop_data['d_cards_name'][i] == 1:
                button_text += ' ✅'
            button1 = telebot.types.InlineKeyboardButton(text = button_text, callback_data = f'd_ask_{num}_cards')
            buttons.row(button1)
            num += 1

    elif key == 'get_fiat_banks':
        text = f'Выберите банки, куда вы можете отправить {user.pop_data["d_fiat"]}'
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
            button2 = telebot.types.InlineKeyboardButton(text = button_text2,
                                                         callback_data = f'd_ask_{i * 2 + 1}_banks')
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

        index = user.pop_data['filter']['index']

        for i in Asks_list:
            button_text = i.button_text(reverse = True)
            button = telebot.types.InlineKeyboardButton(text = button_text, callback_data = f'd_ask_{i.id}_deal')
            buttons.row(button)

        max_index = Asks.amount()
        max_index = max_index // 10 + int(max_index % 10 != 0)
        if max_index != 1:
            button1 = telebot.types.InlineKeyboardButton(text = '<=', callback_data = f'd_ask_prev')
            button3 = telebot.types.InlineKeyboardButton(text = f'{index + 1}/{max_index}', callback_data = f'none')
            button2 = telebot.types.InlineKeyboardButton(text = '=>', callback_data = f'd_ask_next')
            if index == 0:
                buttons.row(button3, button2)
            elif index == max_index - 1:
                buttons.row(button1, button3)
            else:
                buttons.row(button1, button3, button2)

    elif key == 'show_ask_for_show':
        text = Asks_list.preview('deal')
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Принять',
                                                    callback_data = f'd_ask_{Asks_list.id}_dealAccept')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Не интересно', callback_data = f'delete')
        buttons.row(button)

    elif key == 'show_ask':
        text = Asks_list.preview('deal')
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Принять',
                                                    callback_data = f'd_ask_{Asks_list.id}_dealAccept')
        buttons.row(button)
        if Asks_list.min_incomplete:
            button = telebot.types.InlineKeyboardButton(text = 'Принять не польностью',
                                                        callback_data = f'd_ask_{Asks_list.id}_dealIncomplete')
            buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'Не интересно', callback_data = f'delete')
        buttons.row(button)

    elif key == 'vst_send':
        if user.pop_data['d_type'] == 'vst':
            text = f'Выберите шаблон Vista {user.pop_data["d_vst"].upper()}, с которого будете отправлять средства:'
        else:
            text = f'Выберите шаблон Vista {user.pop_data["d_vst"].upper()}, на который хотите получить средства:'

        buttons = telebot.types.InlineKeyboardMarkup()

        vst_cards = user.getCards(currency = 'v' + user.pop_data['d_vst'])

        num = 0
        for i in vst_cards:
            button1 = telebot.types.InlineKeyboardButton(text = i.name, callback_data = f'd_ask_{num}_vscard')
            buttons.row(button1)
            num += 1

    elif key == 'incompleteCount':
        if Asks_list.type == 'vst':
            text = f'Введите сумму Vista {Asks_list.have_currency}, которую хотите обменять <b>(число без валюты)</b>' \
                   f'минимальная сумма - <b>{Asks_list.min_incomplete} Vista {Asks_list.have_currency.upper()}</b>'
        else:
            text = f'Введите сумму {Asks_list.have_currency}, которую хотите обменять <b>(число без валюты)</b>' \
                   f'минимальная сумма - <b>{Asks_list.min_incomplete} {Asks_list.have_currency.upper()}</b>'

    # SHOW BOT
    elif key == 'not_reg':
        text = 'Зарегистрируйтесь в боте @Bank_Vista_bot для проведения сделок'

    elif key == 'original_send':
        text = 'Для продолжения сделки перейдите в бот @Bank_Vista_bot'

    return text, buttons


def my_deal(key, user):
    text = 'error my_Deal'
    buttons = None
    if key == 'my_deal':
        deals = Deals.getDeals(idOwner = user.trade_id, active = 'work')
        if len(deals) == 0:
            text = 'У вас нет активных сделок'
        else:
            text = 'Ваши активные сделки'
            buttons = telebot.types.InlineKeyboardMarkup()
            for i in deals:
                button = telebot.types.InlineKeyboardButton(text = i.previewText(type = 'button'),
                                                            callback_data = f'mydeal_{i.id}_show')
                buttons.row(button)

    return text, buttons


def deal(key, Deal, optional=None):
    buttons = None
    helpButtons = True

    # wait_vst
    text = f'Сделка <b>№{Deal.id}!</b>\n\n'
    if key == '1_A':
        text = f'ПОЗДРАВЛЯЕМ!' \
               f'\nМы нашли Вам покупателя на Вашу заявку №{Deal.id}! Для этого Вам необходимо перевести со своего счета VISTA на счет гаранта по следующим реквизитам:' \
               f'\n{Deal.garant_card()}' \
               f'\nСумма перевода (с учетом комиссии сервиса): <b>{Deal.vista_count + Deal.vista_commission} Vista {Deal.vista_currency.upper()}</b>' \
               f'\nКурс обмена: {Deal.show_rate}' \
               f'\n⚠️ Назначение перевода: <code>Заявка {Deal.id}</code> ⚠️' \
               f'\nВНИМАНИЕ!' \
               f'\nОбязательно указывайте правильно назначение перевода "Заявка №{Deal.id}", в противном случае Ваш перевод будет обработан в последнюю очередь!' \
               f''
        # text += f'⚠️ <b>ВНИМАНИЕ!</b> ⚠️' \
        #         f'\nОбязательно указывайте правильное назначение перевода.\n' \
        #         f'\n\n⚠️ Назначение перевода: <code>Заявка {Deal.id}</code> ⚠️' \
        #         f'\n{Deal.garant_card()}' \
        #         f'\nСумма перевода (с учетом комиссии сервиса): <b>{Deal.vista_count} Vista {Deal.vista_currency.upper()}</b>' \
        #         f'\nКурс обмена: {Deal.show_rate}' \
        #         f'\n⚠️ Назначение перевода: <code>Заявка {Deal.id}</code> ⚠️' \
        #         f'\n\n⚠️ <b>ВНИМАНИЕ!</b> ⚠️' \
        #         f'\nОбязательно указывайте правильное назначение перевода. В этом случае ваш перевод будет подтвержден моментально.' \
        #         f'\nЗаявки с неверным назначением перевода будут обработаны в последнюю очередь.'
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Перевёл', callback_data = f'deal_{Deal.id}_vst_sended')
        buttons.row(button)
        if Deal.vista_send_over == 0:
            button = telebot.types.InlineKeyboardButton(text = '15 мин',
                                                        callback_data = f'deal_{Deal.id}_{15}_vst_after')
            button1 = telebot.types.InlineKeyboardButton(text = '30 мин',
                                                         callback_data = f'deal_{Deal.id}_{30}_vst_after')
            button2 = telebot.types.InlineKeyboardButton(text = '1 час',
                                                         callback_data = f'deal_{Deal.id}_{60}_vst_after')
            buttons.row(button, button1, button2)
    elif key == '1_B':
        if Deal.vista_send_over == 0:
            text += 'Ожидайте перевода пользователя A гаранту.'
        else:
            min = int((Deal.vista_send_over - time.time()) // 60)
            sec = int((Deal.vista_send_over - time.time()) % 60)
            text += f'Пользователь A указал, что перевод будет осуществлён через {min}:{sec}.'

    # wait_vst_proof
    elif key == '2_A':
        text += 'Спасибо, информация принята! Пожалуйста, ожидайте подтверждение получения вашего перевода.'
    elif key == '2_B':
        text += 'Пользователь A перевел деньги гаранту, ожидайте подтверждения от гаранта.'

    # wait_fiat
    elif key == '3_A':
        buttons = telebot.types.InlineKeyboardMarkup()
        if Deal.fiat_send_over == 0:
            text += f'Гарант подтвердил получение от Вас средств по сделке. Ожидайте когда покупатель переведет Вам на карту <b>{Deal.fiat_count} {Deal.fiat_currency}</b>'
        else:
            min = int((Deal.fiat_send_over - time.time()) // 60)
            sec = int((Deal.fiat_send_over - time.time()) % 60)
            text += f'Пользователь B указал, что перевод <b>{Deal.fiat_count} {Deal.fiat_currency}</b> будет осуществлён через {min}:{sec}.'

        if Deal.fiat_choose_card:
            text += f'\nНа карту: {Deal.getCards("fiat_choose_card").collect_for_deal()}'

    elif key == '3_B':
        text += f'Гарант подтвердил перевод денег. Переведите <b>{Deal.fiat_count} {Deal.fiat_currency}</b> пользователю A.'
        buttons = telebot.types.InlineKeyboardMarkup()
        k = 0
        for i in Deal.getCards('fiat_cards'):
            button = telebot.types.InlineKeyboardButton(text = i.bank, callback_data = f'deal_{Deal.id}_{k}_show_card')
            k += 1
            buttons.row(button)
    elif key == '3_B_card':
        text += f'Переведите <b>{Deal.fiat_count} {Deal.fiat_currency}</b> пользователю A. ' \
                f'\nВы выбрали эту карту:' \
                f'\n{Deal.getCards(id = optional).collect_for_deal()}'
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Переведу на эту карту',
                                                    callback_data = f'deal_{Deal.id}_{optional}_choosed_card')
        buttons.row(button)
        button = telebot.types.InlineKeyboardButton(text = 'К картам', callback_data = f'deal_{Deal.id}_see_card')
        buttons.row(button)
    elif key == '3_B_with_card':
        text += f'Переведите <b>{Deal.fiat_count} {Deal.fiat_currency}</b> пользователю A. ' \
                f'\nВы выбрали эту карту:' \
                f'\n{Deal.getCards("fiat_choose_card").collect_for_deal()}'
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Перевёл', callback_data = f'deal_{Deal.id}_fiat_sended')
        buttons.row(button)
        if Deal.fiat_send_over == 0:
            button = telebot.types.InlineKeyboardButton(text = '15 мин',
                                                        callback_data = f'deal_{Deal.id}_{15}_fiat_after')
            button1 = telebot.types.InlineKeyboardButton(text = '30 мин',
                                                         callback_data = f'deal_{Deal.id}_{30}_fiat_after')
            button2 = telebot.types.InlineKeyboardButton(text = '1 час',
                                                         callback_data = f'deal_{Deal.id}_{60}_fiat_after')
            buttons.row(button, button1, button2)
        else:
            min = int((Deal.fiat_send_over - time.time()) // 60)
            sec = int((Deal.fiat_send_over - time.time()) % 60)
            text += f'\nОставшееся время: {min}:{sec}'

    # wait_fiat_proof
    elif key == '4_A':
        text += f'Пользователь B перевёл вам <b>{Deal.fiat_count} {Deal.fiat_currency}</b>.' \
                f'\nНа: {Deal.getCards("fiat_choose_card").collect_for_deal()}' \
                f'\nПодтвердите их получение' \
                f'\n\nНи при каких условиях не нажимайте кнопку «Получил», пока лично не убедитесь в поступлении средств, уточнив это в своем банке (интернет-банке).' \
                f'\nДанное действие с вашей стороны является необратимым и отмене не подлежит.' \
                f'\nПодтверждая получение средств, вы несете единоличную финансовую ответственность за свои действия.'
        buttons = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text = 'Получил', callback_data = f'deal_{Deal.id}_fiat_accept')
        buttons.row(button)
    elif key == '4_B':
        text += f'Вы подтвердили перевод <b>{Deal.fiat_count} {Deal.fiat_currency}</b>, ожидайте подтверждения от пользователя A'

    elif key == '5_A_ans':
        import random
        # optional - user
        optional.position = 'count_answer_' + str(Deal.id)
        a = random.randint(1100, 9000)
        b = random.randint(1, 10)
        optional.pop_data.update({'answer': a - b})
        text = f'Если вы лично убедились в поступлении средств и уверены, что хотите подтвердить это, то решите пример и отправьте сообщением боту число с ответом «{a} - {b}»:'
    elif key == '5_A':
        text += f'Вы подтвердили перевод <b>{Deal.fiat_count} {Deal.fiat_currency}</b>, Спасибо за участие в сделке' \
                f'\nВаш рейтинг надежности клиента вскоре будет повышен на 1 балл' \
                f'\nЖдем вас снова!'
    elif key == '5_B':
        text += f'Спасибо за участие в сделке, ожидайте, пока администратор отправит вам {Deal.vista_count} VST {Deal.vista_currency}'

    elif key == '6_A':
        text += 'Вы подтвердили перевод фиантной валюты, Спасибо за участие в сделке'
        return None
    elif key == '6_B':
        text += 'Спасибо за участие в сделке, администратор отправил вам VST' \
                f'\nВаш рейтинг надежности клиента вскоре будет повышен на 1 балл' \
                f'\nЖдем вас снова!'

    elif key == 'cancel':
        text += 'Вы уверены, что хотите отменить сделку?'
        helpButtons = False

        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Да', callback_data = f'deal_{Deal.id}_cancel_accept')
        button2 = telebot.types.InlineKeyboardButton(text = 'Нет', callback_data = f'deal_{Deal.id}_none')
        buttons.row(button1, button2)
    elif key == 'cancel_accept':
        text += 'Заявка отменена, ожидайте отмены администратора'

    elif key == 'moder':
        text += 'Вы уверены, что что-то произошло не так и хотите чтобы с вами связался модератор?'
        helpButtons = False

        buttons = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(text = 'Да', callback_data = f'deal_{Deal.id}_moder_accept')
        button2 = telebot.types.InlineKeyboardButton(text = 'Нет', callback_data = f'deal_{Deal.id}_none')
        buttons.row(button1, button2)
    elif key == 'moder_accept':
        text += 'Заявка поставлена на паузу, ожидайте, когда вам напишет модератор'

    if buttons and helpButtons:
        button1 = telebot.types.InlineKeyboardButton(text = 'Отменить', callback_data = f'deal_{Deal.id}_cancel')
        button2 = telebot.types.InlineKeyboardButton(text = 'Помощь модерации', callback_data = f'deal_{Deal.id}_moder')
        buttons.row(button1, button2)

    return text, buttons


def referral(key, commission=None, commissionCurrency=None):
    buttons = None
    if key == 'bonus':
        text = f'На ваш счет начислено {commission} {commissionCurrency}'

    return text, buttons


def main_screen_show(key):
    buttons = None
    if key == 'main':
        text = 'Главное меню:'
        buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons.row('💵 Фильтр заявок', '💵 Все заявки')

    return text, buttons
