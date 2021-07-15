from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from . import config, utils


def kb_cancel():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(KeyboardButton('Отменить'))
    return m


def bank_name_markup():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(KeyboardButton('Тинькоф'))
    m.row(KeyboardButton('Сбербанк'))
    m.row(KeyboardButton('Отменить'))
    return m


def card_type_markup():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(KeyboardButton('VISA'))
    m.row(KeyboardButton('MasterCard'))
    m.row(KeyboardButton('Maestro'), KeyboardButton('Мир'))
    m.row(KeyboardButton('Отменить'))
    return m


def admin():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(KeyboardButton('Активные обмены'), KeyboardButton('Заявки на одобрении'))
    m.row(KeyboardButton('Все рефералы'), KeyboardButton('Статистика проекта'))
    m.row(KeyboardButton('Счета'), KeyboardButton('Настройки'))
    return m


def minus_referral_income():
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Снять баланс', callback_data='minus-ref-income'))
    return m


def admin_templates():
    m = InlineKeyboardMarkup()
    for cur in ['VISTA EUR', 'VISTA USD', 'THB']:
        m.row(InlineKeyboardButton(cur, callback_data=f'get-admin-templates_{cur}'))
    return m


def admin_templates_by_cur(templates, currency):
    m = InlineKeyboardMarkup()
    for template in templates:
        m.row(InlineKeyboardButton('{}{}'.format('✅ ' if template.get('active') else '',
                                                 template.get('number')),
                                   callback_data=f'show-admin-template_{template.get("id")}'))
    m.row(InlineKeyboardButton('➕ Добавить шаблон', callback_data=f'add-new-admin-template_{currency}'))
    m.row(InlineKeyboardButton('🔙 назад', callback_data='back-to-admin-currencies'))
    return m


def admin_template_menu(template, delete=False):
    m = InlineKeyboardMarkup()
    t_id = template.get("id")
    currency = template.get("currency")
    if not template.get('active'):
        m.row(InlineKeyboardButton('Сделать активным',
                                   callback_data=f'make-active-admin-template_{t_id}_{currency}'))
        if delete:
            m.row(InlineKeyboardButton('Удалить', callback_data=f'fill-admin-template_{t_id}'),
                  InlineKeyboardButton('Отменить', callback_data=f'delete-cancel-admin-template_{t_id}'))
        else:
            m.row(InlineKeyboardButton('Удалить шаблон', callback_data=f'delete-admin-template_{t_id}'))
    m.row(InlineKeyboardButton('🔙 назад', callback_data=f'back-to-admin-templates_{currency}'))
    return m


def settings(moderate: bool):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Редактировать комиссию', callback_data='edit-commission'))
    m.row(InlineKeyboardButton('Отключить модерацию' if moderate else 'Включить модерацию',
                               callback_data='switch-moderate'))
    return m


def main():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(KeyboardButton('Создать заявку'))
    m.row(KeyboardButton('Найти заявку'), KeyboardButton('Мои заявки'))
    m.row(KeyboardButton('Мои шаблоны'), KeyboardButton('Личный кабинет'))
    return m


def cb_rf(rate):
    if not rate: return None
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('По курсу ЦБРФ', callback_data='set-cb-rf'))
    return m


def buy_order_from_channel(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Обменять', url=f'https://t.me/{config.bot_name}?start=buyorder_{order_id}'))
    return m


def buy_order(order_id, partial=False):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Обменять', callback_data='buy-that-order_{}'.format(order_id)))
    if partial:
        m.row(InlineKeyboardButton('Частичный выкуп', callback_data=f'partial-buy-order_{order_id}'))
    return m


def my_templates(templates):
    m = InlineKeyboardMarkup()
    for temp in templates:
        t_id, name, _ = temp
        m.row(InlineKeyboardButton(name, callback_data='template-info_{}'.format(t_id)))
    m.row(InlineKeyboardButton('➕ Добавить шаблон', callback_data='add-new-template'))
    return m


def template_markup(t_id, delete=False):
    m = InlineKeyboardMarkup()
    if delete:
        m.row(InlineKeyboardButton('🗑 Удалить', callback_data='delete-template-accept_{}'
                                   .format(t_id)),
              InlineKeyboardButton('Отменить', callback_data='delete-template-decline_{}'.format(t_id)))
    else:
        m.row(InlineKeyboardButton('🗑 Удалить шаблон', callback_data='delete-template_{}'
                                   .format(t_id)))
    m.row(InlineKeyboardButton('🔙 назад', callback_data='back-to-templates'))
    return m


def new_template_type():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(*[InlineKeyboardButton(t_type, callback_data='new-template-type_{}'.format(t_type))
            for t_type in config.all_template_types.keys()])
    return m


def order_currency_from():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(*[InlineKeyboardButton(t_type, callback_data='order-currency-from_{}'.format(t_type))
            for t_type in config.all_template_types.keys()])
    return m


def order_currency_to(currency_from):
    m = InlineKeyboardMarkup(row_width=2)
    m.add(*[InlineKeyboardButton(t_type, callback_data='order-currency-to_{}'.format(t_type))
            for t_type in config.all_template_types[currency_from]['allowed_pairs']])
    return m


def allow_partial_exchange():
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Да', callback_data='partial-exchange_1'),
          InlineKeyboardButton('Нет', callback_data='partial-exchange_0'))
    return m


