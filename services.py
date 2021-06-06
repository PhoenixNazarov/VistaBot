mails = ['box.az', 'byke.com', 'chez.com', 'email.ru', 'gmail.com', 'gmx.net/mail/', 'goldmail.ru', 'inet.ua',
         'loveemail.com', 'bigmailbox.com', 'bigmir.net', 'mail.com', 'mail.e1.ru', 'mail.gala.net', 'lycos.com',
         'rambler.ru', 'mail.ru', 'tut.by', 'yahoo.com', 'yandex.ru', 'netaddress.com', 'newmail.net', 'nicknames.com',
         'outlook.live.com', 'post.cz', 'spam.lv', 'techemail.com', 'ua.fm', 'webmail.aol.com']

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

def check_email(mail):
    if '@' not in mail:
        return False

    if len(mail.split('@')) != 2:
        return False

    name, name_service = mail.split('@')

    if len(name) < 3 or name_service not in mails:
        return False

    return True


def check_phone(phone):
    phone = phone.replace('+', '')
    if 5 < len(phone) < 15 and phone.isdigit():
        return True
    return False


def check_fio(fio):
    for i in fio:
        if i not in russian+'. ':
            return False
    return True
