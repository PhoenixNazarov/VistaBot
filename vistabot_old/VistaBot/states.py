from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):
    fio = State()
    phone = State()
    email = State()
    timezone = State()


class Admin(StatesGroup):
    main = State()

    get_new_commission = State()

    get_user_to_minus_ref_income = State()
    get_value_to_minus_ref_income = State()


class User(StatesGroup):
    main = State()

    get_partial_amount = State()
    edit_fio = State()
    edit_phone = State()
    edit_email = State()
    edit_timezone = State()

    edit_new_order_amount = State()
    edit_new_order_exchange_rate = State()


class NewOrder(StatesGroup):
    change_amount = State()
    currency_to = State()
    exchange_rate = State()
    partial_exchange = State()
    template_from = State()
    template_to = State()


class NewAdminTemplate(StatesGroup):
    class VistaEUR(StatesGroup):
        acc_number = State()
        phone_number = State()

    class VistaUSD(StatesGroup):
        acc_number = State()
        phone_number = State()

    class THB(StatesGroup):
        bank = State()
        acc_number = State()
        holder_name = State()


class NewTemplate(StatesGroup):
    name = State()

    class VistaEUR(StatesGroup):
        acc_number = State()
        phone_number = State()

    class VistaUSD(StatesGroup):
        acc_number = State()
        phone_number = State()

    class RUB(StatesGroup):
        bank = State()
        region = State()
        card_type = State()
        holder_name = State()
        card_number = State()

    class BYN(StatesGroup):
        bank = State()
        region = State()
        card_type = State()
        holder_name = State()
        card_number = State()

    class THB(StatesGroup):
        bank = State()
        acc_number = State()
        holder_name = State()
