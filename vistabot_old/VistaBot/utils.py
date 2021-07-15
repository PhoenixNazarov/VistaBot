from . import db_manager, config, markup
from aiogram import Bot


async def get_order_text(order_id, who='owner', bot: Bot=None):
    order_data = await db_manager.get_order_data(order_id)

    user_id = order_data.get('user_id')
    template_to = order_data.get('template_to')
    template_from = order_data.get('template_from')
    currency_from = order_data.get('currency_from')
    currency_to = order_data.get('currency_to')
    amount = order_data.get('amount')
    exchange_rate = order_data.get('exchange_rate')
    partial = order_data.get('partial')
    amount_to = order_data.get('amount_to')
    amount_from = order_data.get('amount_from')
    converted_amount = order_data.get('converted_amount')
    commission_payer = order_data.get('commission_payer')

    owner_rate = await db_manager.get_user_rating(user_id)

    if who == 'owner':
        if commission_payer == 'owner':
            text = (f'Информация о заявке №{order_id}:\n\n'
                    f'Отдаете (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                    f'Получаете: <b>{amount_to} {currency_to}</b>\n'
                    f'Курс обмена: {exchange_rate}'
                    )
        else:
            text = (f'Информация о заявке №{order_id}:\n\n'
                    f'Отдаете (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                    f'Получаете: <b>{converted_amount} {currency_to}</b>\n'
                    f'Курс обмена: {exchange_rate}'
                    )
    elif who == 'customer':
        if commission_payer == 'customer':
            text = (f'Информация о заявке №{order_id}:\n\n'
                    f'Отдаете (с учетом комиссии сервиса): <b>{amount_to} {currency_to}</b>\n'
                    f'Получаете: <b>{amount_from} {currency_from}</b>\n'
                    f'Курс обмена: {exchange_rate}\n'
                    f'Рейтинг создателя заявки: {owner_rate}'
                    )
        else:
            text = (f'Информация о заявке №{order_id}:\n\n'
                    f'Отдаете (с учетом комиссии сервиса): <b>{amount_to} {currency_to}</b>\n'
                    f'Получаете: <b>{amount} {currency_from}</b>\n'
                    f'Курс обмена: {exchange_rate}\n'
                    f'Рейтинг создателя заявки: {owner_rate}'
                    )
    elif who == 'admin_approve':
        if commission_payer == 'owner':
            text = (f'Новая заявка №{order_id}:\n'
                    f'Создатель: {(await bot.get_chat(user_id)).get_mention(as_html=True)}\n'
                    f'Отдаст (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                    f'Получит: <b>{amount_to} {currency_to}</b>\n\n'
                    f'Покупатель отдаст: <b>{amount_to} {currency_to}</b>\n'
                    f'Покупаель получит: <b>{amount} {currency_from}</b>\n\n'
                    f'Курс обмена: {exchange_rate}\n'
                    f'Рейтинг создателя заявки: {owner_rate}'
                    )
        else:
            text = (f'Новая заявка №{order_id}:\n'
                    f'Создатель: {(await bot.get_chat(user_id)).get_mention(as_html=True)}\n'
                    f'Отдаст (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                    f'Получит: <b>{converted_amount} {currency_to}</b>\n\n'
                    f'Покупатель отдаст: <b>{amount_to} {currency_to}</b>\n'
                    f'Покупаель получит: <b>{amount_from} {currency_from}</b>\n\n'
                    f'Курс обмена: {exchange_rate}\n'
                    f'Рейтинг создателя заявки: {owner_rate}'
                    )
    elif who == 'admin_first_pay':
        order_data = await db_manager.get_buy_order_data(order_id)
        currency_from = order_data.get('currency_from')
        currency_to = order_data.get('currency_to')
        amount_to = order_data.get('amount_to')
        amount_from = order_data.get('amount_from')
        if commission_payer == 'owner':
            text = (f'Заявка №{order_id}:\n'
                    f'Создатель {(await bot.get_chat(order_data.get("owner_id"))).get_mention(as_html=True)} '
                    f'заявки перевел Вам <b>{amount_from} {currency_from}</b>\n\n'
                    f'Пожалуйста, проверьте и подтвердите перевод\n\n'
                    f'Перевод должен поступить со счета:\n'
                    f'{await get_template_text_for_order(order_data.get("template_from"))}'
                    )
        else:
            text = (f'Заявка №{order_id}:\n'
                    f'Покупатель {(await bot.get_chat(order_data.get("customer_id"))).get_mention(as_html=True)} '
                    f'перевел Вам <b>{amount_to} {currency_to}</b>\n\n'
                    f'Пожалуйста, проверьте и подтвердите перевод\n\n'
                    f'Перевод должен поступить со счета:\n'
                    f'{await get_template_text_for_order(order_data.get("customer_template_from"))}'
                    )
        return text
    elif who == 'second_pay':
        order_data = await db_manager.get_buy_order_data(order_id)
        currency_from = order_data.get('currency_from')
        currency_to = order_data.get('currency_to')
        amount_to = order_data.get('amount_to')
        amount_from = order_data.get('amount_from')
        if commission_payer == 'owner':
            text = (f'Заявка №{order_id}:\n'
                    f'Покупатель заявки заявки перевел Вам <b>{amount_to} {currency_to}</b>\n\n'
                    f'Пожалуйста, проверьте и подтвердите перевод\n\n'
                    f'⚠️ ВНИМАНИЕ!\n'
                    f'Ни при каких условиях не нажимайте кнопку «Подтвердить получение», пока лично не убедитесь '
                    f'в поступлении средств, уточнив это в своем банке (интернет-банке).\n'
                    f'Данное действие с вашей стороны является необратимым и отмене не подлежит.\n'
                    f'Подтверждая получение средств, вы несете единоличную финансовую '
                    f'ответственность за свои действия.'
                    )
        else:
            text = (f'Заявка №{order_id}:\n'
                    f'Владелец заявки перевел Вам <b>{amount_from} {currency_from}</b>\n\n'
                    f'Пожалуйста, проверьте и подтвердите перевод\n\n'
                    f'⚠️ ВНИМАНИЕ!\n'
                    f'Ни при каких условиях не нажимайте кнопку «Подтвердить получение», пока лично не убедитесь '
                    f'в поступлении средств, уточнив это в своем банке (интернет-банке).\n'
                    f'Данное действие с вашей стороны является необратимым и отмене не подлежит.\n'
                    f'Подтверждая получение средств, вы несете единоличную финансовую '
                    f'ответственность за свои действия.'
                    )
        return text
    elif who == 'not-enough-second-pay':
        order_data = await db_manager.get_buy_order_data(order_id)
        currency_from = order_data.get('currency_from')
        currency_to = order_data.get('currency_to')
        amount_to = order_data.get('amount_to')
        amount_from = order_data.get('amount_from')
        customer_id = order_data.get("customer_id")
        owner_id = order_data.get("owner_id")
        if commission_payer == 'owner':
            text = (f'⚠️ Заявка №{order_id}:\n'
                    f'⚠️ Покупатель заявки {(await bot.get_chat(customer_id)).get_mention(as_html=True)} '
                    f'должен был перевести <b>{amount_to} {currency_to}</b>\n\n'
                    f'⚠️ Владелец заявки {(await bot.get_chat(owner_id)).get_mention(as_html=True)} '
                    f'сообщает, что пришло меньше, чем должно было')
        else:
            text = (f'⚠️ Заявка №{order_id}:\n'
                    f'⚠️ Владелец заявки {(await bot.get_chat(owner_id)).get_mention(as_html=True)} '
                    f'должен был перевести <b>{amount_from} {currency_from}</b>\n\n'
                    f'⚠️ Покупатель заявки {(await bot.get_chat(customer_id)).get_mention(as_html=True)} '
                    f'сообщает, что пришло меньше, чем должно было')
        return text
    elif who == 'admin_last_pay':
        order_data = await db_manager.get_buy_order_data(order_id)
        if commission_payer == 'owner':
            text = ('Заявка №{}:\n'
                    'Владелец {} заявки подтвердил получение средств\n\n'
                    'Теперь Вы можете перевести покупателю {} <b>{} {}</b> по реквизитам:\n\n'
                    '{}\n\n'
                    '⚠️ <b>ВАЖНО!</b>\n'
                    'После того, как вы совершите перевод, обязательно закройте заявку'
                    .format(order_id,
                            (await bot.get_chat(order_data.get("owner_id"))).get_mention(as_html=True),
                            (await bot.get_chat(order_data.get("customer_id"))).get_mention(as_html=True),
                            order_data.get("amount"), order_data.get("currency_from"),
                            '\n'.join([await get_template_text_for_order(t_id)
                                       for t_id in order_data.get('customer_template_to').split(',')])))
        else:
            text = ('Заявка №{}:\n'
                    'Покупатель {} заявки подтвердил получение средств\n\n'
                    'Теперь Вы можете перевести владельцу {} <b>{} {}</b> по реквизитам:\n\n'
                    '{}\n\n'
                    '⚠️ <b>ВАЖНО!</b>\n'
                    'После того, как вы совершите перевод, обязательно закройте заявку'
                    .format(order_id,
                            (await bot.get_chat(order_data.get("customer_id"))).get_mention(as_html=True),
                            (await bot.get_chat(order_data.get("owner_id"))).get_mention(as_html=True),
                            order_data.get("converted_amount"), order_data.get("currency_to"),
                            '\n'.join([await get_template_text_for_order(t_id)
                                       for t_id in order_data.get('template_to').split(',')])))
        return text
    else:
        text = 'Ошибка'

    if currency_to in ['RUB', 'BYN', 'THB']:
        text += '\nВозможные способы оплаты {}:\n {}' \
            .format(currency_to,
                    '\n'.join([await get_pay_type_text_for_order(t_id) for t_id in template_to.split(',')]))
    elif currency_from in ['RUB', 'BYN', 'THB']:
        text += '\nВозможные способы получения {}:\n {}' \
            .format(currency_from,
                    await get_pay_type_text_for_order(template_from))

    if partial:
        text += '\n\nВозможен частичный выкуп'
    return text


