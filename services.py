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
card_type = ['VISA', 'MASTER CARD', 'MAESTRO', 'МИР']

http_bot = 't.me/Test_for_phoenix_bot?start='


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