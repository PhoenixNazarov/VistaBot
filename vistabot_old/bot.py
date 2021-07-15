from asyncio import get_event_loop, create_task
from aiohttp import web

from aiogram import executor, Bot, exceptions
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.webhook import get_new_configured_app

from VistaBot import config, markup, db_manager, utils
from VistaBot.states import User, Registration, Admin, NewTemplate, NewOrder, NewAdminTemplate

from baluhn import verify

loop = get_event_loop()
storage = RedisStorage2()
bot = Bot(config.TOKEN, loop=loop, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)


async def on_startup(disp):
    # await bot.delete_webhook()
    # await bot.set_webhook(WEBHOOK_URL, certificate=open('/etc/nginx/ssl/nginx.crt'))
    print(await bot.get_webhook_info())


async def on_shutdown(disp):
    # await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()


async def create_new_order(user_id, order_data):
    order_id = await db_manager.create_new_order(user_id, *order_data)
    await bot.send_message(user_id,
                           'Создаю заявку...',
                           reply_markup=markup.main())

    settings = await db_manager.get_settings()
    moderate = settings.get('moderate')

    if moderate:
        await bot.send_message(user_id,
                               'Заявка создана и отправлена на одобрение администратором!\n'
                               'После одобрения Вы будете уведомлены!\n\n' +
                               await utils.get_order_text(order_id, 'owner'),
                               reply_markup=markup.cancel_new_order(order_id))
        await bot.send_message(config.manager_id,
                               await utils.get_order_text(order_id, 'admin_approve', bot),
                               reply_markup=markup.approve_new_order(order_id))
    else:
        await db_manager.approve_new_order(order_id)
        await bot.send_message(user_id,
                               f'Заявка была создана под номером {order_id}!',
                               reply_markup=markup.edit_new_order(order_id))
        msg_id = (await bot.send_message(config.order_channel,
                                         await utils.get_order_text(order_id, who='customer'),
                                         reply_markup=markup.buy_order_from_channel(order_id))).message_id
        await db_manager.set_order_msg_id(order_id, msg_id)


async def create_new_template(user_id, state: FSMContext, t_id):
    data = await state.get_data()
    stage = data.get('stage')
    if not stage:
        t_type = data.get('t_type')
        await state.finish()
        await User.main.set()
        await bot.send_message(user_id,
                               'Новый шаблон счета {} был успешно создан!'.format(t_type),
                               reply_markup=markup.main())
        return

    if stage == 'from':
        currency_to = data.get('currency_to')
        await state.update_data({'template_from': t_id})
        await NewOrder.template_to.set()
        templates = await db_manager.get_templates_for_type(user_id, currency_to)
        msg_id = (await bot.send_message(user_id,
                                         'Выберите шаблон для получения {}:'.format(currency_to),
                                         reply_markup=markup.select_template_to(templates, currency_to))).message_id
        await state.update_data({'msg_id': msg_id})
    elif stage == 'to':
        currency_to = data.get('currency_to')
        currency_from = data.get('currency_from')
        template_to = t_id
        template_from = data.get('template_from')
        amount = data.get('amount')
        exchange_rate = data.get('exchange_rate')
        partial = data.get('partial')
        amount_to = data.get('amount_to')
        amount_from = data.get('amount_from')
        converted_amount = data.get('converted_amount')
        commission_payer = data.get('commission_payer')

        await state.finish()
        await User.main.set()
        await create_new_order(user_id,
                               [currency_from, currency_to, amount,
                                converted_amount, amount_from, amount_to,
                                exchange_rate, template_from, template_to,
                                commission_payer, partial])
    elif stage == 'buy-order-to':
        await state.finish()
        await User.main.set()
        await bot.send_message(user_id,
                               f'Новый шаблон счета {data.get("t_type")} был успешно создан!',
                               reply_markup=markup.main())

        order_id = data.get('order_id')
        t_to = t_id
        order_data = await db_manager.get_order_data(order_id)

        if order_data.get('blocked') or not order_data:
            await bot.send_message(user_id,
                                   'Эта заявка больше недоступна!')
            return

        currency_to = order_data.get('currency_to')
        if currency_to in ['VST EUR', 'VST USD', 'THB']:
            templates = await db_manager.get_templates_for_type(user_id, currency_to)
            await bot.send_message(user_id,
                                   f'Выберите шаблон, с которого будете отправлять {currency_to}',
                                   reply_markup=markup.select_t_from_buy_order(order_id, t_to, templates))
            return

        await buy_order(user_id, order_id, t_to)

    elif stage == 'buy-order-from':
        await state.finish()
        await User.main.set()
        await bot.send_message(user_id,
                               f'Новый шаблон счета {data.get("t_type")} был успешно создан!',
                               reply_markup=markup.main())
        order_id = data.get('order_id')
        t_to = data.get('t_to')
        t_from = t_id
        order_data = await db_manager.get_order_data(order_id)

        if order_data.get('blocked') or not order_data:
            await bot.send_message(user_id,
                                   'Эта заявка больше недоступна!')
            return

        await buy_order(user_id, order_id, t_to, t_from)

    elif stage == 'buy-order-to-partial':
        await state.finish()
        await User.main.set()
        await bot.send_message(user_id,
                               f'Новый шаблон счета {data.get("t_type")} был успешно создан!',
                               reply_markup=markup.main())

        order_id = data.get('order_id')
        t_to = t_id
        order_data = await db_manager.get_order_data(order_id)

        if order_data.get('blocked') or not order_data:
            await bot.send_message(user_id,
                                   'Эта заявка больше недоступна!')
            return

        currency_to = order_data.get('currency_to')
        if currency_to in ['VISTA EUR', 'VISTA USD', 'THB']:
            templates = await db_manager.get_templates_for_type(user_id, currency_to)
            await bot.send_message(user_id,
                                   f'Выберите шаблон, с которого будете отправлять {currency_to}',
                                   reply_markup=markup.select_t_from_buy_order_partial(order_id, t_to, templates))
            return

        await User.get_partial_amount.set()
        await state.set_data({'order_id': order_id,
                              't_to': t_to})
        await bot.send_message(user_id,
                               f'Введите сумму {order_data.get("currency_from")} которую хотите купить:',
                               reply_markup=markup.kb_cancel())

    elif stage == 'buy-order-from-partial':
        await state.finish()
        await User.main.set()
        await bot.send_message(user_id,
                               f'Новый шаблон счета {data.get("t_type")} был успешно создан!',
                               reply_markup=markup.main())
        order_id = data.get('order_id')
        t_to = data.get('t_to')
        t_from = t_id
        order_data = await db_manager.get_order_data(order_id)

        if order_data.get('blocked') or not order_data:
            await bot.send_message(user_id,
                                   'Эта заявка больше недоступна!')
            return

        await User.get_partial_amount.set()
        await state.set_data({'order_id': order_id,
                              't_to': t_to,
                              't_from': t_from})
        await bot.send_message(user_id,
                               f'Введите сумму {order_data.get("currency_from")} которую хотите купить:',
                               reply_markup=markup.kb_cancel())


async def buy_order(user_id, order_id, t_to, t_from=None, amount=0.0, approved=1):  # Вызывает только клиент
    print(t_from)
    msg_id = await db_manager.buy_order(user_id, order_id, t_to, t_from, amount, approved)
    if approved:
        try:
            await bot.delete_message(config.order_channel, msg_id)
        except exceptions.MessageCantBeDeleted:
            await bot.edit_message_text('Удалена', config.order_channel, msg_id)
        except exceptions.MessageToDeleteNotFound:
            pass

    order_data = await db_manager.get_buy_order_data(order_id)
    if not approved:
        await bot.send_message(order_data.get('owner_id'),
                               f'Заявка №{order_id}\n\n'
                               f'Запрос на частичный выкуп {amount} {order_data.get("currency_from")}',
                               reply_markup=markup.partial_approve(order_id))
        await bot.send_message(user_id,
                               'Отлично! Запрос на частичный выкуп заявки был отправлен её владельцу!\n'
                               'Как только он примет решение - Вы получите уведомление',
                               reply_markup=markup.main())
        return

    if order_data.get('commission_payer') == 'customer':  # Опеределяет, что клиент == commission_payer
        admin_template_data = await utils.get_admin_template_data(
            await db_manager.get_active_admin_template(order_data.get("currency_to")))
        await bot.send_message(user_id,
                               f'Отлично!\n'
                               f'Сейчас Вы должны перевести {order_data.get("amount_to")} '
                               f'{order_data.get("currency_to")} по указанным ниже реквизитам:\n'
                               f'{admin_template_data}\n\n'
                               f'Назначение перевода: Заявка <b>{order_id}</b>\n\n'
                               f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                               f'Обязательно указывайте правильное назначение перевода.\n'
                               f'Заявки с неверным назначением перевода будут обработаны в последнюю очередь.\n\n'
                               f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                               f'После того, как вы совершите перевод, обязательно нажмите кнопку «Перевёл».',
                               reply_markup=markup.first_pay(order_id))
        await bot.send_message(order_data.get('owner_id'),
                               f'Заявка №{order_id}\n\n'
                               f'Мы нашли Вам покупателя!\n'
                               f'Как только он переведет нужную сумму гаранту - Вы будете оповещены!')
        return

    admin_template_data = await utils.get_admin_template_data(
        await db_manager.get_active_admin_template(order_data.get("currency_from")))
    await bot.send_message(user_id,
                           'Спасибо, информация принята! Пожалуйста, ожидайте готовность гаранта к обмену. '
                           'Мы вас моментально уведомим об этом.',
                           reply_markup=markup.cancel_buy_order(order_id))
    await bot.send_message(order_data.get('owner_id'),
                           f'Заявка №{order_id}\n\n'
                           f'Отлично!\n Мы нашли Вам партнера для обмена!\n\n'
                           f'Сейчас Вы должны перевести {order_data.get("amount_from")} '
                           f'{order_data.get("currency_from")} по указанным ниже реквизитам:\n'
                           f'{admin_template_data}\n\n'
                           f'Назначение перевода: Заявка <b>{order_id}</b>\n\n'
                           f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                           f'Обязательно указывайте правильное назначение перевода.\n'
                           f'Заявки с неверным назначением перевода будут обработаны в последнюю очередь.\n\n'
                           f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                           f'После того, как вы совершите перевод, обязательно нажмите кнопку «Перевёл».',
                           reply_markup=markup.first_pay(order_id))
    return


async def second_pay_buy_order(order_id):
    order_data = await db_manager.get_buy_order_data(order_id)
    commission_payer = order_data.get('commission_payer')
    if commission_payer == 'owner':
        await bot.send_message(order_data.get('customer_id'),
                               'Заявка №{}\n\n'
                               'Владелец заявки перевел сумму гаранту!\n'
                               'Сейчас Вы должны перевести '
                               '<b>{} {}</b> по указанным ниже ревизитам:\n'
                               '{}\n\n'
                               '⚠️ <b>ВНИМАНИЕ!</b>\n'
                               'После того, как вы совершите перевод, обязательно нажмите кнопку Перевёл'
                               .format(order_id, order_data.get('amount_to'), order_data.get('currency_to'),
                                       '\n\n'.join([await utils.get_template_text_for_order(t_id)
                                                    for t_id in order_data.get('template_to').split(',')])),
                               reply_markup=markup.second_pay(order_id))
        await bot.send_message(order_data.get('owner_id'),
                               f'Ваш перевод по заявке №{order_id} получен.\n'
                               f'Пожалуйста, ожидайте уведомление об отправке вам средств.')
    else:
        await bot.send_message(order_data.get('customer_id'),
                               f'Ваш перевод по заявке №{order_id} получен.\n'
                               f'Пожалуйста, ожидайте уведомление об отправке вам средств.')
        await bot.send_message(order_data.get('owner_id'),
                               'Заявка №{}\n\n'
                               'Покупатель перевел сумму гаранту!\n'
                               'Сейчас Вы должны перевести '
                               '<b>{} {}</b> по указанным ниже ревизитам:\n'
                               '{}\n\n'
                               '⚠️ <b>ВНИМАНИЕ!</b>\n'
                               'После того, как вы совершите перевод, обязательно нажмите кнопку Перевёл'
                               .format(order_id, order_data.get('amount_from'), order_data.get('currency_from'),
                                       '\n\n'.join([await utils.get_template_text_for_order(t_id)
                                                    for t_id in order_data.get('customer_template_to').split(',')])),
                               reply_markup=markup.second_pay(order_id))