async def get_pay_type_text_for_order(template_id):
    (user_id, acc_type, name, bank, region,
     card_type, holder_name, number, phone) = await db_manager.get_template_data(template_id)
    if acc_type == 'THB':
        return f'- {bank}'
    return f'- {bank} {region} {card_type}'


async def get_template_text(template_id):
    (user_id, acc_type, name, bank, region,
     card_type, holder_name, number, phone) = await db_manager.get_template_data(template_id)

    text = (f'Шаблон <b>{name}</b>\n\n'
            f'Валюта: {acc_type}\n')
    if acc_type in ['RUB', 'BYN']:
        text += (f'Номер карты: {number}\n'
                 f'Банк: {bank} {region} {card_type}\n'
                 f'Вледелец карты: {holder_name}')
    elif acc_type in ['VISTA EUR', 'VISTA USD']:
        text += (f'Номер счета: {number}\n'
                 f'Номер телефона: {phone}')
    elif acc_type == 'THB':
        text += (f'Название банка: {bank}\n'
                 f'Номер счета: {number}\n'
                 f'Держатель счета: {holder_name}')
    return text


async def get_template_text_for_order(template_id):
    (user_id, acc_type, name, bank, region,
     card_type, holder_name, number, phone) = await db_manager.get_template_data(template_id)

    if acc_type in ['RUB', 'BYN']:
        text = (f'Номер карты: {number}\n'
                f'Банк: {bank} {region} {card_type}\n'
                f'Вледелец карты: {holder_name}')
    elif acc_type in ['VISTA EUR', 'VISTA USD']:
        text = (f'Номер счета: {number}\n'
                f'Номер телефона: {phone}')
    elif acc_type == 'THB':
        text = (f'Название банка: {bank}\n'
                f'Номер счета: {number}\n'
                f'Держатель счета: {holder_name}')
    else:
        text = 'Ошибка'
    return text


