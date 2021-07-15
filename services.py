whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace
printable += 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
printable += 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

russian = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
russian += 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

time_zones = [
    'МСК',
    'МСК+1',
    'МСК+2',
    'МСК+3',
    'МСК+4',
    'МСК+5',
    'МСК+6',
    'МСК+7',
    'МСК+8',
]

popular_russian_bank = ['Сбербанк', 'Альфа-банк', 'ВТБ', 'Тинькоф']
popular_belarus_bank = ['Приорбанк', 'Белагропромбанк', 'Беларусьбанк', 'Бел ВЭБ']
all_banks = popular_russian_bank+popular_belarus_bank+['PayPal']
card_type = ['VISA', 'MASTER CARD', 'MAESTRO', 'МИР']

http_bot = 't.me/Bank_Vista_bot?start='

signs = {
    'usd': '$',
    'eur': '€',
    'rub': '₽',
    'byn': 'Br'
}

referral_bonus = 0.1
referral_withdrawal_usd = 5
referral_withdrawal_eur = 5


def check_email(mail):
    if '@' not in mail:
        return False

    if len(mail.split('@')) != 2:
        return False

    name, name_service = mail.split('@')
    # or name_service not in mails
    if len(name) < 3:
        return False

    return True


def check_phone(phone):
    phone = phone.replace('+', '')
    if 5 < len(phone) < 15 and phone.isdigit():
        return True
    return False


def check_fio(fio):
    for i in fio:
        if i not in russian + '. ':
            return False
    return True


def check_card_name(name):
    if len(name) > 20:
        return False
    return True


def check_vista_account(number):
    numbers = number.split('-')

    if len(numbers) != 4 and number != '23':
        return False

    if numbers[0] == 'VST' and numbers[1].isdigit() and numbers[2].isdigit() and numbers[3].isdigit():
        return True
    return False


def check_card_number(number):
    if len(number) == 16 and number.isdigit():
        return True
    return False


def check_account_number(number):
    if len(number) == 20 and number.isdigit():
        return True
    return False


def check_bik(number):
    if len(number) == 9 and number.isdigit():
        return True
    return False


def check_date_end(date):
    if len(date) == 5 and date[2] == '/':
        numbers = date.split('/')
        if len(numbers) == 2:
            if numbers[0].isdigit() and numbers[1].isdigit():
                return True
    return False


def find_vst_fiat(f_cur, s_cur):
    vst_cur = ''
    fiat_cur = ''

    if 'vusd' in [f_cur, s_cur]:
        vst_cur = 'usd'
    if 'veur' in [f_cur, s_cur]:
        vst_cur = 'eur'

    if 'rub' in [f_cur, s_cur]:
        fiat_cur = 'rub'
    if 'usd' in [f_cur, s_cur]:
        fiat_cur = 'usd'
    if 'byn' in [f_cur, s_cur]:
        fiat_cur = 'byn'
    if 'eur' in [f_cur, s_cur]:
        fiat_cur = 'eur'

    return vst_cur, fiat_cur


def collect_card1(c_list, type = None):
    c_type = c_list[0]
    card_info = [['Название', c_list[1]]]

    if c_type == 've':
        card_info.append(['Валюта', 'Vista EUR'])
        card_info.append(['Номер счет', c_list[3]])
        card_info.append(['Номер телефона', c_list[4]])

    elif c_type == 'vu':
        card_info.append(['Валюта', 'Vista USD'])
        card_info.append(['Номер счет', c_list[3]])
        card_info.append(['Номер телефона', c_list[4]])

    elif c_type == 'c':
        card_info.append(['Валюта', c_list[2]])
        card_info.append(['Тип', 'Карта'])
        card_info.append(['Банк', c_list[3]])
        card_info.append(['Тип карты', c_list[4]])
        card_info.append(['Номер карты', c_list[5]])
        card_info.append(['ФИО', c_list[6]])

    elif c_type == 'a':
        card_info.append(['Валюта', c_list[2]])
        card_info.append(['Тип', 'Счет'])
        card_info.append(['Банк', c_list[3]])
        card_info.append(['БИК', c_list[4]])
        card_info.append(['Номер счета', c_list[5]])
        card_info.append(['ФИО', c_list[6]])

    elif c_type == 'p':
        card_info.append(['Валюта', c_list[2]])
        card_info.append(['Тип', 'PayPal'])
        card_info.append(['Mail', c_list[3]])

    else:
        card_info.append(['Валюта', c_list[2]])
        card_info.append(['Банк', c_list[3]])
        card_info.append(['Тип карты', c_list[4]])
        card_info.append(['ФИО', c_list[5]])
        card_info.append(['Дата действия', c_list[6]])

    card = ''
    for i in card_info:
        card += f'{i[0]}: {i[1]}'
        if type == 'web':
            card += '<br>'
        else:
            card += '\n'

    return card