# ==================================================================================================================
# ======================================== ADMIN INTERFACE =========================================================
# ==================================================================================================================
@dp.message_handler(lambda message: message.chat.id in config.admin_id,
                    commands=['admin'], state='*')
async def process_admin(message: Message, state: FSMContext):
    await state.finish()
    await Admin.main.set()
    await bot.send_message(message.chat.id,
                           'Админ-меню',
                           reply_markup=markup.admin())


@dp.message_handler(text='Все рефералы', state=Admin.main)
async def get_ref_stat(message: Message):
    ref_stat = await db_manager.get_all_ref_stat()
    if not ref_stat:
        await bot.send_message(message.chat.id,
                               'Еще ни у кого нет рефералов')
        return

    message_text = ''
    for user_data in ref_stat:
        print(user_data)
        message_text += f'<code>{user_data.get("user_id")}</code>' \
                        f'| {(await bot.get_chat(user_data.get("user_id"))).get_mention(as_html=True)} ' \
                        f'| {user_data.get("c")} ' \
                        f'| {user_data.get("income")} RUB\n'

    await bot.send_message(message.chat.id,
                           message_text,
                           reply_markup=markup.minus_referral_income())


@dp.callback_query_handler(text='minus-ref-income', state=Admin.main)
async def minus_ref_income(call: CallbackQuery):
    await call.answer()
    await Admin.get_user_to_minus_ref_income.set()
    await bot.send_message(call.message.chat.id,
                           'Отправьте ID пользователя, которому хотите снять баланс:',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=Admin.get_user_to_minus_ref_income)
async def get_user_to_minus_ref_income(message: Message, state: FSMContext):
    if not await db_manager.is_user(message.text):
        await bot.send_message(message.chat.id,
                               'Такого пользователя нет в системе')
        return

    await state.set_data({'user_id': message.text})
    await Admin.get_value_to_minus_ref_income.set()
    await bot.send_message(message.chat.id,
                           'Введите значение (через точку), на которое Вы хотите уменьшить реферальный баланс '
                           'пользователя')


@dp.message_handler(state=Admin.get_value_to_minus_ref_income)
async def get_value_to_minus_ref_income(message: Message, state: FSMContext):
    try:
        value = float(message.text)
        if value <= 0:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Значение должно быть числом, больше 0')
    else:
        data = await state.get_data()
        user_id = data.get('user_id')

        user_data = await db_manager.get_referral_stat(user_id)
        income = user_data.get('income')
        if value > income:
            await bot.send_message(message.chat.id,
                                   'Вы не можете снять больше, чем есть у пользователя')
            return

        await db_manager.minus_ref_income(user_id, value)
        await state.finish()
        await Admin.main.set()
        await bot.send_message(message.chat.id,
                               f'Реферальный баланс пользователя '
                               f'{(await bot.get_chat(user_id)).get_mention(as_html=True)} был изменен',
                               reply_markup=markup.admin())
        await get_ref_stat(message)


@dp.message_handler(text='Статистика проекта', state=Admin.main)
async def get_project_stat(message: Message):
    closed_orders, today_data, total_data = await db_manager.get_orders_stat()
    message_text = f'Всего обменов завершено: {closed_orders}\n\n'
    if today_data:
        message_text += f'Обмены за сегодня:\n\n'
        today_commissions = {}
        for e_order in today_data:
            message_text += ('{} {} {} ↔️ {} {} {}\n'
                             .format((await bot.get_chat(e_order.get('owner_id'))).get_mention(as_html=True),
                                     e_order.get('amount_from'), e_order.get('currency_from'),
                                     e_order.get('currency_to'), e_order.get('amount_to'),
                                     (await bot.get_chat(e_order.get('customer_id'))).get_mention(as_html=True)))
            if e_order.get('commission_payer') == 'owner':
                if not today_commissions.get(e_order.get('currency_from')):
                    today_commissions[e_order.get('currency_from')] = float(e_order.get('amount_from')) \
                                                                      - float(e_order.get('amount'))
                else:
                    today_commissions[e_order.get('currency_from')] += float(e_order.get('amount_from')) \
                                                                       - float(e_order.get('amount'))

        message_text += '\nЗаработано за <b>сегодня</b> за {} обменов:\n{}\n' \
                        '<i>из которых {} RUB реферальные бонусы</i>'\
            .format(len(today_data),
                    ', '.join([f'{value:.2f} {config.all_template_types[cur]["sign"]}'
                               for cur, value in today_commissions.items()]),
                    sum([e_order.get('ref_value') for e_order in today_data]))

        total_commissions = {}
        for e_order in total_data:
            if e_order.get('commission_payer') == 'owner':
                if not total_commissions.get(e_order.get('currency_from')):
                    total_commissions[e_order.get('currency_from')] = float(e_order.get('amount_from')) \
                                                                      - float(e_order.get('amount'))
                else:
                    total_commissions[e_order.get('currency_from')] += float(e_order.get('amount_from')) \
                                                                       - float(e_order.get('amount'))
        message_text += '\n\nЗаработано за <b>все время</b> за {} обменов:\n{}\n' \
                        '<i>из которых {} RUB реферальные бонусы</i>'\
            .format(len(total_data),
                    ', '.join([f'{value:.2f} {config.all_template_types[cur]["sign"]}'
                               for cur, value in total_commissions.items()]),
                    sum([e_order.get('ref_value') for e_order in total_data]))
    else:
        message_text += 'Обменов за сегодня нет'

    await bot.send_message(message.chat.id,
                           message_text)


@dp.message_handler(text='Заявки на одобрении', state=Admin.main)
async def admin_orders_on_approval(message: Message):
    orders = await db_manager.get_orders_on_approve()
    if not orders:
        await bot.send_message(message.chat.id,
                               'Заявок на одобрении нет')
        return

    for order_data in orders:
        order_id = order_data.get('id')
        await bot.send_message(message.chat.id,
                               await utils.get_order_text(order_id, 'admin_approve', bot),
                               reply_markup=markup.approve_new_order(order_id))


@dp.callback_query_handler(lambda call: 'new-order-approve_' in call.data,
                           state='*')
async def approve_new_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if not order_data or order_data.get('approved') == 1:
        await call.answer()
        await call.message.delete()
        return

    await call.answer('Заявка была одобрена', show_alert=True)
    await call.message.edit_reply_markup(None)
    await db_manager.approve_new_order(order_id)
    await bot.send_message(order_data.get('user_id'),
                           f'Ваша заявка №{order_id} была одобрена!')
    msg_id = (await bot.send_message(config.order_channel,
                                     await utils.get_order_text(order_id, who='customer'),
                                     reply_markup=markup.buy_order_from_channel(order_id))).message_id
    await db_manager.set_order_msg_id(order_id, msg_id)


@dp.callback_query_handler(lambda call: 'new-order-decline_' in call.data,
                           state='*')
async def decline_new_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if not order_data or order_data.get('approved') == 1:
        await call.answer()
        await call.message.delete()
        return

    await call.answer('Заявка была отклонена', show_alert=True)
    await call.message.delete()
    await db_manager.delete_order(order_id)
    await bot.send_message(order_data.get('user_id'),
                           f'Ваша заявка №{order_id} была отклонена и удалена из системы!')


# =============================== Подвтердить first_pay ===========================================================
@dp.callback_query_handler(lambda call: 'approve-first-pay_' in call.data,
                           state='*')