def get_find_order_button_text(order):
    commission_payer = order.get('commission_payer')
    cur_from = order.get('currency_from')
    amount = order.get('amount')
    amount_from = order.get('amount_from')
    cur_to = order.get('currency_to')
    amount_to = order.get('amount_to')
    exchange_rate = order.get('exchange_rate')

    if commission_payer == 'customer':
        return f'{config.all_template_types[cur_from]["sign"]} {amount_from} ' \
            f'➡️ {config.all_template_types[cur_to]["sign"]} {amount_to} 📈{exchange_rate}'
    else:
        return f'{config.all_template_types[cur_from]["sign"]} {amount} ' \
            f'➡️ {config.all_template_types[cur_to]["sign"]} {amount_to} 📈{exchange_rate}'


def get_owner_orders_button_text(order):
    order_id = order.get('id')
    commission_payer = order.get('commission_payer')
    cur_from = order.get('currency_from')
    amount = order.get('amount')
    converted_amount = order.get('converted_amount')
    amount_from = order.get('amount_from')
    cur_to = order.get('currency_to')
    amount_to = order.get('amount_to')
    exchange_rate = order.get('exchange_rate')

    if commission_payer == 'owner':
        return f'{order_id}. {config.all_template_types[cur_from]["sign"]} {amount_from} ' \
            f'➡️ {config.all_template_types[cur_to]["sign"]} {amount_to} 📈{exchange_rate}'
    else:
        return f'{order_id}. {config.all_template_types[cur_from]["sign"]} {amount} ' \
            f'➡️ {config.all_template_types[cur_to]["sign"]} {converted_amount} 📈{exchange_rate}'