def select_template_from(templates, t_type):
    m = InlineKeyboardMarkup()
    for temp in templates:
        tid, name = temp
        m.row(InlineKeyboardButton(name, callback_data='new-order-template_{}'.format(tid)))
    m.row(InlineKeyboardButton('Создать новый', callback_data='new-order-another-temp_{}'.format(t_type)))
    return m


def select_template_to(templates, t_type):
    m = InlineKeyboardMarkup()
    if len(templates) > 1:
        m.row(InlineKeyboardButton('Выбрать все', callback_data='select-all-templates'))
    for temp in templates:
        tid, name = temp
        m.row(InlineKeyboardButton(name, callback_data='new-order-template_{}'.format(tid)))
    m.row(InlineKeyboardButton('Создать новый', callback_data='new-order-another-temp_{}'.format(t_type)))
    return m


def cancel_new_order(order_id, cancel=False):
    m = InlineKeyboardMarkup()
    if cancel:
        m.row(InlineKeyboardButton('Отменить', callback_data=f'cancel-new-order-a_{order_id}'),
              InlineKeyboardButton('назад', callback_data=f'cancel-new-order-d_{order_id}'))
    else:
        m.row(InlineKeyboardButton('Отменить заявку', callback_data=f'cancel-new-order_{order_id}'))
    return m


def edit_new_order(order_id, cancel=False):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Редактировать', callback_data=f'edit-new-order_{order_id}'))
    if cancel:
        m.row(InlineKeyboardButton('Отменить', callback_data=f'cancel-new-order-a_{order_id}'),
              InlineKeyboardButton('назад', callback_data=f'cancel-new-edit-order-d_{order_id}'))
    else:
        m.row(InlineKeyboardButton('Отменить заявку', callback_data=f'cancel-new-edit-order_{order_id}'))
    return m