async def admin_approve_first_pay(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(markup.admin_first_pay_approve(call.data.split('_')[-1], True))


@dp.callback_query_handler(lambda call: 'approve-first-pay-a_' in call.data,
                           state='*')
async def admin_accept_approve_first_pay(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    await call.message.edit_reply_markup(None)

    if not order_data or order_data.get('stage') != 'first_approve':
        await call.answer()
        return

    await call.answer('Сообщение о подтверждении отправлено клиенту!', show_alert=True)
    await db_manager.first_pay_approved(order_id)
    await second_pay_buy_order(order_id)


@dp.callback_query_handler(lambda call: 'approve-first-pay-d_' in call.data,
                           state='*')
async def admin_cancel_approve_first_pay(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(markup.admin_first_pay_approve(call.data.split('_')[-1]))


# ============================= Заявка завершена =================================================================
@dp.callback_query_handler(lambda call: 'set-order-done_' in call.data,
                           state='*')
async def set_buy_order_done(call: CallbackQuery):
    await call.answer('Заявка закрыта, рейтинг будет начислен обоим участникам обмена', show_alert=True)
    order_id = call.data.split('_')[-1]
    await call.message.edit_reply_markup(None)
    await db_manager.set_buy_order_done(order_id)
    order_data = await db_manager.get_buy_order_data(order_id)
    await bot.send_message(order_data.get('owner_id'),
                           f'Заявка №{order_id} была завершена!\n'
                           f'Вам было начислено +1 рейтинг')
    await bot.send_message(order_data.get('customer_id'),
                           f'Заявка №{order_id} была завершена!\n'
                           f'Вам было начислено +1 рейтинг')

    commission_payer = order_data.get('commission_payer')
    if commission_payer == 'owner':
        commission = float(order_data.get('amount_from')) - float(order_data.get('amount'))
        currency = order_data.get('currency_from')
    else:
        commission = float(order_data.get('amount_to')) - float(order_data.get('converted_amount'))
        currency = order_data.get('currency_to')

    ref_bonus = commission * .1
    exchange_rate = await db_manager.get_exchange_rate(currency)
    ref_bonus = config.convert[(currency, 'RUB')]['convert'](ref_bonus, exchange_rate)
    print('Комиссия:', commission,
          '\nБонус реферала в RUB:', ref_bonus,
          '\nКурс:', exchange_rate)

    for user_id in [order_data.get('owner_id'), order_data.get('customer_id')]:
        ref_father = await db_manager.get_ref_father(user_id)
        if ref_father:
            try:
                await bot.send_message(ref_father,
                                       f'Ваш реферальный счет пополнен на {ref_bonus} RUB '
                                       f'за обмен Вашего друга')
            except exceptions.BotBlocked:
                pass
            else:
                await db_manager.add_ref_bonus(order_id, ref_father, user_id, ref_bonus)


# ====================================Активные обмены===============================================================
@dp.message_handler(text='Активные обмены', state=Admin.main)
async def active_orders_admin(message: Message):
    orders = await db_manager.admin_get_all_orders()
    if not orders:
        await bot.send_message(message.chat.id,
                               'Активных обменов нет')
        return

    for order_data in orders:
        order_id = order_data.get('id')
        text, m = await utils.get_admin_active_order(order_id, bot)
        await bot.send_message(message.chat.id,
                               text,
                               reply_markup=m)


# ================================Счета============================================================================
@dp.message_handler(text='Счета', state=Admin.main)
async def admin_templates(message: Message):
    await bot.send_message(message.chat.id,
                           'Выберите валюту',
                           reply_markup=markup.admin_templates())


@dp.callback_query_handler(text='back-to-admin-currencies', state=Admin.main)
async def back_to_admin_templates(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text('Выберите валюту',
                                 reply_markup=markup.admin_templates())


@dp.callback_query_handler(lambda call: 'back-to-admin-templates_' in call.data,
                           state=Admin.main)
async def back_to_admin_templates(call: CallbackQuery):
    cur = call.data.split('_')[-1]
    await call.answer()
    templates = await db_manager.get_admin_templates(cur)
    await call.message.edit_text('Выберите шаблон\n'
                                 '✅ отмечен активный шаблон',
                                 reply_markup=markup.admin_templates_by_cur(templates, cur))


@dp.callback_query_handler(lambda call: 'get-admin-templates_' in call.data,
                           state=Admin.main)
async def get_admin_templates(call: CallbackQuery):
    cur = call.data.split('_')[-1]
    await call.answer()
    templates = await db_manager.get_admin_templates(cur)
    await call.message.edit_text('Выберите шаблон\n'
                                 '✅ отмечен активный шаблон',
                                 reply_markup=markup.admin_templates_by_cur(templates, cur))


@dp.callback_query_handler(lambda call: 'show-admin-template_' in call.data,
                           state=Admin.main)
async def show_admin_template(call: CallbackQuery):
    template_id = call.data.split('_')[-1]
    await call.answer()
    template = await db_manager.get_admin_template(template_id)
    await call.message.edit_text(f'Шаблон <b>{template.get("currency")}</b>\n'
                                 f'{"✅ Активный" if template.get("active") else ""}\n' +
                                 await utils.get_admin_template_data(template_id),
                                 reply_markup=markup.admin_template_menu(template))


@dp.callback_query_handler(lambda call: 'delete-admin-template_' in call.data,
                           state=Admin.main)
async def delete_admin_template(call: CallbackQuery):
    t_id = call.data.split('_')[-1]
    template = await db_manager.get_admin_template(t_id)
    await call.answer('Внимание! Все данные шаблона будут удалены', show_alert=True)
    await call.message.edit_reply_markup(reply_markup=markup.admin_template_menu(template, delete=True))


@dp.callback_query_handler(lambda call: 'delete-cancel-admin-template_' in call.data,
                           state=Admin.main)
async def cancel_delete_admin_template(call: CallbackQuery):
    t_id = call.data.split('_')[-1]
    template = await db_manager.get_admin_template(t_id)
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=markup.admin_template_menu(template))


@dp.callback_query_handler(lambda call: 'make-active-admin-template_' in call.data,
                           state=Admin.main)
async def activate_admin_template(call: CallbackQuery):
    await call.answer()
    t_id, currency = call.data.split('_')[1:]
    await db_manager.set_active_template(t_id, currency)
    template = await db_manager.get_admin_template(t_id)
    await call.message.edit_text(f'Шаблон <b>{template.get("currency")}</b>\n'
                                 f'{"✅ Активный" if template.get("active") else ""}\n' +
                                 await utils.get_admin_template_data(t_id),
                                 reply_markup=markup.admin_template_menu(template))


@dp.callback_query_handler(lambda call: 'add-new-admin-template_' in call.data,
                           state=Admin.main)
async def new_admin_template(call: CallbackQuery, state: FSMContext):
    await call.answer()
    cur = call.data.split('_')[-1]
    await call.message.delete()
    await state.set_data({'cur': cur})

    if cur == 'VISTA EUR':
        await NewAdminTemplate.VistaEUR.acc_number.set()
        await bot.send_message(call.message.chat.id,
                               'Введите номер Вашего счета VISTA EUR:',
                               reply_markup=markup.kb_cancel())
    elif cur == 'VISTA USD':
        await NewAdminTemplate.VistaUSD.acc_number.set()
        await bot.send_message(call.message.chat.id,
                               'Введите номер Вашего счета VISTA USD:',
                               reply_markup=markup.kb_cancel())
    elif cur == 'THB':
        await NewAdminTemplate.THB.bank.set()
        await bot.send_message(call.message.chat.id,
                               'Введите название банка:',
                               reply_markup=markup.kb_cancel())


@dp.message_handler(text='Отменить', state=NewAdminTemplate)
async def cancel_new_admin_template(message: Message, state: FSMContext):
    await state.finish()
    await Admin.main.set()
    await bot.send_message(message.chat.id,
                           'Действие отменено',
                           reply_markup=markup.admin())


# =================== Создание    Админ     Шаблона         VISTA EUR =====================
@dp.message_handler(state=NewAdminTemplate.VistaEUR.acc_number)
async def get_vista_eur_acc_number(message: Message, state: FSMContext):
    await state.update_data({'number': message.text})
    await NewAdminTemplate.VistaEUR.phone_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер телефона, который привязан к Вашему счету:')


@dp.message_handler(state=NewAdminTemplate.VistaEUR.phone_number)
async def get_vista_eur_phone_number(message: Message, state: FSMContext):
    data = await state.get_data()
    data.update({'phone': message.text})
    t_id = await db_manager.new_admin_template(data)
    await state.finish()
    await Admin.main.set()
    await bot.send_message(message.chat.id,
                           'Шаблон сохранен!',
                           reply_markup=markup.admin())
    await bot.send_message(message.chat.id,
                           f'Шаблон <b>{data.get("cur")}</b>\n\n' +
                           await utils.get_admin_template_data(t_id),
                           reply_markup=markup.admin_template_menu(await db_manager.get_admin_template(t_id)))


# =================== Создание     Админ    Шаблона         VISTA USD =====================
@dp.message_handler(state=NewAdminTemplate.VistaUSD.acc_number)
async def get_vista_usd_acc_number(message: Message, state: FSMContext):
    await state.update_data({'number': message.text})
    await NewAdminTemplate.VistaUSD.phone_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер телефона, который привязан к Вашему счету:')


@dp.message_handler(state=NewAdminTemplate.VistaUSD.phone_number)
async def get_vista_usd_phone_number(message: Message, state: FSMContext):
    data = await state.get_data()
    data.update({'phone': message.text})
    t_id = await db_manager.new_admin_template(data)
    await state.finish()
    await Admin.main.set()
    await bot.send_message(message.chat.id,
                           'Шаблон сохранен!',
                           reply_markup=markup.admin())
    await bot.send_message(message.chat.id,
                           f'Шаблон <b>{data.get("cur")}</b>\n\n' +
                           await utils.get_admin_template_data(t_id),
                           reply_markup=markup.admin_template_menu(await db_manager.get_admin_template(t_id)))


# =================== Создание   Админ      Шаблона         THB =====================
@dp.message_handler(state=NewAdminTemplate.THB.bank)
async def get_thb_bank_name(message: Message, state: FSMContext):
    await state.update_data({'bank': message.text})
    await NewAdminTemplate.THB.acc_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер счета без пробелов и дефисов: 5571236543 (10 цифр)')


@dp.message_handler(state=NewAdminTemplate.THB.acc_number)
async def get_thb_acc_number(message: Message, state: FSMContext):
    try:
        int(message.text)
        if len(message.text) != 10:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Неверный формат!\n'
                               'Пожалуйста, введите номер счета длинной 10 цифр без пробелов и дефисов!')
    else:
        await state.update_data({'number': message.text})
        await NewAdminTemplate.THB.holder_name.set()
        await bot.send_message(message.chat.id,
                               'Введите фамилию и имя держателя счета латиницей: Ivanov Ivan')


@dp.message_handler(state=NewAdminTemplate.THB.holder_name)
async def get_thb_holder_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data.update({'holder_name': message.text})
    t_id = await db_manager.new_admin_template(data)
    await state.finish()
    await Admin.main.set()
    await bot.send_message(message.chat.id,
                           'Шаблон сохранен!',
                           reply_markup=markup.admin())
    await bot.send_message(message.chat.id,
                           f'Шаблон <b>{data.get("cur")}</b>\n\n' +
                           await utils.get_admin_template_data(t_id),
                           reply_markup=markup.admin_template_menu(await db_manager.get_admin_template(t_id)))


# ==================================== Админ настройки ============================================================
@dp.message_handler(text='Настройки', state=Admin.main)
async def admin_settings(message: Message):
    settings = await db_manager.get_settings()
    await bot.send_message(message.chat.id,
                           f'Комиссия сервиса: {settings.get("commission")}%\n'
                           f'Модерация заявок: {"✅ Активна" if settings.get("moderate") else "💤 Отключена"}',
                           reply_markup=markup.settings(settings.get('moderate')))


@dp.callback_query_handler(text='switch-moderate', state='*')
async def switch_admin_moderate(call: CallbackQuery):
    await call.answer()
    await db_manager.switch_moderate()
    settings = await db_manager.get_settings()
    await call.message.edit_text(f'Комиссия сервиса: {settings.get("commission")}%\n'
                                 f'Модерация заявок: {"✅ Активна" if settings.get("moderate") else "💤 Отключена"}',
                                 reply_markup=markup.settings(settings.get('moderate')))


@dp.callback_query_handler(text='edit-commission', state=Admin.main)
async def edit_commission(call: CallbackQuery):
    await call.answer()
    await Admin.get_new_commission.set()
    await call.message.delete()
    await bot.send_message(call.message.chat.id,
                           'Введите новое значение комиссии в %',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=Admin.get_new_commission)
async def get_new_commission(message: Message):
    if message.text == 'Отменить':
        await Admin.main.set()
        await bot.send_message(message.chat.id,
                               'Изменения отменены',
                               reply_markup=markup.admin())
        await admin_settings(message)
        return

    try:
        commission = float(message.text)
        if commission < 0:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Комиссия должна быть числом больше 0')
    else:
        await db_manager.set_commission(commission)
        await Admin.main.set()
        await bot.send_message(message.chat.id,
                               'Комиссия изменена',
                               reply_markup=markup.admin())
        await admin_settings(message)


# ==================================================================================================================
# ======================================== USER INTERFACE ==========================================================
# ==================================================================================================================
@dp.message_handler(commands=['start'], state='*')
async def process_start(message: Message, state: FSMContext):
    await state.finish()
    message_data = message.get_args()

    if not await db_manager.is_user(message.chat.id):
        await db_manager.create_user(message.chat.id)
        if await db_manager.is_user(message_data):
            await db_manager.set_ref(message_data, message.chat.id)

    order_id = 0
    if message_data and 'buyorder_' in message_data:
        order_id = message_data.split('_')[-1]
        if await db_manager.check_can_buy_order(order_id):
            await state.update_data({'order_id': order_id})

    if not await db_manager.is_registered(message.chat.id):
        await Registration.fio.set()
        await bot.send_message(message.chat.id,
                               'Пожалуйста, введите ваше ФИО')
        return

    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Добро пожаловать',
                           reply_markup=markup.main())
    if order_id:
        order_data = await db_manager.get_order_data(order_id)
        if order_data.get('user_id') == message.chat.id:
            return

        await bot.send_message(message.chat.id,
                               await utils.get_order_text(order_id, 'customer'),
                               reply_markup=markup.buy_order(order_id, partial=order_data.get('partial')))


@dp.message_handler(state=Registration.fio)
async def registration_get_name(message: Message, state: FSMContext):
    await state.set_data({'fio': message.text})
    await Registration.phone.set()
    await bot.send_message(message.chat.id,
                           'Пожалуйста, отправьте Ваш номер телефона')


@dp.message_handler(state=Registration.phone)
async def registration_get_phone(message: Message, state: FSMContext):
    await state.update_data({'phone': message.text})
    await Registration.email.set()
    await bot.send_message(message.chat.id,
                           'Пожалуйста, отправьте Ваш email адрес')


@dp.message_handler(state=Registration.email)
async def registration_get_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    fio = data.get('fio')
    phone = data.get('phone')
    order_id = data.get('order_id')
    await state.finish()
    await db_manager.register_user(message.chat.id, fio, phone, message.text)
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Вы успешно прошли регистрацию!',
                           reply_markup=markup.main())
    if order_id:
        if await db_manager.check_can_buy_order(order_id):
            order_data = await db_manager.get_order_data(order_id)
            if order_data.get('user_id') == message.chat.id:
                return

            await bot.send_message(message.chat.id,
                                   await utils.get_order_text(order_id, 'customer'),
                                   reply_markup=markup.buy_order(order_id, order_data.get('partial')))


# =========================== ОСНОВНАЯ ЧАСТЬ =========================================
# ============================== Шаблоны =============================================
@dp.message_handler(text='Мои шаблоны', state=User.main)
async def my_templates(message: Message):
    templates = await db_manager.get_all_templates(message.chat.id)
    if not templates:
        text = 'У Вас еще нет ни одного шаблона'
    else:
        text = 'Ваши шаблоны счетов:'

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=markup.my_templates(templates))


@dp.callback_query_handler(lambda call: 'template-info_' in call.data,
                           state=User.main)
async def get_user_template_info(call: CallbackQuery):
    template_id = call.data.split('_')[-1]
    await call.answer()
    template_data = await db_manager.get_template_data(template_id)
    if not template_data:
        templates = await db_manager.get_all_templates(call.message.chat.id)
        if not templates:
            text = 'У Вас еще нет ни одного шаблона'
        else:
            text = 'Ваши шаблоны счетов:'
        await call.message.edit_text(text,
                                     reply_markup=markup.my_templates(templates))
        return

    await call.message.edit_text(await utils.get_template_text(template_id),
                                 reply_markup=markup.template_markup(template_id))