async def get_admin_template_data(t_id):
    admin_template_data = await db_manager.get_admin_template(t_id)
    currency = admin_template_data.get("currency")
    if currency in ['RUB', 'BYN']:
        text = (f'Номер карты: {admin_template_data.get("number")}\n'
                f'Банк: {admin_template_data.get("bank")} {admin_template_data.get("region")}'
                f' {admin_template_data.get("card_type")}\n'
                f'Вледелец карты: {admin_template_data.get("holder_name")}')
    elif currency in ['VISTA EUR', 'VISTA USD']:
        text = (f'Номер счета: {admin_template_data.get("number")}\n'
                f'Номер телефона: {admin_template_data.get("phone")}')
    elif currency == 'THB':
        text = (f'Название банка: {admin_template_data.get("bank")}\n'
                f'Номер счета: {admin_template_data.get("number")}\n'
                f'Держатель счета: {admin_template_data.get("holder_name")}')
    else:
        text = ''
    return text


async def get_my_order(order_id):
    order_data = await db_manager.get_order_data(order_id)
    stage = order_data.get('stage')
    approved = order_data.get('approved')
    blocked = order_data.get('blocked')
    currency_from = order_data.get('currency_from')
    currency_to = order_data.get('currency_to')
    exchange_rate = order_data.get('exchange_rate')
    amount_to = order_data.get('amount_to')
    amount_from = order_data.get('amount_from')
    converted_amount = order_data.get('converted_amount')
    commission_payer = order_data.get('commission_payer')

    if commission_payer == 'owner':
        text = (f'Заявка №{order_id}:\n\n'
                f'Отдаете (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                f'Получаете: <b>{amount_to} {currency_to}</b>\n'
                f'Курс обмена: {exchange_rate}'
                )
    else:
        text = (f'Заявка №{order_id}:\n\n'
                f'Отдаете (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                f'Получаете: <b>{converted_amount} {currency_to}</b>\n'
                f'Курс обмена: {exchange_rate}'
                )

    m = markup.cancel_new_order(order_id)
    if not approved:
        text += '\n\n⏱ Заявка находится на рассмотрении администратором'
    elif not blocked:
        text += '\n\n🔎 Поиск покупателя'
        m = markup.edit_new_order(order_id)
    elif stage is None:
        text += (f'\n\n Запрос на частичный выкуп заявки\n'
                 f'Сумма: <b>{order_data.get("partial_amount")} {currency_from}</b>')
        m = markup.partial_approve(order_id)
    elif stage == 'first_pay':
        if commission_payer == 'owner':
            admin_template_data = await get_admin_template_data(
                await db_manager.get_active_admin_template(order_data.get("currency_from")))
            text += (f'\n\nСейчас Вы должны перевести {order_data.get("amount_from")} '
                     f'{order_data.get("currency_from")} по указанным ниже реквизитам:\n'
                     f'{admin_template_data}\n\n'
                     f'Назначение перевода: Заявка <b>{order_id}</b>\n\n'
                     f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                     f'Обязательно указывайте правильное назначение перевода.\n'
                     f'Заявки с неверным назначением перевода будут обработаны в последнюю очередь.\n\n'
                     f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                     f'После того, как вы совершите перевод, обязательно нажмите кнопку «Перевёл».')
            m = markup.first_pay(order_id)
        else:
            text += '\n\n💸 Ожидает оплату покупателя'
    elif stage == 'first_approve':
        text += '\n\n👨‍💻 Ожидает проверку платежа Гарантом'
    elif stage == 'second_pay':
        if commission_payer == 'owner':
            text += '\n\n💵 Ожидает перевода средств покупателем на Ваш счет'
        else:
            text += ('\n\nСейчас Вы должны перевести '
                     '<b>{} {}</b> по указанным ниже ревизитам:\n'
                     '{}\n\n'
                     '⚠️ <b>ВНИМАНИЕ!</b>\n'
                     'После того, как вы совершите перевод, обязательно нажмите кнопку Перевёл'
                     .format(order_id, order_data.get('amount_from'), order_data.get('currency_from'),
                             '\n\n'.join([await get_template_text_for_order(t_id)
                                          for t_id in order_data.get('customer_template_to').split(',')])))
            m = markup.second_pay(order_id)
    elif stage == 'second_approve':
        if commission_payer == 'owner':
            text += '\n\n⚠️ Ожидает от Вас проверку платежа от клиента на сумму <b>{} {}</b>\n' \
                    'Пожалуйста, подтвердите перевод как только получите его'\
                .format(order_data.get('amount_to'), order_data.get('currency_to'))
            m = markup.second_pay_approve(order_id)
        else:
            text += '\n\n💤 Ожидаем проверку Вашего платежа со стороны покупателя'
    elif stage == 'wait_closing':
        if commission_payer == 'owner':
            text += '\n\n⏰ Ожидаем закрытие заявки Гарантом'
            m = None
        else:
            text += '\n\n⏰ Ожидаем перевода средств Гарантом'
    elif stage == 'closed':
        text += '\n\n✅ Обмен завершен'
        m = None

    return text, m


