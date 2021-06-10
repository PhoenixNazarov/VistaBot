import screens


class My_card:
    def __init__(self):
        self.currency = ''
        self.name = ''

    # def set_currency(self, currency):
    #     self.currency =
    #     if currency == 'v_eur':

    def to_json(self):
        return {
            'currency': self.currency,
            'name': self.name,
        }


class Card_Vista(My_card):
    def __init__(self):
        super().__init__()
        self.number = ''
        self.phone = ''



    def to_json(self):
        _dict = super().to_json()
        _dict.update({
            'number': self.number,
            'phone': self.phone
        })
        return _dict


class Card(My_card):
    def __init__(self):
        super().__init__()
        self.number = ''
        self.bank = ''
        self.card_type = ''
        self.fio = ''

    def format_number(self, number):
        if len(number) == 16 and number.isdigit():
            return True
        return False

    def to_json(self):
        _dict = super().to_json()
        _dict.update({
            'number': self.number,
            'bank': self.bank,
            'card_type': self.card_type,
            'fio': self.fio
        })
        return _dict


class Bank_account(My_card):
    def __init__(self):
        super().__init__()
        self.number = ''
        self.bank = ''
        self.card_type = ''
        self.fio = ''

    def format_number(self, number):
        if len(number) == 20 and number.isdigit():
            return True
        return False

    def to_json(self):
        _dict = super().to_json()
        _dict.update({
            'number': self.number,
            'bank': self.bank,
            'card_type': self.card_type,
            'fio': self.fio
        })
        return _dict


class PayPal(My_card):
    def __init__(self):
        super().__init__()
        self.mail = ''

    def format_number(self, number):
        if len(number) == 20 and number.isdigit():
            return True
        return False

    def to_json(self):
        _dict = super().to_json()
        _dict.update({
            'mail': self.mail,
        })
        return _dict


class Byn(Card):
    def __init__(self):
        super().__init__()
        self.number = ''
        self.bank = ''
        self.card_type = ''
        self.fio = ''
        self.date = ''

    def to_json(self):
        _dict = super().to_json()
        _dict.update({
            'number': self.number,
            'bank': self.bank,
            'card_type': self.card_type,
            'fio': self.fio,
            'date': self.date
        })
        return _dict

            
            
            
        