@dp.callback_query_handler(text='back-to-templates', state=User.main)
async def back_to_templates(call: CallbackQuery):
    await call.answer()
    templates = await db_manager.get_all_templates(call.message.chat.id)
    if not templates:
        text = 'У Вас еще нет ни одного шаблона'
    else:
        text = 'Ваши шаблоны счетов:'
    await call.message.edit_text(text,
                                 reply_markup=markup.my_templates(templates))


@dp.callback_query_handler(lambda call: 'delete-template_' in call.data,
                           state=User.main)
async def delete_template(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=markup.template_markup(call.data.split('_')[-1], delete=True))


@dp.callback_query_handler(lambda call: 'delete-template-decline_' in call.data,
                           state=User.main)
async def delete_template_decline(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=markup.template_markup(call.data.split('_')[-1]))


@dp.callback_query_handler(lambda call: 'delete-template-accept_' in call.data,
                           state=User.main)
async def delete_template_accept(call: CallbackQuery):
    await call.answer('Шаблон удален', show_alert=True)
    await db_manager.delete_template(call.data.split('_')[-1])
    templates = await db_manager.get_all_templates(call.message.chat.id)
    if not templates:
        text = 'У Вас еще нет ни одного шаблона'
    else:
        text = 'Ваши шаблоны счетов:'
    await call.message.edit_text(text,
                                 reply_markup=markup.my_templates(templates))


# ====================================== Создание нового шаблона =======================================
@dp.callback_query_handler(text='add-new-template', state=User.main)
async def add_new_template(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text('Выбери, шаблон какой валюты ты хочешь создать',
                                 reply_markup=markup.new_template_type())


@dp.callback_query_handler(lambda call: 'new-template-type_' in call.data,
                           state=User.main)
async def new_template_type(call: CallbackQuery, state: FSMContext):
    t_type = call.data.split('_')[-1]
    await call.answer()
    await call.message.delete()
    await state.set_data({'t_type': t_type})
    await NewTemplate.name.set()
    await bot.send_message(call.message.chat.id,
                           'Введите название шаблона (будет отображаться при выборе счета):',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=NewTemplate.name)
async def get_new_template_name(message: Message, state: FSMContext):
    data = await state.get_data()
    t_type = data.get('t_type')
    await state.update_data({'name': message.text})
    if t_type == 'VISTA EUR':
        await NewTemplate.VistaEUR.acc_number.set()
        await bot.send_message(message.chat.id,
                               'Введите номер Вашего счета VISTA EUR:')
    elif t_type == 'VISTA USD':
        await NewTemplate.VistaUSD.acc_number.set()
        await bot.send_message(message.chat.id,
                               'Введите номер Вашего счета VISTA USD:')
    elif t_type == 'RUB':
        await NewTemplate.RUB.bank.set()
        await bot.send_message(message.chat.id,
                               'Выберите Банк или введите его название вручную:',
                               reply_markup=markup.bank_name_markup())
    elif t_type == 'BYN':
        await NewTemplate.BYN.bank.set()
        await bot.send_message(message.chat.id,
                               'Введите название банка:')
    elif t_type == 'THB':
        await NewTemplate.THB.bank.set()
        await bot.send_message(message.chat.id,
                               'Введите название банка:')


# =================== Создание         Шаблона         VISTA EUR =====================
@dp.message_handler(state=NewTemplate.VistaEUR.acc_number)
async def get_vista_eur_acc_number(message: Message, state: FSMContext):
    await state.update_data({'acc_number': message.text})
    # TODO: валидация счета виста еур
    await NewTemplate.VistaEUR.phone_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер телефона, который привязан к Вашему счету:')


@dp.message_handler(state=NewTemplate.VistaEUR.phone_number)
async def get_vista_eur_phone_number(message: Message, state: FSMContext):
    data = await state.get_data()
    t_type = data.get('t_type')
    name = data.get('name')
    acc_number = data.get('acc_number')
    phone = message.text
    t_id = await db_manager.new_template(message.chat.id, t_type, name, number=acc_number, phone=phone)
    await create_new_template(message.chat.id, state, t_id)


# =================== Создание         Шаблона         VISTA USD =====================
@dp.message_handler(state=NewTemplate.VistaUSD.acc_number)
async def get_vista_usd_acc_number(message: Message, state: FSMContext):
    await state.update_data({'acc_number': message.text})
    # TODO: валидация счета виста еур
    await NewTemplate.VistaUSD.phone_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер телефона, который привязан к Вашему счету:')


@dp.message_handler(state=NewTemplate.VistaUSD.phone_number)
async def get_vista_usd_phone_number(message: Message, state: FSMContext):
    data = await state.get_data()
    t_type = data.get('t_type')
    name = data.get('name')
    acc_number = data.get('acc_number')
    phone = message.text
    t_id = await db_manager.new_template(message.chat.id, t_type, name, number=acc_number, phone=phone)
    await create_new_template(message.chat.id, state, t_id)


# =================== Создание         Шаблона         RUB =====================
@dp.message_handler(state=NewTemplate.RUB.bank)
async def get_rub_bank_name(message: Message, state: FSMContext):
    await state.update_data({'bank': message.text})
    await NewTemplate.RUB.region.set()
    await bot.send_message(message.chat.id,
                           'Введите название региона или города, в котором '
                           'получена карта (например, Московская область или Казань):',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=NewTemplate.RUB.region)
async def get_rub_region(message: Message, state: FSMContext):
    await state.update_data({'region': message.text})
    await NewTemplate.RUB.holder_name.set()
    await bot.send_message(message.chat.id,
                           'Введите полностью фамилию, имя и отчество человека, '
                           'на которого оформлена карта (русскими буквами):')


@dp.message_handler(state=NewTemplate.RUB.holder_name)
async def get_rub_holder_name(message: Message, state: FSMContext):
    await state.update_data({'holder_name': message.text})
    await NewTemplate.RUB.card_type.set()
    await bot.send_message(message.chat.id,
                           'Выберите тип карты из списка или введите вручную:',
                           reply_markup=markup.card_type_markup())


@dp.message_handler(state=NewTemplate.RUB.card_type)
async def get_rub_card_type(message: Message, state: FSMContext):
    await state.update_data({'card_type': message.text})
    await NewTemplate.RUB.card_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер вашей карты:',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=NewTemplate.RUB.card_number)
async def get_rub_card_number(message: Message, state: FSMContext):
    if not verify(message.text):
        await bot.send_message(message.chat.id,
                               'Пожалуйста, введите валидный номер карты')
        return

    data = await state.get_data()
    t_type = data.get('t_type')
    name = data.get('name')
    bank = data.get('bank')
    region = data.get('region')
    holder_name = data.get('holder_name')
    card_type = data.get('card_type')
    card_number = message.text
    t_id = await db_manager.new_template(message.chat.id, t_type, name, bank=bank,
                                         region=region, holder_name=holder_name,
                                         card_type=card_type, number=card_number)
    await create_new_template(message.chat.id, state, t_id)


# =================== Создание         Шаблона         BYN =====================
@dp.message_handler(state=NewTemplate.BYN.bank)
async def get_byn_bank_name(message: Message, state: FSMContext):
    await state.update_data({'bank': message.text})
    await NewTemplate.BYN.region.set()
    await bot.send_message(message.chat.id,
                           'Введите название региона или города, в котором '
                           'получена карта (например, Московская область или Казань):',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=NewTemplate.BYN.region)
async def get_byn_region(message: Message, state: FSMContext):
    await state.update_data({'region': message.text})
    await NewTemplate.BYN.holder_name.set()
    await bot.send_message(message.chat.id,
                           'Введите полностью фамилию, имя и отчество человека, '
                           'на которого оформлена карта (русскими буквами):')


@dp.message_handler(state=NewTemplate.BYN.holder_name)
async def get_byn_holder_name(message: Message, state: FSMContext):
    await state.update_data({'holder_name': message.text})
    await NewTemplate.BYN.card_type.set()
    await bot.send_message(message.chat.id,
                           'Выберите тип карты из списка или введите вручную:',
                           reply_markup=markup.card_type_markup())


@dp.message_handler(state=NewTemplate.BYN.card_type)
async def get_byn_card_type(message: Message, state: FSMContext):
    await state.update_data({'card_type': message.text})
    await NewTemplate.BYN.card_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер вашей карты:',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=NewTemplate.BYN.card_number)
async def get_byn_card_number(message: Message, state: FSMContext):
    if not verify(message.text):
        await bot.send_message(message.chat.id,
                               'Пожалуйста, введите валидный номер карты')
        return

    data = await state.get_data()
    t_type = data.get('t_type')
    name = data.get('name')
    bank = data.get('bank')
    region = data.get('region')
    holder_name = data.get('holder_name')
    card_type = data.get('card_type')
    card_number = message.text
    t_id = await db_manager.new_template(message.chat.id, t_type, name, bank=bank,
                                         region=region, holder_name=holder_name,
                                         card_type=card_type, number=card_number)
    await create_new_template(message.chat.id, state, t_id)


# =================== Создание         Шаблона         THB =====================
@dp.message_handler(state=NewTemplate.THB.bank)
async def get_thb_bank_name(message: Message, state: FSMContext):
    await state.update_data({'bank': message.text})
    await NewTemplate.THB.acc_number.set()
    await bot.send_message(message.chat.id,
                           'Введите номер счета без пробелов и дефисов: 5571236543 (10 цифр)')


@dp.message_handler(state=NewTemplate.THB.acc_number)
async def get_thb_acc_number(message: Message, state: FSMContext):
    try:
        int(message.text)
        if len(message.text) != 10:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Неверный формат!\n'
                               'Пожалуйста, введите номер счета длинной 10 цифр без пробелов и дефисов!')
    else:
        await state.update_data({'acc_number': message.text})
        await NewTemplate.THB.holder_name.set()
        await bot.send_message(message.chat.id,
                               'Введите фамилию и имя держателя счета латиницей: Ivanov Ivan')


@dp.message_handler(state=NewTemplate.THB.holder_name)
async def get_thb_holder_name(message: Message, state: FSMContext):
    data = await state.get_data()
    t_type = data.get('t_type')
    name = data.get('name')
    bank = data.get('bank')
    acc_number = data.get('acc_number')
    holder_name = message.text
    t_id = await db_manager.new_template(message.chat.id, t_type, name, bank=bank,
                                         number=acc_number, holder_name=holder_name)
    await create_new_template(message.chat.id, state, t_id)
# =============================== Шаблоны END =======================================


# =============================== Создание заявки ===================================
@dp.message_handler(text='Создать заявку', state=User.main)
async def process_create_new_order(message: Message):
    await bot.send_message(message.chat.id,
                           'Выберите валюту, которую хотите отдать',
                           reply_markup=markup.order_currency_from())


@dp.message_handler(text='Отменить', state=NewOrder)
async def cancel_new_order(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get('msg_id')
    if msg_id:
        try:
            await bot.edit_message_reply_markup(message.chat.id,
                                                msg_id,
                                                reply_markup=None)
        except:
            pass

    await state.finish()
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Создание заявки отменено',
                           reply_markup=markup.main())


@dp.callback_query_handler(lambda call: 'order-currency-from_' in call.data,
                           state=User.main)
async def order_currency_from(call: CallbackQuery, state: FSMContext):
    await call.answer()
    currency_from = call.data.split('_')[-1]
    await state.update_data({'currency_from': currency_from})
    await call.message.delete()
    await NewOrder.change_amount.set()
    await bot.send_message(call.message.chat.id,
                           'Введите сумму, которую хотите отдать:',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=NewOrder.change_amount)
async def new_order_change_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Сумма обмена должна быть числом больше 0')
    else:
        currency_from = (await state.get_data()).get('currency_from')
        await NewOrder.currency_to.set()
        msg_id = (await bot.send_message(message.chat.id,
                                         'Выберите валюту, которую хотите получить:',
                                         reply_markup=markup.order_currency_to(currency_from))).message_id
        await state.update_data({'amount': amount,
                                 'msg_id': msg_id})


@dp.callback_query_handler(lambda call: 'order-currency-to_' in call.data,
                           state=NewOrder.currency_to)