async def get_admin_active_order(order_id, bot):
    order_data = await db_manager.get_buy_order_data(order_id)
    stage = order_data.get('stage')
    owner_id = order_data.get('owner_id')
    customer_id = order_data.get('customer_id')
    currency_from = order_data.get('currency_from')
    currency_to = order_data.get('currency_to')
    exchange_rate = order_data.get('exchange_rate')
    amount = order_data.get('amount')
    amount_to = order_data.get('amount_to')
    amount_from = order_data.get('amount_from')
    converted_amount = order_data.get('converted_amount')
    commission_payer = order_data.get('commission_payer')

    owner_rate = await db_manager.get_user_rating(owner_id)

    if commission_payer == 'owner':
        text = (f'Заявка №{order_id}:\n'
                f'Создатель: {(await bot.get_chat(owner_id)).get_mention(as_html=True)}\n'
                f'Рейтинг создателя заявки: {owner_rate}\n\n'
                f'Отдаст (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                f'Получит: <b>{amount_to} {currency_to}</b>\n\n'
                f'Покупатель отдаст: <b>{amount_to} {currency_to}</b>\n'
                f'Покупаель получит: <b>{amount} {currency_from}</b>\n\n')
    else:
        text = (f'Заявка №{order_id}:\n'
                f'Создатель: {(await bot.get_chat(owner_id)).get_mention(as_html=True)}\n'
                f'Рейтинг создателя заявки: {owner_rate}\n\n'
                f'Отдаст (с учетом комиссии сервиса): <b>{amount_from} {currency_from}</b>\n'
                f'Получит: <b>{converted_amount} {currency_to}</b>\n\n'
                f'Покупатель отдаст: <b>{amount_to} {currency_to}</b>\n'
                f'Покупаель получит: <b>{amount_from} {currency_from}</b>\n\n')

    text += f'Курс обмена: {exchange_rate}\n\n'

    customer_rate = await db_manager.get_user_rating(customer_id)
    text += (f'Покупатель: {(await bot.get_chat(customer_id)).get_mention(as_html=True)}\n'
             f'Рейтинг покупателя: {customer_rate}\n\n')

    m = None
    if stage == 'first_pay':
        if commission_payer == 'owner':
            text += '⏰ Ожидаем перевода средств на счет Гаранта от Создателя заявки'
        else:
            text += '⏰ Ожидаем перевода средств на счет Гаранта от Покупателя'
    elif stage == 'first_approve':
        if commission_payer == 'owner':
            text += (f'Создатель заявки перевел Вам (Гаранту) <b>{amount_from} {currency_from}</b>\n\n'
                     f'Пожалуйста, проверьте и подтвердите перевод\n\n'
                     f'Перевод должен поступить со счета:\n'
                     f'{await get_template_text_for_order(order_data.get("template_from"))}')
        else:
            text += (f'Покупатель перевел Вам (Гаранту) <b>{amount_to} {currency_to}</b>\n\n'
                     f'Пожалуйста, проверьте и подтвердите перевод\n\n'
                     f'Перевод должен поступить со счета:\n'
                     f'{await get_template_text_for_order(order_data.get("customer_template_from"))}')
        m = markup.admin_first_pay_approve(order_id)
    elif stage == 'second_pay':
        if commission_payer == 'customer':
            text += '⏰ Ожидаем перевода средств на счет Покупателя от Создателя заявки'
        else:
            text += '⏰ Ожидаем перевода средств на счет Создателя заявки от Покупателя'
    elif stage == 'second_approve':
        if commission_payer == 'customer':
            text += '⏰ Ожидаем подтверждения перевода на счет Покупателя'
        else:
            text += '⏰ Ожидаем перевода средств на счет Создателя заявки'
    elif stage == 'wait_closing':
        if commission_payer == 'owner':
            text += ('Создатель заявки подтвердил получение средств\n\n'
                     'Теперь Вы можете перевести покупателю <b>{} {}</b> по реквизитам:\n\n'
                     '{}\n\n'
                     '⚠️ <b>ВАЖНО!</b>\n'
                     'После того, как вы совершите перевод, обязательно закройте заявку'
                     .format(order_data.get("amount"), order_data.get("currency_from"),
                             '\n'.join([await get_template_text_for_order(t_id)
                                        for t_id in order_data.get('customer_template_to').split(',')])))
        else:
            text += ('Покупатель заявки подтвердил получение средств\n\n'
                     'Теперь Вы можете перевести создателю заявки <b>{} {}</b> по реквизитам:\n\n'
                     '{}\n\n'
                     '⚠️ <b>ВАЖНО!</b>\n'
                     'После того, как вы совершите перевод, обязательно закройте заявку'
                     .format(order_data.get("converted_amount"), order_data.get("currency_to"),
                             '\n'.join([await get_template_text_for_order(t_id)
                                        for t_id in order_data.get('template_to').split(',')])))
        m = markup.admin_buy_order_done(order_id)

    return text, m