def edit_what_new_order(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Изменить сумму', callback_data=f'new-order-edit-amount_{order_id}'))
    m.row(InlineKeyboardButton('Изменить курс', callback_data=f'new-order-edit-exchange-rate_{order_id}'))
    m.row(InlineKeyboardButton('назад', callback_data=f'back-to-edit-new-order_{order_id}'))
    return m


def approve_new_order(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Одобрить', callback_data='new-order-approve_{}'.format(order_id)),
          InlineKeyboardButton('Отклонить', callback_data='new-order-decline_{}'.format(order_id)))
    return m


def find_order_currency_from(currencies):
    m = InlineKeyboardMarkup(row_width=2)
    m.add(*[InlineKeyboardButton(f'{cur}({cur_count})', callback_data=f'select-currency-from_{cur}')
            for cur, cur_count in currencies.items()])
    return m


def find_order_currency_to(currencies, currency_from):
    m = InlineKeyboardMarkup(row_width=2)
    m.add(*[InlineKeyboardButton(f'{cur}({cur_count})', callback_data=f'select-currency-to_{cur}_{currency_from}')
            for cur, cur_count in currencies.items()])
    return m


def find_orders_markup(orders):
    m = InlineKeyboardMarkup()
    for order in orders:
        order_id = order.get('id')
        m.row(InlineKeyboardButton(utils.get_find_order_button_text(order),
                                   callback_data='show-order-data_{}'.format(order_id)))
    return m


def select_t_to_buy_order(order_id, templates):
    m = InlineKeyboardMarkup()
    for temp in templates:
        t_id, name = temp
        m.row(InlineKeyboardButton(name, callback_data=f'buy-order-template-to_{t_id}_{order_id}'))
    m.row(InlineKeyboardButton('➕ Добавить шаблон', callback_data=f'buy-order-new-template-to_{order_id}'))
    m.row(InlineKeyboardButton('🔙 к заявке', callback_data=f'back-to-order-info_{order_id}'))
    return m


def select_t_from_buy_order(order_id, t_to, templates):
    m = InlineKeyboardMarkup()
    for temp in templates:
        t_id, name = temp
        m.row(InlineKeyboardButton(name, callback_data=f'buy-order-template-from_{t_id}_{t_to}_{order_id}'))
    m.row(InlineKeyboardButton('➕ Добавить шаблон', callback_data=f'buy-order-new-template-from_{t_to}_{order_id}'))
    m.row(InlineKeyboardButton('🔙 к заявке', callback_data=f'back-to-order-info_{order_id}'))
    return m


def select_t_to_buy_order_partial(order_id, templates):
    m = InlineKeyboardMarkup()
    for temp in templates:
        t_id, name = temp
        m.row(InlineKeyboardButton(name, callback_data=f'buy-order-p-template-to_{t_id}_{order_id}'))
    m.row(InlineKeyboardButton('➕ Добавить шаблон', callback_data=f'buy-order-p-new-template-to_{order_id}'))
    m.row(InlineKeyboardButton('🔙 к заявке', callback_data=f'back-to-order-info_{order_id}'))
    return m


def select_t_from_buy_order_partial(order_id, t_to, templates):
    m = InlineKeyboardMarkup()
    for temp in templates:
        t_id, name = temp
        m.row(InlineKeyboardButton(name,
                                   callback_data=f'buy-order-p-template-from_{t_id}_{t_to}_{order_id}'))
    m.row(InlineKeyboardButton('➕ Добавить шаблон',
                               callback_data=f'buy-order-p-new-template-from_{t_to}_{order_id}'))
    m.row(InlineKeyboardButton('🔙 к заявке', callback_data=f'back-to-order-info_{order_id}'))
    return m


def partial_approve(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Подтвердить', callback_data=f'partial-approve-accept_{order_id}'),
          InlineKeyboardButton('Отклонить', callback_data=f'partial-approve-decline_{order_id}'))
    return m


def cancel_buy_order(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Отменить заявку', callback_data=f'cancel-this-buy-order_{order_id}'))
    return m


def cancel_buy_order_approve(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Отменить', callback_data=f'cancel-this-buy-order-a_{order_id}'),
          InlineKeyboardButton('назад', callback_data=f'cancel-this-buy-order-d_{order_id}'))
    return m


def first_pay(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Первел', callback_data=f'first-pay-done_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 15 минут', callback_data=f'first-pay-delay_15-min_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 30 минут', callback_data=f'first-pay-delay_30-min_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 1 час', callback_data=f'first-pay-delay_1-hour_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 3 часа', callback_data=f'first-pay-delay_3-hour_{order_id}'))
    m.row(InlineKeyboardButton('Отменить заявку', callback_data=f'cancel-this-buy-order_{order_id}'))
    return m


def admin_first_pay_approve(order_id, approve=False):
    m = InlineKeyboardMarkup()
    if not approve:
        m.row(InlineKeyboardButton('Подтвердить получение', callback_data=f'approve-first-pay_{order_id}'))
    else:
        m.row(InlineKeyboardButton('Подтвердить', callback_data=f'approve-first-pay-a_{order_id}'),
              InlineKeyboardButton('назад', callback_data=f'approve-first-pay-d_{order_id}'))
    return m


def second_pay(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Первел', callback_data=f'second-pay-done_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 15 минут', callback_data=f'second-pay-delay_15-min_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 30 минут', callback_data=f'second-pay-delay_30-min_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 1 час', callback_data=f'second-pay-delay_1-hour_{order_id}'))
    m.row(InlineKeyboardButton('Переведу через 3 часа', callback_data=f'second-pay-delay_3-hour_{order_id}'))
    m.row(InlineKeyboardButton('Отменить заявку', callback_data=f'cancel-this-buy-order_{order_id}'))
    return m


def second_pay_approve(order_id, approve=False):
    m = InlineKeyboardMarkup()
    if not approve:
        m.row(InlineKeyboardButton('Подтвердить получение', callback_data=f'approve-second-pay_{order_id}'))
    else:
        m.row(InlineKeyboardButton('Подтвердить', callback_data=f'approve-second-pay-a_{order_id}'),
              InlineKeyboardButton('назад', callback_data=f'approve-second-pay-d_{order_id}'))
    m.row(InlineKeyboardButton('Получил не все', callback_data=f'not-enough-second-pay_{order_id}'))
    return m


def admin_buy_order_done(order_id):
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Заявка завершена', callback_data=f'set-order-done_{order_id}'))
    return m


def user_orders_markup(orders):
    m = InlineKeyboardMarkup()
    for order in orders:
        order_id = order.get('id')
        m.row(InlineKeyboardButton(utils.get_owner_orders_button_text(order),
                                   callback_data=f'show-my-order_{order_id}'))
    return m


def personal_cab():
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('Редактировать', callback_data='edit-personal-data'))
    m.row(InlineKeyboardButton('Реферальная система', callback_data='show-referral-sys'))
    return m


def edit_personal_data():
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton('🖌 ФИО', callback_data='edit-data_fio'),
          InlineKeyboardButton('🖌 Номер телефона', callback_data='edit-data_phone'))
    m.row(InlineKeyboardButton('🖌 E-mail', callback_data='edit-data_email'),
          InlineKeyboardButton('🖌 Часовой пояс', callback_data='edit-data_timezone'))
    m.row(InlineKeyboardButton('🔙 назад', callback_data='back-to-personal-cab'))
    return m


def referral_sys():
    m = InlineKeyboardMarkup()
    # m.row(InlineKeyboardButton('Запросить вывод', callback_data='make-referral-withdraw-request'))
    m.row(InlineKeyboardButton('🔙 назад', callback_data='back-to-personal-cab'))
    return m