async def new_order_currency_to(call: CallbackQuery, state: FSMContext):
    await call.answer()
    currency_to = call.data.split('_')[-1]
    await call.message.delete()
    data = await state.get_data()
    currency_from = data.get('currency_from')
    await NewOrder.exchange_rate.set()
    if currency_from == 'RUB':
        rate = await db_manager.get_exchange_rate(currency_to)
    elif currency_to == 'RUB':
        rate = await db_manager.get_exchange_rate(currency_from)
    else:
        rate = 0

    msg_id = (await bot.send_message(call.message.chat.id,
                                     'Введите курс, по которому хотите обменять:{}'
                                     .format(f'\nКурс ЦБРФ: {rate:.2f}' if rate else ''),
                                     reply_markup=markup.cb_rf(rate))).message_id
    await state.update_data({'currency_to': currency_to,
                             'msg_id': msg_id if rate else None})


@dp.callback_query_handler(text='set-cb-rf',
                           state=NewOrder.exchange_rate)
async def new_order_exchange_rate_cb(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    currency_from = data.get('currency_from')
    currency_to = data.get('currency_to')
    if currency_from == 'RUB':
        rate = await db_manager.get_exchange_rate(currency_to)
    else:
        rate = await db_manager.get_exchange_rate(currency_from)
    await state.update_data({'exchange_rate': rate})
    await NewOrder.partial_exchange.set()
    await call.message.edit_text('Разрешить частичный выкуп Вашей заявки?',
                                 reply_markup=markup.allow_partial_exchange())


@dp.message_handler(state=NewOrder.exchange_rate)
async def new_order_exchange_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))
        if rate <= 0:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Курс обмена должен быть числом больше 0')
    else:
        data = await state.get_data()
        msg_id = data.get('msg_id')
        if msg_id:
            await bot.edit_message_reply_markup(message.chat.id,
                                                msg_id,
                                                reply_markup=None)

        await NewOrder.partial_exchange.set()
        msg_id = (await bot.send_message(message.chat.id,
                                         'Разрешить частичный выкуп Вашей заявки?',
                                         reply_markup=markup.allow_partial_exchange())).message_id
        await state.update_data({'exchange_rate': rate,
                                 'msg_id': msg_id})


@dp.callback_query_handler(lambda call: 'partial-exchange_' in call.data,
                           state=NewOrder.partial_exchange)
async def new_order_partial_exchange(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    currency_from = data.get('currency_from')
    currency_to = data.get('currency_to')
    amount = float(data.get('amount'))
    exchange_rate = float(data.get('exchange_rate'))

    commission = await db_manager.get_commission()
    convert_rule = config.convert[(currency_from, currency_to)]
    converted_amount = config.convert[(currency_from, currency_to)]['convert'](amount, exchange_rate)

    if currency_from == convert_rule['commission']:
        amount_from = round(amount * (1 + commission * 2 / 100), 2)
        amount_to = round(converted_amount * (1 + commission / 100), 2)
        message_text = (f'Отдадите (с учетом комиссии сервиса): {amount_from} {currency_from}\n'
                        f'Получите: {amount_to} {currency_to}\n\n'
                        f'Выберите шаблон {currency_from}, с которого будете отправлять средства:')
        await state.update_data({'commission_payer': 'owner'})
    else:
        amount_from = round(amount * (1 + commission / 100), 2)
        amount_to = round(converted_amount * (1 + commission * 2 / 100), 2)
        message_text = (f'Отдадите (с учетом комиссии сервиса): {amount_from} {currency_from}\n'
                        f'Получите: {converted_amount} {currency_to}\n\n'
                        f'Выберите шаблон {currency_from}, с которого будете отправлять средства:')
        await state.update_data({'commission_payer': 'customer'})

    await state.update_data({'partial': call.data.split('_')[-1],
                             'amount_to': amount_to,
                             'amount_from': amount_from,
                             'converted_amount': converted_amount})
    await call.message.delete()
    await NewOrder.template_from.set()
    templates = await db_manager.get_templates_for_type(call.message.chat.id, currency_from)
    msg_id = (await bot.send_message(call.message.chat.id,
                                     message_text,
                                     reply_markup=markup.select_template_from(templates, currency_from))).message_id
    await state.update_data({'msg_id': msg_id})


@dp.callback_query_handler(lambda call: 'new-order-template_' in call.data,
                           state=NewOrder.template_from)
async def select_template_for_new_order(call: CallbackQuery, state: FSMContext):
    temp_id = call.data.split('_')[-1]
    await call.answer()
    currency_to = (await state.get_data()).get('currency_to')
    await state.update_data({'template_from': temp_id})
    await NewOrder.template_to.set()
    templates = await db_manager.get_templates_for_type(call.message.chat.id, currency_to)
    await call.message.edit_text('Выберите шаблон для получения {}:'.format(currency_to),
                                 reply_markup=markup.select_template_to(templates, currency_to))


@dp.callback_query_handler(text='select-all-templates',
                           state=NewOrder.template_to)
async def select_all_to_templates_for_new_order(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    currency_to = data.get('currency_to')
    templates = await db_manager.get_templates_for_type(call.message.chat.id, currency_to)
    template_to = ','.join([str(el[0]) for el in templates])
    template_from = data.get('template_from')
    currency_from = data.get('currency_from')
    amount = data.get('amount')
    exchange_rate = data.get('exchange_rate')
    partial = data.get('partial')
    amount_to = data.get('amount_to')
    amount_from = data.get('amount_from')
    converted_amount = data.get('converted_amount')
    commission_payer = data.get('commission_payer')

    await state.finish()
    await User.main.set()

    await call.message.delete()
    await create_new_order(call.message.chat.id, [currency_from, currency_to, amount, converted_amount,
                                                  amount_from, amount_to, exchange_rate,
                                                  template_from, template_to, commission_payer,
                                                  partial])


@dp.callback_query_handler(lambda call: 'new-order-template_' in call.data,
                           state=NewOrder.template_to)
async def select_template_for_new_order(call: CallbackQuery, state: FSMContext):
    await call.answer()
    template_to = call.data.split('_')[-1]
    data = await state.get_data()
    template_from = data.get('template_from')
    currency_from = data.get('currency_from')
    currency_to = data.get('currency_to')
    amount = data.get('amount')
    exchange_rate = data.get('exchange_rate')
    partial = data.get('partial')
    amount_to = data.get('amount_to')
    amount_from = data.get('amount_from')
    converted_amount = data.get('converted_amount')
    commission_payer = data.get('commission_payer')

    await state.finish()
    await User.main.set()

    await call.message.delete()
    await create_new_order(call.message.chat.id,
                           [currency_from, currency_to, amount, converted_amount,
                            amount_from, amount_to, exchange_rate,
                            template_from, template_to, commission_payer,
                            partial])


@dp.callback_query_handler(lambda call: 'new-order-another-temp_' in call.data,
                           state=NewOrder.template_from)
async def create_new_template_from_order(call: CallbackQuery, state: FSMContext):
    await call.answer()
    t_type = call.data.split('_')[-1]
    await state.update_data({'t_type': t_type,
                             'msg_id': 0,
                             'stage': 'from'})
    await call.message.delete()
    await NewTemplate.name.set()
    await bot.send_message(call.message.chat.id,
                           'Введите название шаблона {} (будет отображаться при выборе счета):'
                           .format(t_type),
                           reply_markup=markup.kb_cancel())


@dp.callback_query_handler(lambda call: 'new-order-another-temp_' in call.data,
                           state=NewOrder.template_to)
async def create_new_template_to_order(call: CallbackQuery, state: FSMContext):
    await call.answer()
    t_type = call.data.split('_')[-1]
    await state.update_data({'t_type': t_type,
                             'msg_id': 0,
                             'stage': 'to'})
    await call.message.delete()
    await NewTemplate.name.set()
    await bot.send_message(call.message.chat.id,
                           'Введите название шаблона {} (будет отображаться при выборе счета):'
                           .format(t_type),
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=NewTemplate.name)
async def get_new_template_name(message: Message, state: FSMContext):
    data = await state.get_data()
    t_type = data.get('t_type')
    await state.update_data({'name': message.text})
    if t_type == 'VISTA EUR':
        await NewTemplate.VistaEUR.acc_number.set()
        await bot.send_message(message.chat.id,
                               'Введите номер Вашего счета VISTA EUR:')
    elif t_type == 'VISTA USD':
        await NewTemplate.VistaUSD.acc_number.set()
        await bot.send_message(message.chat.id,
                               'Введите номер Вашего счета VISTA USD:')
    elif t_type == 'RUB':
        await NewTemplate.RUB.bank.set()
        await bot.send_message(message.chat.id,
                               'Выберите Банк или введите его название вручную:',
                               reply_markup=markup.bank_name_markup())
    elif t_type == 'BYN':
        await NewTemplate.BYN.bank.set()
        await bot.send_message(message.chat.id,
                               'Введите название банка:')
    elif t_type == 'TBH':
        await NewTemplate.THB.bank.set()
        await bot.send_message(message.chat.id,
                               'Введите название банка:')


# ============================================ Edit New Order ================================================
@dp.callback_query_handler(lambda call: 'edit-new-order_' in call.data,
                           state=User)
async def edit_new_order(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(markup.edit_what_new_order(call.data.split('_')[-1]))


@dp.callback_query_handler(lambda call: 'back-to-edit-new-order_' in call.data,
                           state=User)
async def back_to_edit_new_order(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(markup.edit_new_order(call.data.split('_')[-1]))


@dp.callback_query_handler(lambda call: 'new-order-edit-amount_' in call.data,
                           state=User)
async def edit_new_order_amount(call: CallbackQuery, state: FSMContext):
    await call.answer()
    order_id = call.data.split('_')[-1]
    await state.set_data({'order_id': order_id})
    await call.message.delete()
    await User.edit_new_order_amount.set()
    await bot.send_message(call.message.chat.id,
                           'Введите новую сумму заявки:',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=User.edit_new_order_amount)
async def get_new_order_amount(message: Message, state: FSMContext):
    order_id = (await state.get_data()).get('order_id')
    if message.text == 'Отменить':
        await state.finish()
        await User.main.set()
        await bot.send_message(message.chat.id,
                               'Редактирование заявки отменено',
                               reply_markup=markup.main())
        await bot.send_message(message.chat.id,
                               await utils.get_order_text(order_id, 'owner'),
                               reply_markup=markup.edit_new_order(order_id))
        return

    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('stage') is not None:
        await state.finish()
        await User.main.set()
        await bot.send_message(message.chat.id,
                               'Вы не можете отредактировать заявку, т.к. у неё уже есть покупатель',
                               reply_markup=markup.main())
        return

    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Сумма заявки должна быть числом, больше 0!')
    else:
        currency_from = order_data.get('currency_from')
        currency_to = order_data.get('currency_to')
        exchange_rate = float(order_data.get('exchange_rate'))

        commission = await db_manager.get_commission()
        convert_rule = config.convert[(currency_from, currency_to)]
        converted_amount = config.convert[(currency_from, currency_to)]['convert'](amount, exchange_rate)

        if currency_from == convert_rule['commission']:
            amount_from = round(amount * (1 + commission * 2 / 100), 2)
            amount_to = round(converted_amount * (1 + commission / 100), 2)
        else:
            amount_from = round(amount * (1 + commission / 100), 2)
            amount_to = round(converted_amount * (1 + commission * 2 / 100), 2)

        await state.finish()
        await User.main.set()
        msg_id = await db_manager.new_order_amount(order_id, exchange_rate, amount,
                                                   converted_amount, amount_from, amount_to)
        await bot.send_message(message.chat.id,
                               'Заявки изменена!',
                               reply_markup=markup.main())
        await bot.send_message(message.chat.id,
                               await utils.get_order_text(order_id, 'owner'),
                               reply_markup=markup.edit_new_order(order_id))
        await bot.edit_message_text(await utils.get_order_text(order_id, 'customer'),
                                    config.order_channel,
                                    msg_id,
                                    reply_markup=markup.buy_order_from_channel(order_id))


@dp.callback_query_handler(lambda call: 'new-order-edit-exchange-rate_' in call.data,
                           state=User)
async def edit_new_order_exchange_rate(call: CallbackQuery, state: FSMContext):
    await call.answer()
    order_id = call.data.split('_')[-1]
    await state.set_data({'order_id': order_id})
    await call.message.delete()
    await User.edit_new_order_exchange_rate.set()
    await bot.send_message(call.message.chat.id,
                           'Введите новый курс обмена заявки:',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(state=User.edit_new_order_exchange_rate)
async def get_new_order_exchange_rate(message: Message, state: FSMContext):
    order_id = (await state.get_data()).get('order_id')
    if message.text == 'Отменить':
        await state.finish()
        await User.main.set()
        await bot.send_message(message.chat.id,
                               'Редактирование заявки отменено',
                               reply_markup=markup.main())
        await bot.send_message(message.chat.id,
                               await utils.get_order_text(order_id, 'owner'),
                               reply_markup=markup.edit_new_order(order_id))
        return

    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('stage') is not None:
        await state.finish()
        await User.main.set()
        await bot.send_message(message.chat.id,
                               'Вы не можете отредактировать заявку, т.к. у неё уже есть покупатель',
                               reply_markup=markup.main())
        return

    try:
        exchange_rate = float(message.text.replace(',', '.'))
        if exchange_rate <= 0:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Обменный курс заявки должен быть числом, больше 0!')
    else:
        amount = float(order_data.get('amount'))
        currency_from = order_data.get('currency_from')
        currency_to = order_data.get('currency_to')

        commission = await db_manager.get_commission()
        convert_rule = config.convert[(currency_from, currency_to)]
        converted_amount = config.convert[(currency_from, currency_to)]['convert'](amount, exchange_rate)

        if currency_from == convert_rule['commission']:
            amount_from = round(amount * (1 + commission * 2 / 100), 2)
            amount_to = round(converted_amount * (1 + commission / 100), 2)
        else:
            amount_from = round(amount * (1 + commission / 100), 2)
            amount_to = round(converted_amount * (1 + commission * 2 / 100), 2)

        await state.finish()
        await User.main.set()
        msg_id = await db_manager.new_order_amount(order_id, exchange_rate, amount,
                                                   converted_amount, amount_from, amount_to)
        await bot.send_message(message.chat.id,
                               'Заявки изменена!',
                               reply_markup=markup.main())
        await bot.send_message(message.chat.id,
                               await utils.get_order_text(order_id, 'owner'),
                               reply_markup=markup.edit_new_order(order_id))
        await bot.edit_message_text(await utils.get_order_text(order_id, 'customer'),
                                    config.order_channel,
                                    msg_id,
                                    reply_markup=markup.buy_order_from_channel(order_id))
# ============================================ Edit New Order End ================================================


@dp.callback_query_handler(lambda call: 'cancel-new-edit-order_' in call.data,
                           state=User)
async def cancel_new_edit_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('stage') is not None:
        await call.answer('⚠️ За отмену этой заявки у Вас будет снято 1 рейтинг', show_alert=True)
    else:
        await call.answer()
    await call.message.edit_reply_markup(reply_markup=markup.edit_new_order(order_id, True))


@dp.callback_query_handler(lambda call: 'cancel-new-edit-order-d_' in call.data,
                           state=User)
async def cancel_new_edit_order(call: CallbackQuery):
    await call.answer()
    order_id = call.data.split('_')[-1]
    await call.message.edit_reply_markup(reply_markup=markup.edit_new_order(order_id))


@dp.callback_query_handler(lambda call: 'cancel-new-order_' in call.data,
                           state=User)
async def cancel_new_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('stage') is not None:
        await call.answer('⚠️ За отмену этой заявки у Вас будет снято 1 рейтинг', show_alert=True)
    else:
        await call.answer()
    await call.message.edit_reply_markup(reply_markup=markup.cancel_new_order(order_id, True))


@dp.callback_query_handler(lambda call: 'cancel-new-order-d_' in call.data,
                           state=User)
async def cancel_new_order(call: CallbackQuery):
    await call.answer()
    order_id = call.data.split('_')[-1]
    await call.message.edit_reply_markup(reply_markup=markup.cancel_new_order(order_id))


@dp.callback_query_handler(lambda call: 'cancel-new-order-a_' in call.data,
                           state=User)
async def cancel_new_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    minus_rate = False

    if order_data.get('stage') is not None:
        await call.answer('Заявка была удалена\n'
                          'У Вас было снято 1 рейтинг', show_alert=True)
        minus_rate = True
    else:
        await call.answer('Заявка удалена', show_alert=True)

    msg_id = await db_manager.delete_order(order_id, minus_rate=minus_rate)
    if msg_id:
        try:
            await bot.delete_message(config.order_channel,
                                     msg_id)
        except:
            pass

    orders = await db_manager.get_user_orders(call.message.chat.id)
    if not orders:
        await call.message.edit_text('У Вас нет активных заявок')
        return

    await call.message.edit_text('Ваши активные заявки',
                                 reply_markup=markup.user_orders_markup(orders))


# ==========================================================================================================
# ======================================ПОИСК ЗАЯВКИ======================================================
# ==========================================================================================================
@dp.message_handler(text='Найти заявку', state=User.main)
async def find_order(message: Message):
    await bot.send_message(message.chat.id,
                           'Выберите валюту, которую хотите получить:',
                           reply_markup=markup.find_order_currency_from(
                               await db_manager.find_order_from(message.chat.id)))


@dp.callback_query_handler(lambda call: 'select-currency-from_' in call.data,
                           state=User.main)
async def find_order_get_currency_from(call: CallbackQuery):
    currency_from = call.data.split('_')[-1]
    await call.answer()
    await call.message.edit_text('Выберите валюту, которой хотите оплатить:',
                                 reply_markup=markup.find_order_currency_to(
                                     await db_manager.find_order_to(currency_from, call.message.chat.id),
                                     currency_from))


@dp.callback_query_handler(lambda call: 'select-currency-to_' in call.data,
                           state=User.main)
async def find_order_get_currency_from(call: CallbackQuery):
    cur_to, cur_from = call.data.split('_')[1:]
    orders = await db_manager.get_orders(call.message.chat.id, cur_from, cur_to)
    if not orders:
        await call.answer('По этому направлению нет активных заявок!', show_alert=True)
        return

    await call.answer()
    await call.message.edit_text('Выберите заявку:',
                                 reply_markup=markup.find_orders_markup(orders))


@dp.callback_query_handler(lambda call: 'show-order-data_' in call.data,
                           state=User.main)
async def show_order_data(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    await call.message.edit_text(await utils.get_order_text(order_id, 'customer'),
                                 reply_markup=markup.buy_order(order_id, order_data.get('partial')))


@dp.callback_query_handler(lambda call: 'back-to-order-info_' in call.data,
                           state=User)
async def back_to_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    await call.message.edit_text(await utils.get_order_text(order_id, 'customer'),
                                 reply_markup=markup.buy_order(order_id, order_data.get('partial')))


# ================================== ПОКУПКА ЗАЯВКИ =========================================================
# ================================= Частичная покупка =======================================================
@dp.callback_query_handler(lambda call: 'partial-buy-order_' in call.data,
                           state=User.main)
async def partial_buy_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    currency_from = order_data.get('currency_from')
    templates = await db_manager.get_templates_for_type(call.message.chat.id, currency_from)
    await call.message.edit_text(f'Выберите шаблон для получения {currency_from}',
                                 reply_markup=markup.select_t_to_buy_order_partial(order_id, templates))


@dp.callback_query_handler(lambda call: 'buy-order-p-template-to_' in call.data,
                           state=User.main)
async def select_partial_template_buy_to(call: CallbackQuery, state: FSMContext):
    t_to, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_order_data(order_id)

    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    currency_to = order_data.get('currency_to')
    if currency_to in ['VISTA EUR', 'VISTA USD', 'THB']:
        templates = await db_manager.get_templates_for_type(call.message.chat.id, currency_to)
        await call.message.edit_text(f'Выберите шаблон, с которого будете отправлять {currency_to}',
                                     reply_markup=markup.select_t_from_buy_order_partial(order_id, t_to, templates))
        return

    await call.message.delete()
    await User.get_partial_amount.set()
    await state.set_data({'order_id': order_id,
                          't_to': t_to})
    await bot.send_message(call.message.chat.id,
                           f'Текущая сумма заявки: <b>{order_data.get("amount")} '
                           f'{order_data.get("currency_from")}</b>\n\n'
                           f'Введите сумму {order_data.get("currency_from")} которую хотите купить:',
                           reply_markup=markup.kb_cancel())


@dp.callback_query_handler(lambda call: 'buy-order-p-template-from_' in call.data,
                           state=User.main)
async def select_partial_template_buy_from(call: CallbackQuery, state: FSMContext):
    t_from, t_to, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_order_data(order_id)

    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    await call.message.delete()
    await User.get_partial_amount.set()
    await state.set_data({'order_id': order_id,
                          't_to': t_to,
                          't_from': t_from})

    await bot.send_message(call.message.chat.id,
                           f'Текущая сумма заявки: <b>{order_data.get("amount")} '
                           f'{order_data.get("currency_from")}</b>\n\n'
                           f'Введите сумму {order_data.get("currency_from")} которую хотите купить:',
                           reply_markup=markup.kb_cancel())


@dp.message_handler(text='Отменить',
                    state=User.get_partial_amount)
async def cancel_buy_partial_order(message: Message, state: FSMContext):
    # data = await state.get_data()
    # order_id = data.get('order_id')
    # t_to = data.get('t_to')
    # t_from = data.get('t_from')
    await state.finish()
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Покупка заявки отменена',
                           reply_markup=markup.main())


@dp.message_handler(state=User.get_partial_amount)
async def get_partial_amount_buy_order(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Пожалуйста, введите число больше 0')
    else:
        data = await state.get_data()
        order_id = data.get('order_id')
        t_to = data.get('t_to')
        t_from = data.get('t_from')
        order_data = await db_manager.get_order_data(order_id)
        if amount > float(order_data.get('amount')):
            await bot.send_message(message.chat.id,
                                   'Сумма покупки не может быть больше, чем сумма заявки')
            return

        if amount == order_data.get('amount'):
            await bot.send_message(message.chat.id,
                                   'Для того, что бы выкупить всю заявку, пожалуйста, '
                                   'воспользуйтесь кнопкой Обменять вместо Частичный выкуп')
            return

        await state.finish()
        await User.main.set()
        await buy_order(message.chat.id, order_id, t_to, t_from, amount, 0)


@dp.callback_query_handler(lambda call: 'buy-order-p-new-template-to_' in call.data,
                           state=User.main)
async def add_new_template_buy_order_partial_to(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    await state.update_data({'order_id': order_id,
                             'stage': 'buy-order-to-partial',
                             't_type': order_data.get("currency_from")})
    await NewTemplate.name.set()
    await bot.send_message(call.message.chat.id,
                           f'Введите название шаблона {order_data.get("currency_from")} '
                           f'(будет отображаться при выборе счета):',
                           reply_markup=markup.kb_cancel())


@dp.callback_query_handler(lambda call: 'buy-order-p-new-template-from_' in call.data,
                           state=User.main)
async def add_new_template_buy_order_partial_to(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    t_to, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_order_data(order_id)
    await state.update_data({'order_id': order_id,
                             'stage': 'buy-order-from-partial',
                             't_to': t_to,
                             't_type': order_data.get("currency_to")})
    await NewTemplate.name.set()
    await bot.send_message(call.message.chat.id,
                           f'Введите название шаблона {order_data.get("currency_to")} '
                           f'(будет отображаться при выборе счета):',
                           reply_markup=markup.kb_cancel())


@dp.callback_query_handler(lambda call: 'partial-approve-decline_' in call.data,
                           state=User)
async def decline_partial_buy_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    await call.answer('Покупатель будет уведомлен о Вашем отказе', show_alert=True)
    await call.message.delete()
    customer_id = await db_manager.decline_partial_buy_order(order_id)
    if customer_id:
        try:
            await bot.send_message(customer_id,
                                   f'Заявка №{order_id}\n'
                                   f'Владелец отклонил Ваш запрос на частичную покупку заявки')
        except:
            pass


@dp.callback_query_handler(lambda call: 'partial-approve-accept_' in call.data,
                           state=User)
async def accept_partial_exchange(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    await call.answer()
    await call.message.delete()
    order_data = await db_manager.get_buy_order_data(order_id)

    currency_from = order_data.get('currency_from')
    currency_to = order_data.get('currency_to')
    exchange_rate = float(order_data.get('exchange_rate'))
    msg_id = order_data.get('msg_id')

    old_amount = float(order_data.get('amount'))
    partial_amount = float(order_data.get('partial_amount'))

    commission = await db_manager.get_commission()
    convert_rule = config.convert[(currency_from, currency_to)]

    converted_amount = config.convert[(currency_from, currency_to)]['convert'](partial_amount, exchange_rate)
    if currency_from == convert_rule['commission']:
        amount_from = round(partial_amount * (1 + commission * 2 / 100), 2)
        amount_to = round(converted_amount * (1 + commission / 100), 2)
    else:
        amount_from = round(partial_amount * (1 + commission / 100), 2)
        amount_to = round(converted_amount * (1 + commission * 2 / 100), 2)

    try:
        await bot.delete_message(config.order_channel,
                                 msg_id)
    except exceptions.MessageCantBeDeleted:
        await bot.edit_message_text('Удалена',
                                    config.order_channel,
                                    msg_id)
    except exceptions.MessageToDeleteNotFound:
        pass

    await db_manager.change_order_amounts(order_id, {'amount': partial_amount,
                                                     'converted_amount': converted_amount,
                                                     'amount_from': amount_from,
                                                     'amount_to': amount_to})

    new_order_amount = old_amount - partial_amount
    converted_amount = config.convert[(currency_from, currency_to)]['convert'](new_order_amount, exchange_rate)
    if currency_from == convert_rule['commission']:
        amount_from = round(new_order_amount * (1 + commission * 2 / 100), 2)
        amount_to = round(converted_amount * (1 + commission / 100), 2)
    else:
        amount_from = round(new_order_amount * (1 + commission / 100), 2)
        amount_to = round(converted_amount * (1 + commission * 2 / 100), 2)

    new_order_id = await db_manager.create_new_order(call.message.chat.id, currency_from, currency_to,
                                                     new_order_amount, converted_amount, amount_from, amount_to,
                                                     exchange_rate, order_data.get('template_from'),
                                                     order_data.get('template_to'),
                                                     order_data.get('commission_payer'),
                                                     0)
    await db_manager.approve_new_order(new_order_id)
    msg_id = (await bot.send_message(config.order_channel,
                                     await utils.get_order_text(new_order_id, who='customer'),
                                     reply_markup=markup.buy_order_from_channel(new_order_id))).message_id
    await db_manager.set_order_msg_id(new_order_id, msg_id)

    order_data = await db_manager.get_buy_order_data(order_id)
    if order_data.get('commission_payer') == 'customer':
        admin_template_data = await utils.get_admin_template_data(
            await db_manager.get_active_admin_template(order_data.get("currency_to")))
        await bot.send_message(order_data.get('customer_id'),
                               f'Заявка №{order_id}!\n'
                               f'Запрос на частичный выкуп был принят владельцем заявки\n\n'
                               f'Сейчас Вы должны перевести {order_data.get("amount_to")} '
                               f'{order_data.get("currency_to")} по указанным ниже реквизитам:\n'
                               f'{admin_template_data}\n\n'
                               f'Назначение перевода: Заявка <b>{order_id}</b>\n\n'
                               f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                               f'Обязательно указывайте правильное назначение перевода.\n'
                               f'Заявки с неверным назначением перевода будут обработаны в последнюю очередь.\n\n'
                               f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                               f'После того, как вы совершите перевод, обязательно нажмите кнопку «Перевёл».',
                               reply_markup=markup.first_pay(order_id))
        await bot.send_message(call.message.chat.id,
                               'Спасибо, информация принята! Пожалуйста, ожидайте готовность гаранта к обмену. '
                               'Мы вас моментально уведомим об этом.',
                               reply_markup=markup.cancel_new_order(order_id))
    else:
        admin_template_data = await utils.get_admin_template_data(
            await db_manager.get_active_admin_template(order_data.get("currency_from")))
        await bot.send_message(call.message.chat.id,
                               f'Отлично!\n\n'
                               f'Сейчас Вы должны перевести {order_data.get("amount_from")} '
                               f'{order_data.get("currency_from")} по указанным ниже реквизитам:\n'
                               f'{admin_template_data}\n\n'
                               f'Назначение перевода: Заявка <b>{order_id}</b>\n\n'
                               f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                               f'Обязательно указывайте правильное назначение перевода.\n'
                               f'Заявки с неверным назначением перевода будут обработаны в последнюю очередь.\n\n'
                               f'⚠️ <b>ВНИМАНИЕ!</b>\n'
                               f'После того, как вы совершите перевод, обязательно нажмите кнопку «Перевёл».',
                               reply_markup=markup.first_pay(order_id))
        await bot.send_message(order_data.get('customer_id'),
                               f'Заявка №{order_id}!\n'
                               f'Запрос на частичный выкуп был принят владельцем заявки\n\n'
                               f' Пожалуйста, ожидайте готовность гаранта к обмену. '
                               f'Мы вас моментально уведомим об этом.',
                               reply_markup=markup.cancel_buy_order(order_id))
# ==================================== Частичная покупка END ==============================================

    
@dp.callback_query_handler(lambda call: 'buy-that-order_' in call.data,
                           state=User.main)
async def buy_that_order(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    currency_from = order_data.get('currency_from')
    templates = await db_manager.get_templates_for_type(call.message.chat.id, currency_from)
    await call.message.edit_text(f'Выберите шаблон для получения {currency_from}',
                                 reply_markup=markup.select_t_to_buy_order(order_id, templates))


@dp.callback_query_handler(lambda call: 'buy-order-template-to_' in call.data,
                           state=User.main)
async def select_template_buy_to(call: CallbackQuery):  # Шаблон, накоторый будет получать кастомер
    t_to, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_order_data(order_id)

    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    currency_to = order_data.get('currency_to')
    if currency_to in ['VISTA EUR', 'VISTA USD', 'THB']:
        templates = await db_manager.get_templates_for_type(call.message.chat.id, currency_to)
        await call.message.edit_text(f'Выберите шаблон, с которого будете отправлять {currency_to}',
                                     reply_markup=markup.select_t_from_buy_order(order_id, t_to, templates))
        return

    await call.message.delete()
    await buy_order(call.message.chat.id, order_id, t_to)


@dp.callback_query_handler(lambda call: 'buy-order-template-from_' in call.data,
                           state=User.main)
async def select_template_buy_from(call: CallbackQuery):  # Шаблон, с которого будет отправлять кастомер
    t_from, t_to, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_order_data(order_id)

    if order_data.get('blocked') or not order_data:
        await call.answer('Эта заявка более недоступна!', show_alert=True)
        await call.message.delete()
        return

    await call.answer()
    await call.message.delete()
    await buy_order(call.message.chat.id, order_id, t_to, t_from)


@dp.callback_query_handler(lambda call: 'buy-order-new-template-to_' in call.data,
                           state=User.main)
async def add_new_template_buy_order_to(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    await state.update_data({'order_id': order_id,
                             'stage': 'buy-order-to',
                             't_type': order_data.get("currency_from")})
    await NewTemplate.name.set()
    await bot.send_message(call.message.chat.id,
                           f'Введите название шаблона {order_data.get("currency_from")} '
                           f'(будет отображаться при выборе счета):',
                           reply_markup=markup.kb_cancel())


@dp.callback_query_handler(lambda call: 'buy-order-new-template-from_' in call.data,
                           state=User.main)
async def add_new_template_buy_order_to(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    t_to, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_order_data(order_id)
    await state.update_data({'order_id': order_id,
                             'stage': 'buy-order-from',
                             't_to': t_to,
                             't_type': order_data.get("currency_to")})
    await NewTemplate.name.set()
    await bot.send_message(call.message.chat.id,
                           f'Введите название шаблона {order_data.get("currency_to")} '
                           f'(будет отображаться при выборе счета):',
                           reply_markup=markup.kb_cancel())


@dp.callback_query_handler(lambda call: 'cancel-this-buy-order_' in call.data,
                           state=User)
async def cancel_buy_order(call: CallbackQuery):
    await call.answer('В случае отмены Вашей заявки, у Вас будет снято 1 рейтинга', show_alert=True)
    order_id = call.data.split('_')[-1]
    await call.message.edit_reply_markup(reply_markup=markup.cancel_buy_order_approve(order_id))


@dp.callback_query_handler(lambda call: 'cancel-this-buy-order-d_' in call.data,
                           state=User)
async def cancel_buy_order_decline(call: CallbackQuery):
    await call.answer()
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_buy_order_data(order_id)
    stage = order_data.get('stage')
    if stage is None:
        await call.message.edit_reply_markup(reply_markup=markup.cancel_buy_order(order_id))
    elif stage == 'first_pay':
        commission_payer = order_data.get('commission_payer')
        owner_id = order_data.get('owner_id')

        if call.message.from_user.id == owner_id:
            # Кнопка у овнера на этом шаге может быть только,
            # если комиссию платит он -> первый платеж делает он
            await call.message.edit_reply_markup(reply_markup=markup.first_pay(order_id))
        else:
            if commission_payer == 'owner':
                await call.message.edit_reply_markup(reply_markup=markup.cancel_buy_order(order_id))
            else:
                await call.message.edit_reply_markup(reply_markup=markup.first_pay(order_id))
    elif stage == 'second_pay':
        # В клюбом случае, кнопка отмены заявки на данном этапе может быть только
        # с клавиатурой second_pay
        await call.message.edit_reply_markup(reply_markup=markup.second_pay(order_id))


@dp.callback_query_handler(lambda call: 'cancel-this-buy-order-a_' in call.data,
                           state=User)
async def cancel_buy_order_approve(call: CallbackQuery):
    await call.message.delete()
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_buy_order_data(order_id)

    if not order_data:
        await call.answer('Заявка уже не существует', show_alert=True)
        return

    await call.answer('Заявка была отменена. У Вас было снято 1 рейтинга', show_alert=True)
    if order_data.get('owner_id') == call.message.chat.id:
        await db_manager.delete_order(order_id, minus_rate=True)
        await bot.send_message(order_data.get('customer_id'),
                               f'Заявка №{order_id}\n'
                               f'Владелец удалил заявку')
        return

    user_id, msg_id = await db_manager.cancel_buy_order(call.message.chat.id, order_id)
    if not msg_id:
        msg_id = (await bot.send_message(config.order_channel,
                                         await utils.get_order_text(order_id, 'customer'),
                                         reply_markup=markup.buy_order_from_channel(order_id))).message_id
        await db_manager.set_order_msg_id(order_id, msg_id)
    await bot.send_message(user_id,
                           f'Заявка №{order_id}\n'
                           f'Клиент отказался от покупки. Заявка была снова размещена в канале')

# ============================= Подтверждение первого перевода ===============================
@dp.callback_query_handler(lambda call: 'first-pay-done_' in call.data,
                           state=User.main)
async def first_pay_done(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_buy_order_data(order_id)
    if not order_data.get('blocked') or order_data.get('stage') != 'first_pay' \
            or not (order_data.get('owner_id') != call.message.from_user.id
                    and order_data.get('customer_id') != call.message.from_user.id):
        await call.answer('Заявка была отменена', show_alert=True)
        await call.message.delete()
        return

    await call.answer('Гарант будет уведомлен о переводе!', show_alert=True)
    await call.message.edit_text('Спасибо, информация принята! Пожалуйста, '
                                 'ожидайте подтверждение получения вашего перевода.\n'
                                 'Бот подтверждает получение средств новым сообщением.')
    await db_manager.first_pay_done(order_id)
    await bot.send_message(config.manager_id,
                           await utils.get_order_text(order_id, 'admin_first_pay', bot),
                           reply_markup=markup.admin_first_pay_approve(order_id))


@dp.callback_query_handler(lambda call: 'first-pay-delay_' in call.data,
                           state=User.main)
async def first_pay_delay(call: CallbackQuery):
    delay, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_buy_order_data(order_id)
    if not order_data.get('blocked') or order_data.get('stage') != 'first_pay' \
            or not (order_data.get('owner_id') != call.message.from_user.id
                    and order_data.get('customer_id') != call.message.from_user.id):
        await call.answer('Заявка была отменена', show_alert=True)
        await call.message.delete()
        return

    await call.answer('Гаран будет уведомлен!', show_alert=True)
    if delay == '15-min':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана Гаранту.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 15 минут.')
        await bot.send_message(config.manager_id,
                               f'Плательщик по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 15 минут')
    elif delay == '30-min':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана Гаранту.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 30 минут.')
        await bot.send_message(config.manager_id,
                               f'Плательщик по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 30 минут')
    elif delay == '1-hour':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана Гаранту.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 1 часа.')
        await bot.send_message(config.manager_id,
                               f'Плательщик по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 1 часа')
    elif delay == '3-hour':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана Гаранту.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 3ех часов')
        await bot.send_message(config.manager_id,
                               f'Плательщик по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 3ех часов')


# ========================= Подтверждение второго перевода ===================================
@dp.callback_query_handler(lambda call: 'second-pay-done_' in call.data,
                           state=User.main)
async def second_pay_done(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_buy_order_data(order_id)
    if not order_data or not order_data.get('blocked') or order_data.get('stage') != 'second_pay' \
            or not (order_data.get('owner_id') != call.message.from_user.id
                    and order_data.get('customer_id') != call.message.from_user.id):
        await call.answer('Заявка была отменена', show_alert=True)
        await call.message.delete()
        return

    await call.answer('Вторая сторона получит уведомление о переводе средств!\n'
                      'Ожидайте его подтверждения', show_alert=True)
    await call.message.edit_text('Спасибо, информация принята!\n'
                                 'Как только ваш партнер по обмену подтвердит получение средств от '
                                 'вас, мы отправим {} на ваш счет.\n'
                                 'Пожалуйста, ожидайте уведомление от нас!'
                                 .format('{} {}'.format(order_data.get('amount'),
                                                        order_data.get('currency_from'))
                                         if order_data.get('commission_payer') == 'owner'
                                         else '{} {}'.format(order_data.get('converted_amount'),
                                                             order_data.get('currency_to'))))
    await db_manager.second_pay_done(order_id)
    await bot.send_message(order_data.get('owner_id')
                           if order_data.get('commission_payer') == 'owner'
                           else order_data.get('customer_id'),
                           await utils.get_order_text(order_id, 'second_pay'),
                           reply_markup=markup.second_pay_approve(order_id))


@dp.callback_query_handler(lambda call: 'second-pay-delay_' in call.data,
                           state=User.main)
async def second_pay_delay(call: CallbackQuery):
    delay, order_id = call.data.split('_')[1:]
    order_data = await db_manager.get_buy_order_data(order_id)
    if not order_data or not order_data.get('blocked') or order_data.get('stage') != 'second_pay' \
            or not (order_data.get('owner_id') != call.message.from_user.id
                    and order_data.get('customer_id') != call.message.from_user.id):
        await call.answer('Заявка была отменена', show_alert=True)
        await call.message.delete()
        return

    await call.answer('Ваш партнер по обмену будет уведомлен!', show_alert=True)
    if order_data.get('owner_id') == call.message.chat.id:
        user_id = order_data.get('customer_id')
    else:
        user_id = order_data.get('owner_id')
    if delay == '15-min':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана вашему партнеру по обмену.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 15 минут.')
        await bot.send_message(user_id,
                               f'Ваш партнер по обмену по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 15 минут')
    elif delay == '30-min':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана вашему партнеру по обмену.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 30 минут.')
        await bot.send_message(user_id,
                               f'Ваш партнер по обмену по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 30 минут')
    elif delay == '1-hour':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана вашему партнеру по обмену.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 1 часа.')
        await bot.send_message(user_id,
                               f'Ваш партнер по обмену по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 1 часа')
    elif delay == '3-hour':
        await bot.send_message(call.message.chat.id,
                               f'Спасибо, информация принята и передана вашему партнеру по обмену.\n'
                               f'Ожидаем ваш перевод по заявке №{order_id} в течении 3ех часов')
        await bot.send_message(user_id,
                               f'Ваш партнер по обмену по заявке №{order_id} сообщает, что произведет платеж '
                               f'в течении 3ех часов')


# ======================= Подтверждение получения второго перевода ===========================
@dp.callback_query_handler(lambda call: 'approve-second-pay_' in call.data,
                           state=User)
async def approve_second_pay(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(markup.second_pay_approve(call.data.split('_')[-1], True))


@dp.callback_query_handler(lambda call: 'approve-second-pay-a_' in call.data,
                           state=User)
async def accept_approve_second_pay(call: CallbackQuery):
    order_id = call.data.split('_')[-1]
    await call.answer('Спасибо за подтверждение! Ожидайте перевода!', show_alert=True)
    await db_manager.second_pay_approved(order_id)
    await call.message.edit_text('Спасибо, информация принята!\n'
                                 'Как только Гарант переведет средства Вашему партнеру и закроет заявку Вам'
                                 ' будет начислено 1 рейтинг.\n'
                                 'Спасибо, что воспользовались нашим сервисом! Ждем Вас снова!')
    order_data = await db_manager.get_buy_order_data(order_id)
    await bot.send_message(order_data.get('customer_id')
                           if order_data.get('commission_payer') == 'owner'
                           else order_data.get('owner_id'),
                           f'Заявка №{order_id}\n\n'
                           f'Вторая сторона подвтердила Ваш перевод\n'
                           f'После перечисления оставшейся суммы Гарантом заявка будет закрыта и Вам будет '
                           f'начислен рейтинг!\n'
                           f'Спасибо, что пользуетесь нашим сервисом')
    await bot.send_message(config.manager_id,
                           await utils.get_order_text(order_id, 'admin_last_pay', bot),
                           reply_markup=markup.admin_buy_order_done(order_id))


@dp.callback_query_handler(lambda call: 'approve-second-pay-d_' in call.data,
                           state='*')
async def cancel_approve_second_pay(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(markup.second_pay_approve(call.data.split('_')[-1]))


@dp.callback_query_handler(lambda call: 'not-enough-second-pay_' in call.data,
                           state=User)
async def not_enough_second_pay(call: CallbackQuery):
    try:
        await dp.throttle('not-enough-second-pay', rate=300)
    except exceptions.Throttled:
        await call.answer('Уведомление уже было отправлено Гаранту!\n'
                          'Следующее уведомление можно будет отправить только через 5 минут',
                          show_alert=True)
    else:
        await call.answer('Гарант получит уведомление. Пожалуйста, ожидайте решения вопроса',
                          show_alert=True)
        order_id = call.data.split('_')[-1]
        await bot.send_message(config.manager_id,
                               await utils.get_order_text(order_id, 'not-enough-second-pay', bot))


# =================================================================================================
# ================================ МОИ ЗАЯВКИ =====================================================
# =================================================================================================
@dp.message_handler(text='Мои заявки', state=User.main)
async def my_orders_menu(message: Message):
    orders = await db_manager.get_user_orders(message.chat.id)
    if not orders:
        await bot.send_message(message.chat.id,
                               'У Вас нет активных заявок')
        return

    await bot.send_message(message.chat.id,
                           'Ваши активные заявки',
                           reply_markup=markup.user_orders_markup(orders))


@dp.callback_query_handler(lambda call: 'show-my-order_' in call.data,
                           state=User.main)
async def show_my_order(call: CallbackQuery):
    await call.answer()
    order_id = call.data.split('_')[-1]
    order_data = await db_manager.get_order_data(order_id)
    if not order_data:
        await call.message.delete()
        return

    text, order_markup = await utils.get_my_order(order_id)
    await bot.send_message(call.message.chat.id,
                           text,
                           reply_markup=order_markup)


# ==============================================================================================
# ================================= ЛИЧНЫЙ КАБИНЕТ =============================================
# ==============================================================================================
@dp.message_handler(text='Личный кабинет', state=User.main)
async def process_personal_cab(message: Message):
    user_data = await db_manager.get_user_data(message.chat.id)
    await bot.send_message(message.chat.id,
                           f'Ваш ID: {message.chat.id}\n'
                           f'Ваш рейтинг: {user_data.get("rate")}\n'
                           f'Завершенных заявок: {user_data.get("closed_count")}\n\n'
                           f'ФИО: {user_data.get("fio")}\n'
                           f'Номер телефона: {user_data.get("phone")}\n'
                           f'E-mail: {user_data.get("email")}\n'
                           f'Часовой пояс: {user_data.get("timezone")}',
                           reply_markup=markup.personal_cab())


@dp.callback_query_handler(text='show-referral-sys', state=User.main)
async def show_referral_stat(call: CallbackQuery):
    await call.answer()
    ref_stat = await db_manager.get_referral_stat(call.message.chat.id)
    await call.message.edit_text(f'Ваша реферальная ссылка:\n'
                                 f'https://t.me/{config.bot_name}?start={call.message.chat.id}\n\n'
                                 f'Вы пригласили: {ref_stat.get("ref_count")} человек, которые принесли Вам '
                                 f'{ref_stat.get("income"):.2f} 🍪',
                                 reply_markup=markup.referral_sys())


@dp.callback_query_handler(text='edit-personal-data', state=User.main)
async def edit_personal_data(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(markup.edit_personal_data())


@dp.callback_query_handler(text='back-to-personal-cab', state=User.main)
async def back_to_personal_cab(call: CallbackQuery):
    await call.answer()
    user_data = await db_manager.get_user_data(call.message.chat.id)
    await call.message.edit_text(f'Ваш ID: {call.message.chat.id}\n'
                                 f'Ваш рейтинг: {user_data.get("rate")}\n'
                                 f'Завершенных заявок: {user_data.get("closed_count")}\n\n'
                                 f'ФИО: {user_data.get("fio")}\n'
                                 f'Номер телефона: {user_data.get("phone")}\n'
                                 f'E-mail: {user_data.get("email")}\n'
                                 f'Часовой пояс: {user_data.get("timezone")}',
                                 reply_markup=markup.personal_cab())


@dp.callback_query_handler(lambda call: 'edit-data_' in call.data,
                           state=User.main)
async def edit_data_chose(call: CallbackQuery):
    what = call.data.split('_')[-1]
    await call.message.delete()
    if what == 'fio':
        await User.edit_fio.set()
        await bot.send_message(call.message.chat.id,
                               'Пожалуйста, введите новое значение параметра ФИО:',
                               reply_markup=markup.kb_cancel())
    elif what == 'phone':
        await User.edit_phone.set()
        await bot.send_message(call.message.chat.id,
                               'Пожалуйста, введите новое значение параметра Номер телефона:',
                               reply_markup=markup.kb_cancel())
    elif what == 'email':
        await User.edit_email.set()
        await bot.send_message(call.message.chat.id,
                               'Пожалуйста, введите новое значение параметра E-mail:',
                               reply_markup=markup.kb_cancel())
    elif what == 'timezone':
        await User.edit_timezone.set()
        await bot.send_message(call.message.chat.id,
                               'Пожалуйста, введите новое значение параметра Часовой пояс:',
                               reply_markup=markup.kb_cancel())


@dp.message_handler(text='Отменить',
                    state=[User.edit_fio, User.edit_phone,
                           User.edit_email, User.edit_timezone])
async def cancel_new_data_value(message: Message):
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Изменения отменены',
                           reply_markup=markup.main())
    await process_personal_cab(message)


@dp.message_handler(state=User.edit_fio)
async def get_new_fio_value(message: Message):
    await db_manager.set_fio(message.chat.id, message.text)
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Новые данные сохранены!',
                           reply_markup=markup.main())
    await process_personal_cab(message)


@dp.message_handler(state=User.edit_phone)
async def get_new_phone_value(message: Message):
    await db_manager.set_phone(message.chat.id, message.text)
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Новые данные сохранены!',
                           reply_markup=markup.main())
    await process_personal_cab(message)


@dp.message_handler(state=User.edit_email)
async def get_new_email_value(message: Message):
    await db_manager.set_email(message.chat.id, message.text)
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Новые данные сохранены!',
                           reply_markup=markup.main())
    await process_personal_cab(message)


@dp.message_handler(state=User.edit_timezone)
async def get_new_timezone_value(message: Message):
    await db_manager.set_timezone(message.chat.id, message.text)
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Новые данные сохранены!',
                           reply_markup=markup.main())
    await process_personal_cab(message)


@dp.message_handler(text='Отменить', state='*')
async def cancel_anything(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get('msg_id'):
        try:
            await bot.delete_message(message.chat.id,
                                     data.get('msg_id'))
        except:
            pass
    await state.finish()
    await User.main.set()
    await bot.send_message(message.chat.id,
                           'Действие отменено',
                           reply_markup=markup.main())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
